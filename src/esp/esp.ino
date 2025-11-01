//Libraries for LoRa
#include "functions.h"

uint8_t deviceID = 1; //NOTE This should eventually be stored on the EEPROM

uint8_t lastDeviceMode = IDLE_MODE;
uint32_t nextCADTime = 0;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

uint32_t epochAtBoot = 0; //TODO this should be set and required to be set at boot

//State tracking variables
bool receiveReady = false;
bool messageDispatched = false;
bool ackDispatched = false;

//LoRa RX Related Variables
CyclicArrayList<LORA_RX_BUFFER_SIZE> rxBuffer; //buffer used to store raw data received from LoRa. This is then processed later 
SimpleArraySet<256, 10> rxMessageArray; //used to store information about successfully processed received messages
DefraggingBuffer<2048, 8> rxMessageBuffer; //used to combine received segmented messages into the final full message

//LoRa TX Related Variables
SimpleArraySet<256, 9> txMessageArray; //buffer used to store information about individual packets that should be dispatched
DefraggingBuffer<2048, 8> txMessageBuffer; //used to store the raw data that should be dispatched
CyclicArrayList<LORA_READY_TO_SEND_BUFFER_SIZE> readyToSendBuffer; //Queue for LoRa device. This just contains a length and an address into the txMessageBuffer
CyclicArrayList<LORA_ACK_BUFFER_SIZE> ackToSendBuffer; //Queue for Acks for the LoRa device. This contains raw ACK messages since they are relatively small

//Serial TX Related Variables
//TODO for sake of performance, this should probably be a CyclicArrayList
SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4> serialReadyToSendArray; //Queue for sending data out to serial 

void setup() {
  //initialize variables
  rxBuffer = CyclicArrayList<LORA_RX_BUFFER_SIZE>();
  rxMessageArray = SimpleArraySet<256, 10>();
  rxMessageBuffer = DefraggingBuffer<2048, 8>();
  rxMessageBuffer.init();
  txMessageArray = SimpleArraySet<256, 9>();
  txMessageBuffer = DefraggingBuffer<2048, 8>();
  txMessageBuffer.init();
  readyToSendBuffer = CyclicArrayList<LORA_READY_TO_SEND_BUFFER_SIZE>();
  ackToSendBuffer = CyclicArrayList<LORA_ACK_BUFFER_SIZE>();
  serialReadyToSendArray = SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4>();

  //Initialize Serial Connection to Computer
  Serial.begin(9600);

  //Initialize OLED Screen
  delay(1000);
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false)) { 
    Serial.println(F("SSD1306 allocation failed"));
    while(1); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);

  //Initialize LoRa
  SPI.begin(SCK_LORA, MISO_LORA, MOSI_LORA, SS_LORA);
  LoRa.setPins(SS_LORA, RST_LORA, DIO0_LORA);
  if (!LoRa.begin(BAND)) {
    Serial.println("Starting LoRa failed!");
    display.clearDisplay();
    display.print("Failed to init LoRa");
    display.display();
    while (1);
  }

  //Register Callbacks
  LoRa.onTxDone(onTxDone);
  LoRa.onCadDone(onCadDone);
  LoRa.onReceive(onReceive);

  //Set idle mode
  Debug(Serial.println("Setup Finished"));
  enterReceiveMode();
  display.clearDisplay();
  display.printf("Device ID: %d\n", deviceID);
  display.display();
}

void loop() {
  static uint8_t tempDeviceMode = 255; //debug variable used to print changes in device mode
  static bool shouldScanRxBuffer = false; //flag that gets set when the rxBuffer should be scanned through (ie. when data is added)

  //Debug: If a device mode change was detected log it to serial if we are in debug mode
  if (lastDeviceMode != tempDeviceMode) {
    Debug(Serial.printf("Device Mode change detected! New device mode is %d\n", lastDeviceMode));
    tempDeviceMode = lastDeviceMode;
  }

  //Debug: if we are in unit test mode, run the unit tests and then halt
  if (RUN_UNIT_TESTS) {
    runTests();
    HALT();
  }

  //----------------------------------------------------- MISC State Behavior -------------------------------------------------
  if (lastDeviceMode == CAD_FAILED) { //if CAD detected a signal, then just go back to RX mode until CAD is ready to try again
    LoRa.receive();
    lastDeviceMode = RX_MODE;
    LError("CAD detected a signal! trying again later");
  }

  //------------------------------------------------------RX Interrupt flag handling ------------------------------------------------
  if (receiveReady) { //receiveReady indicates the LoRa has read data, and data is now available. This flag gets set by the RX interrupt
    LDebug("Handling receive flag");
    int size = LoRa.available();
    receiveReady = false;
    
    //Dump the data into a temporary buffer
    uint8_t tempBuf[256];
    LoRa.readBytes(tempBuf, min(256, size));

    //If there is still data in the buffer, then something isn't right
    //because the max LoRa message size is 256 bytes
    if (LoRa.available()) {
      LError("Received more than 256 bytes in LoRa buffer, which was unexpected!");
      HALT();
    }

    //try to add data the received data to our rxBuffer for later processing
    if (rxBuffer.pushBack(tempBuf, size)) {
      LDebug("Added data to LoRa rx buffer");
      Debug(Serial.printf("First Byte of Data: %d\n", tempBuf[0]));
      Debug(Serial.printf("Second Byte of Data: %d\n", tempBuf[1]));
      //Data was successfully added, so set the shouldScanRxBuffer condition
      shouldScanRxBuffer = true;
    } else {
      LWarn("Rx Buffer is currently full, not adding data");
    }

    //NOTE - After the rx is completed, what mode is the lora in? We assume it remains in RX mode for now, so no mode change is necessary
  }

  // -------------------------------------------------- Receive Loop Behavior ---------------------------------------------
  if (shouldScanRxBuffer) { //this gets set to true when data gets added to rxBuffer, or if theres still potentially a message in rxBuffer after a scan
    LDebug("Scanning RX Buffer");
    shouldScanRxBuffer = false;
    uint16_t startIndex = 65535;
    //First, detect the first start byte
    for (int i = 0; i < rxBuffer.size(); i++) {
      if (rxBuffer[i] == START_BYTE) {
        startIndex = i;
        break;
      }
    }
    if (startIndex != 65535) {
      LDebug("Start Index Found");
      //Where the start index was found, the preceding data is malformed/garbage, so it can be dropped
      rxBuffer.dropFront(startIndex);
      startIndex = 0;

      bool messageFound = false;
      
      //TODO we should add some optimization here so that, when new data comes in and we are still scanning off the same start byte, we should automatically start scanning at the point
      //of the new data since we know the old data doesn't contain a message
      //This problem is most prevalent when an invalid message with a valid end byte is in the buffer and the buffer is under 256 bytes.
      //Every time new data gets added to the buffer, the message will attempt to be processed again 
      
      //iterate over the rxBuffer until we reach its end, or we reach the max size of a LoRa message (256 bytes)
      for (int i = 1; i < min((int)rxBuffer.size(), 256); i++) {
        if (rxBuffer[i] == END_BYTE) { //if we find the end byte... i+1 is now the total message length
          LDebug("Found End Byte in rxBuffer");
          LDebug("Message Identified...");
          Debug(dumpArrayToSerial(&(rxBuffer[0]), i+1));

          //First, Calculate the CRC and check if its correct 
          uint32_t crc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(rxBuffer[1])), i - 3))^0xffffffff;
          uint16_t msgCrc = (rxBuffer[i-2] << 8) + rxBuffer[i-1]; 
          if ((crc & 0xFFFF) != msgCrc) {
            LDebug("Received RX message does not have matching CRC, skipping");
            continue;
          } 

          //Since CRC passed, its time to decrypt the message, so lets decrypt it into a temp buffer
          uint8_t tempBuf[256];
          size_t plaintextLen;
          if (!decryptD2DMessage(&(rxBuffer[2]), i - 4, &(tempBuf[0]), 256, &plaintextLen)) {
            LDebug("Decryption Failed, assuming message has been tampered with since CRC still passed");
            //TODO tamper detection OR different key detection
            continue;
          }

          //Verify the plaintextLen is what is expected
          if (plaintextLen != (i+1) - 5 - AES_GCM_OVERHEAD) {
            LError("Received plaintext message from rx is unexpected size!");
            HALT();
          }

          //Now, the message should be fully contained in tempBuf with length plainTextLen, which excludes the start/stop bytes, the encryption overhead, and the CRC

          //check if its a data packet or ack packet
          if (rxBuffer[1] != 0 && rxBuffer[1] != 1) {
            LDebug("Received RX message does have proper type byte, skipping");
            continue;
          }

          //check if the receiver is correct
          if (tempBuf[1] != deviceID) {
            LDebug("Received RX message is not intended for sender, skipping");
            continue;
          }

          //check if the message was intended to be sent in the last 20 seconds based on the timestamp
          //Dirty hack since the timestamp is at different placements in each buffer
          const uint32_t timestamp = (tempBuf[5 + (1 - rxBuffer[1])] << 24) + (tempBuf[6 + (1 - rxBuffer[1])] << 16) + (tempBuf[7 + (1 - rxBuffer[1])] << 8) + tempBuf[8 + (1 - rxBuffer[1])];
          if ((millis() / 1000) + epochAtBoot - timestamp > 20) {
            LWarn("received RX Message is very old, possible replay attack attempt");
            //TODO logic to log replay attack attempt
            continue;
          }
          
          //Now that checks have passed, we can attempt to process the message. First, lets see what type of message it is
          const uint16_t messageNumber = (tempBuf[2] << 8) + tempBuf[3];
          const uint8_t sequenceNumber = tempBuf[4];
          if (sequenceNumber > 7) {
            LError("Incalid sequence number! dropping");
            continue;
          }

          if (rxBuffer[1] == 0) {
            LDebug("Beginning Normal Message Processing");
            //Normal message
            const uint8_t sequenceCount = tempBuf[5];
            const uint8_t sequenceSize = plaintextLen - 10; //subtracting header size

            //check if the message number is already being tracked in rxMessageArray
            uint16_t loc = rxMessageArray.find(messageNumber >> 8, messageNumber & 0xFF);
            if (loc != 65535) { //if the message number is already in the rx message array
              LDebug("Message is already in RX Message Array");
              //message number was found in rxMessageArray already, check if this sequence is needed stil
              const uint8_t sequenceBitmask = rxMessageArray.get(loc)[7];
              if (sequenceBitmask & (1 << sequenceNumber)) { //if this sequence's bit has already been set...
                //message already received, so no need to reprocess
                LDebug("Message sequence was already received, ignoring");
              } else {
                LDebug("Storing sequence in buffer");
                //message not received yet, so mark it in the bitmask and then add the data to the buffer allocation
                rxMessageArray.get(loc)[7] = sequenceBitmask | (1 << sequenceNumber);
                const uint16_t bufferStart = rxMessageArray.get(loc)[2] * 256 + rxMessageArray.get(loc)[3];
                const uint8_t sequenceBaseSize = rxMessageArray.get(loc)[8];
                const uint8_t sequenceCount = rxMessageArray.get(loc)[6];
                if (sequenceSize > sequenceBaseSize) {
                  LError("Received packet with data size bigger than maximum sequence size!");
                  HALT();
                }
                memcpy(&(rxMessageBuffer[bufferStart + sequenceBaseSize * sequenceNumber]), &(tempBuf[10]), sequenceSize);

                //update the rx timeout
                rxMessageArray.get(loc)[9] = (millis() / 1000) % 255;

                //If we are filling the final sequence packet, then change the message size to be accurate 
                if (sequenceNumber == sequenceCount-1) {
                  LDebug("Last sequence message received, updating total rx message buffer size");
                  uint16_t newBufferSize = sequenceBaseSize * sequenceCount - (sequenceBaseSize - sequenceSize);
                  rxMessageArray.get(loc)[4] = newBufferSize >> 8;
                  rxMessageArray.get(loc)[5] = newBufferSize & 0xFF;
                }
                
              }
            } else { //if the received message is not in the rx message array...
              LDebug("Message is not in RX Message Array, adding...");
              //message was not found, so we need to add it
              
              //Unfortunately, if the last packet is received first, its not possible to tell the total size of the data. 
              //For now, we will just drop the packet and wait for an earlier sequence number packet to arrive first
              //UNLESS its just a one packet message. Then we're good.
              if (sequenceNumber != 0 && sequenceNumber == sequenceCount - 1) {
                LWarn("Last message of the sequence was received first! dropping");
                continue; //skip processing and hope an earlier packet number will be seen
              }

              const uint32_t totalSequenceSize = sequenceSize * sequenceCount;

              //try to allocate space in the rx message buffer
              const uint16_t bufferLocation = rxMessageBuffer.malloc(totalSequenceSize);
              if (bufferLocation == 0xFFFF) {
                LError("No space for new message found in rx message buffer, dropping!");
                continue;
              }

              LDebug("Allocated space in buffer for new message");

              //Now that we successfully got an allocation in the rxMessageBuffer, construct a message in the rxMessageArray
              uint8_t headerBuf[10];
              headerBuf[0] = messageNumber >> 8;
              headerBuf[1] = messageNumber & 0xFF;
              headerBuf[2] = bufferLocation >> 8;
              headerBuf[3] = bufferLocation & 0xFF;
              headerBuf[4] = totalSequenceSize >> 8;
              headerBuf[5] = totalSequenceSize & 0xFF;
              headerBuf[6] = sequenceCount;
              headerBuf[7] = 1 << sequenceNumber;
              headerBuf[8] = sequenceSize;
              headerBuf[9] = (millis() / 1000) % 255;

              //try to add the message to the rxMessageArray
              if (rxMessageArray.add(headerBuf)) {
                //Adding message to rx message array succeeded, so copy the data into the rxMessageBuffer
                LDebug("Added new rx message to buffer");
                memcpy(&(rxMessageBuffer[bufferLocation + sequenceSize * sequenceNumber]), &(tempBuf[10]), sequenceSize);
              } else {
                //Adding message to rx message array failed, so release rx message buffer allocation and drop the message
                LError("Failed to add new rx message to array, rxMessageArray is full! Removing allocation in buffer");
                if (!rxMessageBuffer.free(bufferLocation)) {
                  LError("Buffer Free Failed!");
                  HALT();
                }
                continue;
              }

            }

            //Send an ACK. Since the readyToSendBuffer only references data in other buffers, we will have a seperate ACK buffer
            LDebug("Requesting ACK Send: Adding send to ack buffer");
            uint8_t uBuf[9]; //this is the data that will eventually be encrypted
            uBuf[0] = deviceID;
            uBuf[1] = tempBuf[0];
            uBuf[2] = messageNumber >> 8;
            uBuf[3] = messageNumber & 0xFF;
            uBuf[4] = sequenceNumber;
            const uint32_t timestamp = (millis() / 1000) + epochAtBoot;
            uBuf[5] = timestamp >> 24;
            uBuf[6] = (timestamp >> 16) & 0xFF;
            uBuf[7] = (timestamp >> 8) & 0xFF;
            uBuf[8] = timestamp & 0xFF;

            //construct actual message
            uint8_t vBuf[14 + AES_GCM_OVERHEAD];
            vBuf[0] = START_BYTE;
            vBuf[1] = 1;
            size_t ciphertextLen;
            if (!encryptD2DMessage(&(uBuf[0]), 9, &(vBuf[2]), 14 + AES_GCM_OVERHEAD, &ciphertextLen)) {
              LError("Failed to encrypt ACK message");
              HALT();
            }

            //assert the encrypted string is the expected length
            if (ciphertextLen != 9 + AES_GCM_OVERHEAD) {
              LError("Encrypted ACK has unexpected length!");
              HALT();
            }

            //Add CRC and construct rest of ACK
            uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(vBuf[1])), 10 + AES_GCM_OVERHEAD))^0xffffffff; //note - this is one byte longer because it includes the start byte
            vBuf[11 + AES_GCM_OVERHEAD] = (newCrc & 0x0000FF00) >> 8;
            vBuf[12 + AES_GCM_OVERHEAD] = newCrc & 0x000000FF;
            vBuf[13 + AES_GCM_OVERHEAD] = END_BYTE;

            //Push the ACK to the ack buffer
            ackToSendBuffer.pushBack(&(vBuf[0]), 14 + AES_GCM_OVERHEAD);
            
          } else {
            LDebug("Beginning ACK Message Processing");
            //Ack Message - we need to process the ack

            //First, search for the relevant message in the txMessageArray by its message number and sequence number
            //TODO this might have to be a critical section
            for (int i = 0; i < txMessageArray.size(); i++) {
              if ((txMessageArray.get(i)[0] << 8) + txMessageArray.get(i)[1] == messageNumber && txMessageArray.get(i)[2] == sequenceNumber) {
                LDebug("Found Message - Indicated ACK has been received");
                //we found the right message, so indicate the ack has been received
                txMessageArray.get(i)[8] |= 0b10000000;
              }
            }
          }
          
          //If we've gotten this far, then a message was successfully processed, so break out of the loop checking this specific start byte
          messageFound = true;
          break;
        }
      }
      //if we found a message or we've searched over 256 bytes, then the current start byte (at position zero) cannot be associated with any other messages. Thus, we can drop the start byte
      if (messageFound || rxBuffer.size() >= 256) {
        LDebug("A message was found or the buffer is larger than a single message's length, so dropping the current start byte and rescanning");
        rxBuffer.dropFront(1);
        shouldScanRxBuffer = true;
      }
    } else { //Start byte wasn't found at all in the buffer
      LDebug("Start Index Not Found, Clearing Buffer");
      //Clear the buffer
      rxBuffer.clearBuffer();
    }
  }

  //scan through the RX message array and look for any completed messages or any expiring messages
  static uint32_t lastRxProcess = millis();
  if (millis() > lastRxProcess + 500) {
    lastRxProcess = millis();
    for (int i = 0; i < rxMessageArray.size(); i++) {
      //check if a message has received all its parts
      const uint8_t bitmask = rxMessageArray.get(i)[7];
      const uint8_t sequenceCount = rxMessageArray.get(i)[6];
      if (((bitmask + 1) >> sequenceCount) == 1) { //if all parts have been received... NOTE Im not sure if this work will when there are 8 segments. It should but only because of automatic type promotion
        LDebug("Received message has completed"); 
        //Now that we know the message has been fully received, we will drop it from the rxMessageArray, but keep its allocation in the buffer
        //Then we will pass the index of that allocation off to the serial functionality
        uint8_t tempBuf[4];
        tempBuf[0] = rxMessageArray.get(i)[2]; //Buffer Location
        tempBuf[1] = rxMessageArray.get(i)[3];
        tempBuf[2] = rxMessageArray.get(i)[4]; //Size in buffer
        tempBuf[3] = rxMessageArray.get(i)[5];

        serialReadyToSendArray.add(&(tempBuf[0]));

        //now remove it from rxMessageArray
        rxMessageArray.remove(i);
        i--;
      } else

      //check if a message has expired
      if ((diff((millis() / 1000) % 255, rxMessageArray.get(i)[9], 256)) > 10) { //NOTE this 10 second timeout should eventually become a definition
        LLog("Clearing message in RX buffer that has been around for 10 seconds");
        //since it expired, remove its allocation and clear it from the message array
        const uint16_t address = (rxMessageArray.get(i)[2] << 8) + rxMessageArray.get(i)[3]; 
        if (!rxMessageBuffer.free(address)) {
          LError("Failed to free expiring message from rxBuffer");
          HALT();
        }
        if (!rxMessageArray.remove(i)) {
          LError("Failed to remove expiring message from rxMessageArray");
          HALT();
        } 
        i--;
      }
    }
  }

  // -------------------------------------------- Transmit Interrupt Handling ---------------------------------------
  if (lastDeviceMode == CAD_FINISHED) { //if CAD detection finished and didn't detect any other signals
    LDebug("CAD Finished, beginning to send message");
    //We just finished CAD, so send a message
    if (readyToSendBuffer.size() > 0) { //if there is a normal message to send...
      LoRa.beginPacket();
      messageDispatched = true;
      //get information about message to send from readyToSendBuffer
      uint8_t array[3];
      if (!readyToSendBuffer.peakFront(&(array[0]), 3)) {
        LError("Ready to send buffer reported data, but peak front failed!");
        HALT();
      }
      const uint16_t src = (array[0] << 8) + array[1];
      const uint16_t size = array[2];
      LoRa.write(&(txMessageBuffer[src]), size);
      lastDeviceMode = TX_MODE;
      LoRa.endPacket(true);
      LDebug("Finishing writing Normal message to LoRa, dumping message");
      Debug(dumpArrayToSerial(&(txMessageBuffer[src]), size));
    } else if (ackToSendBuffer.size() > 0) { //if there is a ACK message to send...
      LoRa.beginPacket();
      ackDispatched = true;
      uint8_t array[14 + AES_GCM_OVERHEAD];
      if (!ackToSendBuffer.peakFront(&(array[0]), 14 + AES_GCM_OVERHEAD)) {
        LError("Ack buffer reported data, but peak front failed!");
        HALT();
      }
      LoRa.write(&(array[0]), 14 + AES_GCM_OVERHEAD);
      lastDeviceMode = TX_MODE;
      LoRa.endPacket(true);
      LDebug("Finished writing Ack message to LoRa");
    } else {
      LError("Cad Finished with no data in either buffer!");
    }
    
  }

  // -------------------------------------------- Transmit Loop Behavior ---------------------------------------------
  if (messageDispatched) { //if we sent a TX messsage clean it out of the buffer
    LDebug("Clearing sent normal message out of TX buffer");
    messageDispatched = false;
    readyToSendBuffer.dropFront(3);
  } else if (ackDispatched) {
    LDebug("Clearing sent ACK message out of TX buffer");
    ackDispatched = false;
    ackToSendBuffer.dropFront(14 + AES_GCM_OVERHEAD);
  }

  static uint32_t lastTxProcess = millis(); //NOTE at some point, this should be made into a looping variable. It will overflow in about 1.5 months
  if (millis() > lastTxProcess + 500) {
    lastTxProcess = millis();
    //LDebug("attempting to process messagess in tx message array");
    //for each message in the tx Array...
    for (int i = 0; i < txMessageArray.size(); i++) {
      const uint8_t sendCount = txMessageArray.get(i)[8] & 0b01111111;
      const bool ack = txMessageArray.get(i)[8] & 0b10000000;
      const uint16_t location = (txMessageArray.get(i)[3] << 8) + txMessageArray.get(i)[4];

      //If the ack bit is set, drop the message
      if (ack) {
        LDebug("Ack detected for current tx message, dropping from buffer");
        if(!txMessageBuffer.free(location)) {
          LError("Failed to free allocation in txMessageBuffer");
          HALT();
        }
        if (!txMessageArray.remove(i--)) {
          LError("Failed to remove message from txMessageArray");
          HALT();
        }
        continue;
      }

      //If we've reached the max number of send attempts, drop the data all together
      if (sendCount > LORA_SEND_COUNT_MAX) {
        LDebug("Message has reached max send attempts, dropping from buffer");
        if(!txMessageBuffer.free(location)) {
          LError("Failed to free allocation in txMessageBuffer");
          HALT();
        }
        if (!txMessageArray.remove(i--)) {
          LError("Failed to remove message from txMessageArray");
          HALT();
        }
        continue;
      }

      //If it has been over a second since the previous send, try again //NOTE this 4s resent delay should probably be made shorter and controllable via a constant
      uint16_t lastSendTime = (txMessageArray.get(i)[6] << 8) + txMessageArray.get(i)[7];
      if ((diff(millis() % 65536, lastSendTime, 65536)) > 4000) {
        LDebug("Message being processed has reached send time again");
        Debug(dumpArrayToSerial(&(txMessageArray.get(i)[0]), 9));
        LDebug("adding a message to the readytosend buffer");
        Debug(Serial.printf("Diff = %d, 1 = %d, 2 = %d\n", diff(millis() % 65536, lastSendTime, 65536), millis() % 65536, lastSendTime));
        lastSendTime = millis() % 65536; //TODO - the time for CAD to occur is not accounted for in the resend functionality, which is a problem
        //To fix this easily, we can maintatin an average CAD send time (maybe average over 10 previous sends) and add that to our resend delay
        txMessageArray.get(i)[6] = lastSendTime >> 8;
        txMessageArray.get(i)[7] = lastSendTime & 0xFF;
        txMessageArray.get(i)[8]++; //increment send count
        //create buffer for dispatching message
        uint8_t tBuf[3];
        tBuf[0] = txMessageArray.get(i)[3]; //location high byte
        tBuf[1] = txMessageArray.get(i)[4]; //location low byte
        tBuf[2] = txMessageArray.get(i)[5]; //size
        if (readyToSendBuffer.pushBack(tBuf, 3)) {
          LDebug("Added message to ready to send buffer");
          Debug(dumpArrayToSerial(&(tBuf[0]), 3));
        } else {
          LError("Failed to add message to ready to send buffer because it was full");
        }
      }
    }
  }
  

  if (readyToSendBuffer.size() > 0 || ackToSendBuffer.size() > 0) {
    //LDebug("One of the TX buffers has data, attempting to enter CAD Mode");
    enterChannelActivityDetectionMode();
  }

  // ------------------------------------------------------------- SERIAL HANDLING ---------------------------------------------------------------

  //NOTE this is temporary code
  //For now, we will just push the code straight to the serial buffer
  if (serialReadyToSendArray.size() > 0) {
    LDebug("Detected messages ready to dump out to serial");
    for (int i = 0; i < serialReadyToSendArray.size(); i++) {
      const uint16_t addr = (serialReadyToSendArray.get(i)[0] << 8) + serialReadyToSendArray.get(i)[1];
      const uint16_t size = (serialReadyToSendArray.get(i)[2] << 8) + serialReadyToSendArray.get(i)[3];
      LDebug("Writing received messge to serial...");
      Debug(Serial.printf("Identified addr is %d, Identified size is %d\n", addr, size));
      Serial.write(&(rxMessageBuffer[addr]), size);
      //after writing to the buffer, free it from the rx buffer
      rxMessageBuffer.free(addr);
    }
    //clear the serialReadyToSendArray
    serialReadyToSendArray.clearAll();
  }

  //TEST CODE
  if (Serial.available()) {
    if (Serial.read() == 'w') {
      delay(10);
      while (Serial.available()) {
        int temp = Serial.read();
      }
      LLog("Enter Message to transmit");
      uint8_t temp[1024];
      while (!Serial.available());
      delay(1000); //wait for the rest of the bytes to come in
      int numBytes = Serial.available() - 1;
      Serial.readBytes(&(temp[0]), numBytes);
      Serial.printf("Wrote %d bytes into Serial\n", numBytes);
      addMessageToTxArray(&(temp[0]), numBytes, 1 - deviceID);
    } 
  }

  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer

  //test code to test sending::

  //
  
}

//This function will take the data in src
bool addMessageToTxArray(uint8_t* src, uint16_t size, uint8_t destinationID) {
  //first, make sure the data isn't too big
  if (size > SEQUENCE_MAX_SIZE * 8) {
    LWarn("Message will not be added to tx array because it is too long");
    return false;
  }
  //NOTE we should probably also check the available space in txMessageBuffer, but that would require writing a defragging function so not now

  uint8_t txMessage[9];
  txMessage[6] = 0;
  txMessage[7] = 0;
  txMessage[8] = 0;

  //Find an unused message number. First we will generate a random number
  //Then we will look through all known message numbers. If there is a collision, we will try again
  //If we somehow fail 10 times, then we will assume something has gone very wrong and HALT
  bool foundNumber = false;
  uint16_t messageNumber;
  uint8_t attemptCount = 0;
  while (!foundNumber) {
    attemptCount++;
    messageNumber = esp_random();
    foundNumber = true;
    
    for (int i = 0; i < txMessageArray.size(); i++) {
      if (messageNumber == (txMessageArray.get(i)[0] << 8) + txMessageArray.get(i)[1]) {
        foundNumber = false;
        break;
      }
    }
    if (!foundNumber) continue;
    for (int i = 0; i < rxMessageArray.size(); i++) {
      if (messageNumber == (rxMessageArray.get(i)[0] << 8) + txMessageArray.get(i)[1]) {
        foundNumber = false;
        break;
      }
    }
    if (attemptCount >= 10) {
      LError("Reached 10 attempts to find a new message number");
      HALT();
    }
  }

  txMessage[0] = messageNumber >> 8;
  txMessage[1] = messageNumber & 0xFF;

  uint8_t messageLength;
  const uint8_t sequenceCount = (size % SEQUENCE_MAX_SIZE) ? 1 + (size / SEQUENCE_MAX_SIZE) : size / SEQUENCE_MAX_SIZE; 
  //now that we have the messageNumber, lets start placing in our messages.
  //iterate overall all sequences we will have to add...
  for (int i = 0; i < sequenceCount; i++) {
    txMessage[2] = i;
    messageLength = min(size - (SEQUENCE_MAX_SIZE * i), SEQUENCE_MAX_SIZE);
    if (messageLength == 0) continue; //occures if size is a multiple of the SEQUENCE_MAX_SIZE
    txMessage[5] = messageLength + 15 + AES_GCM_OVERHEAD;

    //allocate space in txMessageBuffer
    uint16_t addr = txMessageBuffer.malloc(messageLength + 15 + AES_GCM_OVERHEAD);
    if (addr == 0xFFFF) {
      LError("Failed to allocate space in txMessageBuffer");
      return false;
    }

    txMessage[3] = addr >> 8;
    txMessage[4] = addr & 0xFF;

    if (!txMessageArray.add(&(txMessage[0]))) {
      LError("Failed to txMessage Array, deleting allocation in buffer");
      txMessageBuffer.free(addr);
      return false;
    }

    LDebug("Dumped message in tx Array:");
    Debug(dumpArrayToSerial(&(txMessage[0]), 8));

    //now that we successfully added the message information to the array and the buffer, construct the message into the buffer
    txMessageBuffer[addr] = START_BYTE;
    txMessageBuffer[addr+1] = 0;
    
    uint8_t uBuf[256]; 
    //construct the encrypted part of the header into uBuf
    uBuf[0] = deviceID;
    uBuf[1] = destinationID;
    uBuf[2] = messageNumber >> 8;
    uBuf[3] = messageNumber & 0xFF;
    uBuf[4] = i; //current sequence number
    uBuf[5] = sequenceCount;
    uint32_t timestamp = (millis() / 1000) + epochAtBoot; 
    uBuf[6] = timestamp >> 24;
    uBuf[7] = (timestamp >> 16) & 0xFF;
    uBuf[8] = (timestamp >> 8) & 0xFF;
    uBuf[9] = timestamp & 0xFF;
    //add the data to the buffer
    memcpy(&(uBuf[10]), &(src[SEQUENCE_MAX_SIZE * i]), messageLength);

    //now that we have the data in the UBuf, encrypt it to the txMessageBuffer
    size_t ciphertextLen;
    if (!encryptD2DMessage(&(uBuf[0]), 10 + messageLength, &(txMessageBuffer[addr+2]), 256 - 10, &ciphertextLen)) {
      LError("Failed to encrypt message, dropping");
      return false;
    }

    //Verify that the encrypted message is the expected length. If not, then halt because something is very wrong
    if (ciphertextLen != 10 + messageLength + AES_GCM_OVERHEAD) {
      LError("Encrypted TX message is not the size expected!");
      HALT();
    }

    //Calculate CRC on everything above except the start byte
    uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(txMessageBuffer[addr+1])), ciphertextLen+1))^0xffffffff; //note - this is one byte longer because it includes the start byte
    
    //Add calculated CRC and end bye to end of message
    txMessageBuffer[addr+2+ciphertextLen] = newCrc >> 8;
    txMessageBuffer[addr+3+ciphertextLen] = newCrc & 0xFF;
    txMessageBuffer[addr+4+ciphertextLen] = END_BYTE;

    LDebug("Finished writing new data to tx message buffer:");
    Debug(dumpArrayToSerial(&(txMessageBuffer[0]), 10 + messageLength));
  }
  return true;
}

void enterChannelActivityDetectionMode() {
  //NOTE - we don't seem to have a way to check if an message is actively being received. Thus, we may accidentally kick the device out of RX mode while is message is transmitting.
  if (millis() > nextCADTime) {
    if (lastDeviceMode == RX_MODE || lastDeviceMode == IDLE_MODE || lastDeviceMode == SLEEP_MODE) {
      lastDeviceMode = CAD_MODE;
      LLog("Entering Channel Activity Detection Mode");
      LoRa.idle();
      delay(5);
      LoRa.channelActivityDetection(); 
    }
  }
}

void enterReceiveMode() {
  //Under normal flow, if a message is added to the send buffer, the device will go to CAD mode, then to TX mode, and then to IDLE mode. from there, we can reenter rec mode
  if (lastDeviceMode == IDLE_MODE) {
    lastDeviceMode = RX_MODE;
    LLog("Entering Receive Mode");
    LoRa.receive();
  }
}
void onCadDone(bool detectedSignal) {
  //LDebug("Cad Finished");
  if (detectedSignal) {
    nextCADTime = MIN_CAD_WAIT_INTERVAL_MS * ((esp_random() % 10) + 1);
    lastDeviceMode = CAD_FAILED;
  } else {
    lastDeviceMode = CAD_FINISHED;
  }
  return;
}
void onTxDone() {
  lastDeviceMode = RX_MODE;
  LoRa.receive();
  return;
}

void onReceive(int size) {
  receiveReady = true;
}

void Log(LOG_LEVEL level, const char* text) {
  if (level <= CURRENT_LOG_LEVEL) {
    Serial.printf("[%s]: %s\n", logLevelEnumToChar(level), text);
  }
}

void dumpArrayToSerial(const uint8_t* src, const uint16_t size) {
  Serial.printf("Dumping Array to Serial: \n");
  for (int i = 0; i < size; i++) {
    Serial.printf("%d ", src[i]);
  }
  Serial.printf("\n");
}






