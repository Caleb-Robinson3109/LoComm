#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1
#define LORA_READY_TO_SEND_BUFFER_SIZE 1024
#define LORA_ACK_BUFFER_SIZE 256
#define LORA_SEND_COUNT_MAX 8
#define SERIAL_READY_TO_SEND_BUFFER_SIZE 128
#define SEQUENCE_MAX_SIZE 128


#define IDLE_MODE 1
#define RX_MODE 2
#define TX_MODE 3
#define CAD_MODE 4
#define CAD_FINISHED 5
#define CAD_FAILED 6
#define SLEEP_MODE 0

#define LLog(x) Log(LOG_LEVEL_LOG, x)
#define LDebug(x) Log(LOG_LEVEL_DEBUG, x)
#define LWarn(x) Log(LOG_LEVEL_WARNING, x)
#define LError(x) Log(LOG_LEVEL_ERROR, x)
#define HALT() Serial.println("Halting"); while(1)

#define diff(new, old, size) (new >= old) ? new - old : size - old + new

#define START_BYTE 0xc1
#define END_BYTE 0x8c

//Libraries for LoRa
#include <SPI.h>
#include "LoRa.h"
#include "functions.h"

//Libraries for OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <esp_rom_crc.h>

#include "esp.h"


uint8_t deviceID = 0; //NOTE This should eventually be stored on the EEPROM

uint8_t lastDeviceMode = IDLE_MODE;
uint32_t nextCADTime = 0;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

bool receiveReady = false;
bool messageDispatched = false;
bool ackDispatched = false;

CyclicArrayList<LORA_RX_BUFFER_SIZE> rxBuffer;
SimpleArraySet<256, 9> rxMessageArray;
DefraggingBuffer<2048, 8> rxMessageBuffer;

SimpleArraySet<256, 8> txMessageArray;
DefraggingBuffer<2048, 8> txMessageBuffer;

CyclicArrayList<LORA_READY_TO_SEND_BUFFER_SIZE> readyToSendBuffer;
CyclicArrayList<LORA_ACK_BUFFER_SIZE> ackToSendBuffer;

SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4> serialReadyToSendArray; //message addr high, message addr low, message size high, message size low

void setup() {
  //initialize variables
  rxBuffer = CyclicArrayList<LORA_RX_BUFFER_SIZE>();
  rxMessageArray = SimpleArraySet<256, 9>();
  rxMessageBuffer = DefraggingBuffer<2048, 8>();
  rxMessageBuffer.init();

  txMessageArray = SimpleArraySet<256, 8>();
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
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
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
  Serial.println("Setup Finished");
  enterReceiveMode();
  display.clearDisplay();
  display.display();
  display.printf("Device ID: %d\n", deviceID);
  display.display();
}

#define RUN_UNIT_TESTS false

void loop() {
  static uint8_t tempDeviceMode = 255;
  if (lastDeviceMode != tempDeviceMode) {
    Serial.printf("Device Mode change detected! New device mode is %d\n", lastDeviceMode);
    tempDeviceMode = lastDeviceMode;
  }


  //TODO write unit tests for the arrays types
  if (RUN_UNIT_TESTS) {
    LLog("Running Cyclic Array List unit tests:");

    //TODO write these
  }

  static bool shouldScanRxBuffer = false; 

  //----------------------------------------------------- MISC State Behavior -------------------------------------------------
  if (lastDeviceMode == CAD_FAILED) {
    LoRa.receive();
    lastDeviceMode = RX_MODE;
    LError("CAD detected a signal! trying again later");
  }

  //------------------------------------------------------Interrupt flag handling ------------------------------------------------
  if (receiveReady) {
    LDebug("Handling receive flag");
    int size = LoRa.available();
    receiveReady = false;
    
    //Dump the data into a temporary buffer
    uint8_t tempBuf[256];
    LoRa.readBytes(tempBuf, min(256, size));

    //Consider adding a debug check to see if there is still data in the buffer
    if (LoRa.available()) {
      LError("Received more than 256 bytes in LoRa buffer, which was unexpected!");
      HALT();
    }

    //try to add data to the buffer
    if (rxBuffer.pushBack(tempBuf, size)) {
      LDebug("Added data to LoRa rx buffer");
      Serial.printf("First Byte of Data: %d\n", tempBuf[0]);
      Serial.printf("Second Byte of Data: %d\n", tempBuf[1]);
      shouldScanRxBuffer = true;
    } else {
      LWarn("Rx Buffer is currently full, not adding data");
    }

  }

  // -------------------------------------------------- Receive Loop Behavior ---------------------------------------------
  if (shouldScanRxBuffer) {
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
      //clear everything before the first start byte
      rxBuffer.dropFront(startIndex);
      startIndex = 0;

      bool messageFound = false;
      
      //TODO we should add some optimization here so that, when new data comes in and we are still scanning off the same start byte, we should automatically start scanning at the point
      //of the new data since we know the old data doesn't contain a message
      //This problem is most prevalent when an invalid message with a valid end byte is in the buffer and the buffer is under 256 bytes.
      //Every time new data gets added to the buffer, the message will attempt to be processed again 

      for (int i = 1; i < min((int)rxBuffer.size(), startIndex + 256); i++) { //i+1 is now the total message length
        if (rxBuffer[i] == END_BYTE) {
          LDebug("Found End Byte in rxBuffer");
          LDebug("Message Identified...");
          dumpArrayToSerial(&(rxBuffer[0]), i+1);


          uint8_t tempBuf[256];

          //NOTE - eventually, we wil decrypt the message and store it in tempBuf. 
          //For now we will send unencrypted messages, so we will just copy it over and not touch it
          memcpy(tempBuf, &(rxBuffer[1]), sizeof(uint8_t) * (i - 1)); //copy contents, excluding start and stop byte
          //now tempbuf contains just the message, going from 0 to i-2, so it contains i-1 bytes

          //check if its a data packet or ack packet
          if (tempBuf[0] != 0 && tempBuf[0] != 1) {
            LDebug("Received RX message does have proper type byte, skipping");
            continue;
          }

          //check if the receiver is correct
          if (tempBuf[2] != deviceID) {
            LDebug("Received RX message is not intended for sender, skipping");
            continue;
          }

          //Calculate the CRC and check if its correct 
          uint32_t crc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)tempBuf, i - 3))^0xffffffff;
          uint16_t msgCrc = (tempBuf[i-3] << 8) + tempBuf[i-2]; 
          if ((crc & 0xFFFF) != msgCrc) {
            LDebug("Received RX message does not have matching CRC, skipping");
            continue;
          } 

          //Now that checks have passed, we can attempt to process the message. First, lets see what type of message it is
          if (tempBuf[0] == 0) {
            LDebug("Beginning Normal Message Processing");
            //Normal message
            const uint8_t messageNumber = tempBuf[3];

            //check if the message number is already being tracked in rxMessageArray
            uint16_t loc = rxMessageArray.find(messageNumber);
            if (loc != 65535) { 
              LDebug("Message is already in RX Message Array");
              //message number was found in rxMessageArray already, check if this sequence is needed stil
              const uint8_t sequenceNumber = tempBuf[4];
              const uint8_t sequenceBitmask = rxMessageArray.get(loc)[6];
              if (sequenceBitmask & (1 << sequenceNumber)) {
                //message already received, so no need to reprocess
                LDebug("Message sequence was already received, ignoring");
              } else {
                LDebug("Storing sequence in buffer");
                //message not received yet, so mark it in the bitmask and then add the data to the buffer allocation
                rxMessageArray.get(loc)[6] = sequenceBitmask & (1 << sequenceNumber);
                const uint16_t bufferStart = rxMessageArray.get(loc)[1] * 256 + rxMessageArray.get(loc)[2];
                const uint8_t sequenceBaseSize = rxMessageArray.get(loc)[7];
                const uint8_t sequenceSize = i-1 - 8;
                const uint8_t sequenceCount = rxMessageArray.get(loc)[5];
                if (sequenceSize > sequenceBaseSize) {
                  LError("Received packet with data size bigger than maximum sequence size!");
                  HALT();
                }
                memcpy(&(rxMessageBuffer[bufferStart + sequenceBaseSize * sequenceNumber]), &(tempBuf[6]), sequenceSize);

                //update the rx timeout
                rxMessageArray.get(loc)[8] = (millis() / 1000) % 255;

                //fill the rest of the buffer with 0x00 if we are populating the final packet 
                if (sequenceNumber == sequenceCount-1) {
                  LDebug("Last sequence message received, filling the rest of the buffer with zeros");
                  for (int i = sequenceSize; i < sequenceBaseSize; i++) {
                    rxMessageBuffer[bufferStart + sequenceBaseSize * sequenceNumber + i] = 0;
                  } 
                }
                
              }
            } else {
              LDebug("Message is not in RX Message Array, adding...");
              //message was not found, so we need to add it
              const uint8_t sequenceNumber = tempBuf[4];
              const uint8_t sequenceCount = tempBuf[5];
              
              //Unfortunately, if the last packet is received first, its not possible to tell the total size of the data. 
              //For now, we will just drop the packet and wait for an earlier sequence number packet to arrive first
              //UNLESS its just a one packet message. Then we're good.
              if (sequenceNumber != 0 && sequenceNumber == sequenceCount - 1) {
                LWarn("Last message of the sequence was received first! dropping");
                continue; //attempt next packet
              }

              const uint8_t sequenceSize = i - 1 - 8;
              const uint32_t totalSequenceSize = sequenceSize * sequenceCount;

              //try to allocate space in the buffer
              const uint16_t bufferLocation = rxMessageBuffer.malloc(totalSequenceSize);
              if (bufferLocation == 0xFFFF) {
                LError("No space for new message found in rx message buffer, dropping!");
              }

              LDebug("Allocated space in buffer for new message");

              //populate the rxMessageArray
              uint8_t headerBuf[9];
              headerBuf[0] = messageNumber;
              headerBuf[1] = bufferLocation >> 8;
              headerBuf[2] = bufferLocation & 0xFF;
              headerBuf[3] = totalSequenceSize >> 8;
              headerBuf[4] = totalSequenceSize & 0xFF;
              headerBuf[5] = sequenceCount;
              headerBuf[6] = 1 << sequenceNumber;
              headerBuf[7] = sequenceSize;
              headerBuf[8] = (millis() / 1000) % 255;

              if (rxMessageArray.add(headerBuf)) {
                LDebug("Added new rx message to buffer");
                memcpy(&(rxMessageBuffer[bufferLocation + sequenceSize * sequenceNumber]), &(tempBuf[i]), sequenceSize);
              } else {
                LError("Failed to add new rx message to array, rxMessageArray is full! Removing allocation in buffer");
                rxMessageBuffer.free(bufferLocation);
              }

            }

            //Send an ACK. Since the readyToSendBuffer only references data in other buffers, we will have a seperate ACK buffer
            //TODO this message should be encrypted eventually
            LDebug("Requesting ACK Send: Adding send to ack buffer");
            uint8_t vBuf[9];
            vBuf[0] = START_BYTE;
            vBuf[1] = 1;
            vBuf[2] = deviceID;
            const uint8_t sender = tempBuf[1]; 
            vBuf[3] = sender;
            vBuf[4] = messageNumber;
            const uint8_t sequenceNumber = tempBuf[4];
            vBuf[5] = sequenceNumber;
            uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(vBuf[1])), 5))^0xffffffff;
            vBuf[6] = (newCrc & 0x0000FF00) >> 8;
            vBuf[7] = newCrc & 0x000000FF;
            vBuf[8] = END_BYTE;
            ackToSendBuffer.pushBack(&(vBuf[0]), 9);
            
          } else {
            LDebug("Beginning ACK Message Processing");
            //Ack Message - we need to process the ack

            const uint8_t messageNumber = tempBuf[3];
            const uint8_t sequenceNumber = tempBuf[4];

            //First, search for the relevant message in the txMessageArray by its message number and sequence number
            //TODO this might have to be a critical section
            for (int i = 0; i < txMessageArray.size(); i++) {
              if (txMessageArray.get(i)[0] == messageNumber && txMessageArray.get(i)[1] == sequenceNumber) {
                LDebug("Found Message - Indicated ACK has been received");
                //we found the right message, so indicate the ack has been received
                txMessageArray.get(i)[7] |= 0b10000000;
              }
            }
          }

          //now that we've processed the messsage, break out of the loop checking this specific start byte
          messageFound = true;
          break;
        }
      }

      if (messageFound || rxBuffer.size() >= 256) {
        LDebug("A message was found or the buffer is larger than a single message's length, so dropping the current start byte and rescanning");
        rxBuffer.dropFront(1);
        shouldScanRxBuffer = true;
      }
    } else {
      LDebug("Start Index Not Found, Clearing Buffer");
      //Start byte wasn't found at all in the buffer. Clear the buffer
      rxBuffer.clearBuffer();
    }
  }

  //scan through the RX buffer and look for any completed messages or any expiring messages
  static uint32_t lastRxProcess = millis();
  if (millis() > lastRxProcess + 500) {
    for (int i = 0; i < rxMessageArray.size(); i++) {
      //check if a message has received all its parts
      const uint8_t bitmask = rxMessageArray.get(i)[6];
      const uint8_t sequenceCount = rxMessageArray.get(i)[5];
      if (((bitmask + 1) >> sequenceCount) == 1) {
        LDebug("Received message has completed"); 
        //Now that we know the message has been fully received, we will drop it from the rxMessageArray, but keep its allocation in the buffer
        //Then we will pass the index of that allocation off to the serial functionality
        uint8_t tempBuf[4];
        tempBuf[0] = rxMessageArray.get(i)[1];
        tempBuf[1] = rxMessageArray.get(i)[2];
        tempBuf[2] = rxMessageArray.get(i)[3];
        tempBuf[3] = rxMessageArray.get(i)[4];

        serialReadyToSendArray.add(&(tempBuf[0]));

        //now remove it from rxMessageArray
        rxMessageArray.remove(i);
        i--;
      } else

      //check if a message has expired
      if ((diff((millis() / 1000) % 255, rxMessageArray.get(i)[8], 256)) > 10) {
        LLog("Clearing message in RX buffer that has been around for 10 seconds");
        //since it expired, remove its allocation and clear it from the message array
        const uint16_t address = (rxMessageArray.get(i)[1] << 8) + rxMessageArray.get(i)[2]; 
        rxMessageBuffer.free(address);
        rxMessageArray.remove(i); 
        i--;
      }
    }
  }

  // -------------------------------------------- Transmit Interrupt Handling ---------------------------------------
  if (lastDeviceMode == CAD_FINISHED) {
    LDebug("CAD Finished, beginning to send message");
    //We just finished CAD, so send a message
    if (readyToSendBuffer.size() > 0) {
      LoRa.beginPacket();
      messageDispatched = true;
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
      dumpArrayToSerial(&(txMessageBuffer[src]), size);
    } else if (ackToSendBuffer.size() > 0) {
      LoRa.beginPacket();
      ackDispatched = true;
      uint8_t array[9];
      if (!ackToSendBuffer.peakFront(&(array[0]), 9)) {
        LError("Ack buffer reported data, but peak front failed!");
        HALT();
      }
      LoRa.write(&(array[0]), 9);
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
    ackToSendBuffer.dropFront(9);
  }

  static uint32_t lastTxProcess = millis(); //NOTE at some point, this should be made into a looping variable. It will overflow in about 1.5 months
  if (millis() > lastTxProcess + 500) {
    lastTxProcess = millis();
    for (int i = 0; i < txMessageArray.size(); i++) {
      LDebug("Processing message in tx message array");
      const uint8_t sendCount = txMessageArray.get(i)[7] & 0b01111111;
      const bool ack = txMessageArray.get(i)[7] & 0b10000000;
      const uint16_t location = (txMessageArray.get(i)[2] << 8) + txMessageArray.get(i)[3];

      //If the ack bit is set, drop the message
      if (ack) {
        LDebug("Ack detected for current tx message, dropping from buffer");
        txMessageBuffer.free(location);
        txMessageArray.remove(i--);
        continue;
      }

      //If we've reached the max number of send attempts, drop the data all together
      if (sendCount > LORA_SEND_COUNT_MAX) {
        LDebug("Message has reached max send attempts, dropping from buffer");
        txMessageBuffer.free(location);
        txMessageArray.remove(i--); //decrement i so that we still iterate over all remaining entries
        continue;
      }

      //If it has been over a second since the previous send, try again //NOTE this 1s resent delay should probably be made shorter and controllable via a constant
      uint16_t lastSendTime = (txMessageArray.get(i)[5] << 8) + txMessageArray.get(i)[6];
      if ((diff(millis() % 65536, lastSendTime, 65536)) > 4000) {
        LDebug("Message being processed has reached send time again");
        dumpArrayToSerial(&(txMessageArray.get(i)[0]), 8);
        LDebug("adding a message to the readytosend buffer");
        Serial.printf("Diff = %d, 1 = %d, 2 = %d\n", diff(millis() % 65536, lastSendTime, 65536), millis() % 65536, lastSendTime);
        lastSendTime = millis() % 65536; //NOTE - the time for CAD to occur is not accounted for in the resend functionality, which is a problem
        txMessageArray.get(i)[5] = lastSendTime >> 8;
        txMessageArray.get(i)[6] = lastSendTime & 0xFF;
        txMessageArray.get(i)[7]++; //increment send count
        uint8_t tBuf[3];
        tBuf[0] = txMessageArray.get(i)[2]; //location high byte
        tBuf[1] = txMessageArray.get(i)[3]; //location low byte
        tBuf[2] = txMessageArray.get(i)[4]; //size
        if (readyToSendBuffer.pushBack(tBuf, 3)) {
          LDebug("Added message to ready to send buffer");
          dumpArrayToSerial(&(tBuf[0]), 3);
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
      Serial.write(&(rxMessageBuffer[addr]), size);
      //after writing to the buffer, free it from the rx buffer
      rxMessageBuffer.free(addr);
    }
    //clear the serialReadyToSendArray
    serialReadyToSendArray.clearAll();
  }

  //TEST CODE
  if (Serial.available()) {
    if (Serial.read() == 'a') {
      LLog("Writing message to buffer");
      uint8_t temp[40];
      addMessageToTxArray(&(temp[0]), 40);
    } 
  }

  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer

  //test code to test sending::

  //
  
}

//This function will take the data in src
bool addMessageToTxArray(uint8_t* src, uint16_t size) {
  //first, make sure the data isn't too big
  if (size > SEQUENCE_MAX_SIZE * 8) {
    LWarn("Message will not be added to tx array because it is too long");
    return false;
  }
  //NOTE we should probably also check the available space in txMessageBuffer, but that would require writing a defragging function so not now

  uint8_t temp[8];
  temp[5] = 0;
  temp[6] = 0;
  temp[7] = 0;

  //Find an unused message number. First we will generate a random number
  //Then we will look through all known message numbers. If there is a collision, we will try again
  //If we somehow fail 10 times, then we will assume something has gone very wrong and HALT
  bool foundNumber = false;
  uint8_t messageNumber;
  uint8_t attemptCount = 0;
  while (!foundNumber) {
    attemptCount++;
    messageNumber = esp_random();
    foundNumber = true;
    
    for (int i = 0; i < txMessageArray.size(); i++) {
      if (messageNumber == txMessageArray.get(i)[0]) {
        foundNumber = false;
        break;
      }
    }
    if (!foundNumber) continue;
    for (int i = 0; i < rxMessageArray.size(); i++) {
      if (messageNumber == rxMessageArray.get(i)[0]) {
        foundNumber = false;
        break;
      }
    }
    if (attemptCount >= 10) {
      LError("Reached 10 attempts to find a new message number");
      HALT();
    }
  }

  temp[0] = messageNumber;

  uint8_t messageLength;
  const uint8_t sequenceCount = (size % SEQUENCE_MAX_SIZE) ? 1 + (size / SEQUENCE_MAX_SIZE) : size / SEQUENCE_MAX_SIZE; 
  //now that we have the messageNumber, lets start placing in our messages
  for (int i = 0; i <= size / SEQUENCE_MAX_SIZE; i++) {
    temp[1] = i;
    messageLength = min(size - (SEQUENCE_MAX_SIZE * i), SEQUENCE_MAX_SIZE);
    if (messageLength == 0) continue; //occures if size is a multiple of the SEQUENCE_MAX_SIZE
    temp[4] = messageLength + 10;

    //allocate space in txMessageBuffer
    uint16_t addr = txMessageBuffer.malloc(messageLength + 10);
    if (addr == 0xFFFF) {
      LError("Failed to allocate space in txMessageBuffer");
      return false;
    }

    temp[2] = addr >> 8;
    temp[3] = addr & 0xFF;

    if (!txMessageArray.add(&(temp[0]))) {
      LError("Failed to txMessage Array, deleting allocation in buffer");
      txMessageBuffer.free(addr);
      return false;
    }

    LDebug("Dumped message in tx Array:");
    dumpArrayToSerial(&(temp[0]), 8);

    //now that we successfully added the message information to the array and the buffer, construct the message into the buffer
    //TODO when we add encryption, we need to encrypt allthis (excluding start and stop byte)
    txMessageBuffer[addr] = START_BYTE;
    txMessageBuffer[addr+1] = 0;
    txMessageBuffer[addr+2] = deviceID;
    txMessageBuffer[addr+3] = 1 - deviceID; //TODO this is temporary and will only work for bicommunication
    txMessageBuffer[addr+4] = messageNumber;
    txMessageBuffer[addr+5] = i;
    txMessageBuffer[addr+6] = sequenceCount;
    memcpy(&(txMessageBuffer[addr+7]), &(src[SEQUENCE_MAX_SIZE * i]), messageLength);
    uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(txMessageBuffer[addr+1])), messageLength + 6))^0xffffffff;
    txMessageBuffer[addr+7+messageLength] = (newCrc & 0x0000FF00) >> 8;
    txMessageBuffer[addr+7+messageLength+1] = (newCrc & 0x000000FF);
    txMessageBuffer[addr+7+messageLength+2] = END_BYTE;
    LDebug("Finished writing new data to tx message buffer:");
    dumpArrayToSerial(&(txMessageBuffer[0]), 10 + messageLength);

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



