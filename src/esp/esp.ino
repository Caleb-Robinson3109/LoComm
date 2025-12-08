//Libraries for LoRa
#include "functions.h"

#include "globals.h"

//api functions
#include "apiCode.h"
#include "security_protocol.h"

extern Preferences storage;


//uint8_t deviceIDList[32]; 
bool deviceIDDataChanged = false;

uint8_t lastDeviceMode = IDLE_MODE;
uint32_t nextCADTime = 0;
//Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

//uint32_t epochAtBoot = 0; //TODO this should be set and required to be set at boot

//Variables for Device ID resolution and maintenance
bool sendDeviceIDResponse = false;
uint32_t lastDeviceIDResponseTime = 0;
uint8_t deviceIDResponseBuffer[10+AES_GCM_OVERHEAD];
bool sendDeviceIDTableResponse = false;
uint32_t lastDeviceIDTableResponseTime = 0;
uint8_t deviceIDTableResponseBuffer[41+AES_GCM_OVERHEAD];
bool sendDeviceIDRequest = false;
uint32_t lastDeviceIDRequest = 0;
uint8_t deviceIDRequestBuffer[10+AES_GCM_OVERHEAD];
bool sendDeviceIDTableRequest = false;
uint32_t lastDeviceIDTableRequestTime = 0;
uint8_t deviceIDTableRequestBuffer[10+AES_GCM_OVERHEAD];


//State tracking variables
bool receiveReady = false;
bool messageDispatched = false;
bool ackDispatched = false;
bool enableLora = false;
CyclicArrayList<uint16_t, 128> previouslySeenIds;
CyclicArrayList<uint16_t, 128> previouslyProcessedIds;

//LoRa RX Related Variables
CyclicArrayList<uint8_t, LORA_RX_BUFFER_SIZE> rxBuffer; //buffer used to store raw data received from LoRa. This is then processed later
uint16_t rxBufferLastSize = 0;
SimpleArraySet<256, 10> rxMessageArray; //used to store information about successfully processed received messages
DefraggingBuffer<2048, 8> rxMessageBuffer; //used to combine received segmented messages into the final full message

//LoRa TX Related Variables
SimpleArraySet<256, 9> txMessageArray; //buffer used to store information about individual packets that should be dispatched
DefraggingBuffer<2048, 8> txMessageBuffer; //used to store the raw data that should be dispatched
CyclicArrayList<uint8_t, LORA_READY_TO_SEND_BUFFER_SIZE> readyToSendBuffer; //Queue for LoRa device. This just contains a length and an address into the txMessageBuffer
CyclicArrayList<uint8_t, LORA_ACK_BUFFER_SIZE> ackToSendBuffer; //Queue for Acks for the LoRa device. This contains raw ACK messages since they are relatively small

//Serial TX Related Variables
//TODO for sake of performance, this should probably be a CyclicArrayList
//SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4> serialReadyToSendArray; //Queue for sending data out to serial //(location in the rxMessageBuffer, size)

//Since both the lora code and api code may need access to the lora rx and tx buffers, both need locks
portMUX_TYPE loraRxSpinLock = portMUX_INITIALIZER_UNLOCKED;
bool loraRxLock = false;
portMUX_TYPE loraTxSpinLock = portMUX_INITIALIZER_UNLOCKED;
bool loraTxLock = false;
portMUX_TYPE serialLoraBridgeSpinLock = portMUX_INITIALIZER_UNLOCKED;
bool serialLoraBridgeLock = false;

bool receivedDeviceIDTable = false;

StackType_t apiStack[API_CODE_STACK_SIZE];
StaticTask_t apiStackBuffer;

void setup() {
  pinMode(2, OUTPUT);
  blinky1();

  //initialize variables
  rxBuffer = CyclicArrayList<uint8_t, LORA_RX_BUFFER_SIZE>();
  rxMessageArray = SimpleArraySet<256, 10>();
  rxMessageBuffer = DefraggingBuffer<2048, 8>();
  rxMessageBuffer.init();
  txMessageArray = SimpleArraySet<256, 9>();
  txMessageBuffer = DefraggingBuffer<2048, 8>();
  txMessageBuffer.init();
  readyToSendBuffer = CyclicArrayList<uint8_t, LORA_READY_TO_SEND_BUFFER_SIZE>();
  ackToSendBuffer = CyclicArrayList<uint8_t, LORA_ACK_BUFFER_SIZE>();
  serialReadyToSendArray = SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4>();
  previouslySeenIds = CyclicArrayList<uint16_t, 128>();
  previouslyProcessedIds = CyclicArrayList<uint16_t, 128>();

  if (!storage.begin("LoComm", 0)) {
    LError("Failed to start storage instance!");
    HALT();
  }

  //preload address resolution buffers with data that doesnt change
  deviceIDRequestBuffer[0] = START_BYTE;
  deviceIDRequestBuffer[1] = 2;
  deviceIDRequestBuffer[9 + AES_GCM_OVERHEAD] = END_BYTE;
  
  deviceIDResponseBuffer[0] = START_BYTE;
  deviceIDResponseBuffer[1] = 3;
  deviceIDResponseBuffer[9 + AES_GCM_OVERHEAD] = END_BYTE;

  deviceIDTableRequestBuffer[0] = START_BYTE;
  deviceIDTableRequestBuffer[1] = 4;
  deviceIDTableRequestBuffer[9 + AES_GCM_OVERHEAD] = END_BYTE;

  deviceIDTableResponseBuffer[0] = START_BYTE;
  deviceIDTableResponseBuffer[1] = 5;
  deviceIDTableResponseBuffer[40 + AES_GCM_OVERHEAD] = END_BYTE;


  //Initialize Serial Connection to Computer
  Serial.begin(115200);
  Serial1.setPins(26, 25);
  Serial1.begin(115200); //TODO set pins for serial1

  while (!Serial);
  while (!Serial1);

  //Initialize OLED Screen
  delay(1000);
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false)) { 
    Serial1.println(F("SSD1306 allocation failed"));
    while(1); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);

  //Initialize LoRa
  SPI.begin(SCK_LORA, MISO_LORA, MOSI_LORA, SS_LORA);
  LoRa.setPins(SS_LORA, RST_LORA, DIO0_LORA);
  if (!LoRa.begin(BAND)) {
    Serial1.println("Starting LoRa failed!");
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
  Debug(Serial1.println("Setup Finished"));
  enterReceiveMode();
  display.clearDisplay();
  display.printf("Device ID: %d\n", deviceID);
  display.display();

  //init security
  sec_init();
  sec_setInitialPassword("password");

  //initialize api task
  delay(1000);
  Serial.println("Booting");
  Serial.flush();
  
  xTaskCreateStaticPinnedToCore(
    apiCode,
    "APICODE",
    API_CODE_STACK_SIZE,
    (void*) 1,
    0,
    apiStack,
    &apiStackBuffer,
    0
  );

  //init the password and keys
  init_password();
}

void loop() {
  static uint8_t tempDeviceMode = 255; //debug variable used to print changes in device mode
  static bool shouldScanRxBuffer = false; //flag that gets set when the rxBuffer should be scanned through (ie. when data is added)

  //Debug: If a device mode change was detected log it to serial if we are in debug mode
  if (lastDeviceMode != tempDeviceMode) {
    Debug(Serial1.printf("Device Mode change detected! New device mode is %d\n", lastDeviceMode));
    tempDeviceMode = lastDeviceMode;
  }

  //----------------------------------------------------- MISC State Behavior -------------------------------------------------
  if (lastDeviceMode == CAD_FAILED) { //if CAD detected a signal, then just go back to RX mode until CAD is ready to try again
    LoRa.receive();
    lastDeviceMode = RX_MODE;
    LError("CAD detected a signal! trying again later");
  }
  static bool startedDeviceIDAcquire = false;
  static bool initializedDeviceRouting = false;
  //Some debug information for logging in 
  static uint32_t lastDebugPrintTime = millis();
  static uint8_t printTimeCount = 0;
  if (millis() - lastDebugPrintTime > 5000) {
    lastDebugPrintTime = millis();
    Debug(Serial1.printf("\nPaired Status: %d\nLogged In Status: %d\n", sec_isPaired(), sec_isLoggedIn()));
    Debug(Serial1.printf("Current Device ID: %d\n", deviceID));
    Debug(Serial1.printf("initializedDeviceRouting: %d\n", initializedDeviceRouting));
    Debug(Serial1.printf("startedDeviceIDAcquire: %d\n", startedDeviceIDAcquire));
    Debug(Serial1.printf("receivedDeviceIDTable: %d\n", receivedDeviceIDTable));
    printTimeCount++;
    if (printTimeCount > 6) {
      LDebug("Dumping Device ID Table contents:");

    }
  } 

  enableLora = sec_isPaired() && sec_isLoggedIn() && epochAtBoot != 0;
  static bool lastLoraEnableStatus = !enableLora;
  if (lastLoraEnableStatus != enableLora) {
    LDebug("Lora Enable status has changed!");
    switch (lastLoraEnableStatus) {
      case true: //actually false since we are checking the previous state
        LDebug("Lora has been disabled, putting into sleep mode");
        LoRa.sleep();
        lastDeviceMode = SLEEP_MODE;
        receiveReady = false;
        shouldScanRxBuffer = false;
        {
          ScopeLock(loraRxSpinLock, loraRxLock);
          rxMessageArray.clearAll();
          rxMessageBuffer.clear();
        }
        {
          ScopeLock(loraTxSpinLock, loraTxLock);
          txMessageArray.clearAll();
          txMessageBuffer.clear();
        }
        rxBuffer.clearBuffer();
        readyToSendBuffer.clearBuffer();
        ackToSendBuffer.clearBuffer();
        previouslySeenIds.clearBuffer();
        previouslyProcessedIds.clearBuffer();
        serialReadyToSendArray.clearAll();
      break;
      case false: //actually true since we are checking the opposite case
        LDebug("Lora has been enabled");
        rxBuffer.clearBuffer();
        LoRa.receive();
        lastDeviceMode = RX_MODE;
    }
    lastLoraEnableStatus = enableLora;
  }


  //-------------------------------------------------------Device ID management ----------------------------------------------------

  static uint32_t lastPrintedDeviceIDTime = millis();
  if (millis() - lastPrintedDeviceIDTime > 5000) {
    lastPrintedDeviceIDTime = millis();
    display.setCursor(0,0);
    display.clearDisplay();
    display.printf("Device ID: %d\n", deviceID);
    display.display();
  }
  

  static uint32_t deviceIDAcquireStartTime = millis();
  //if we have logged in, then pull the device ID and table from memory. if they arent stored, then just put 255 in for the device ID and a blank table in
  if (sec_isLoggedIn() && sec_isPaired() && epochAtBoot != 0) {
    //If we have not initialized the device routing yet, then initialize it
    if (!initializedDeviceRouting) {
      LDebug("Logged in and paired! initializing device routing variables");
      initializedDeviceRouting = true;
      initializeDeviceRouting();
    }

    //If the deviceIDchanged flag is set, then the table has changed, or the device ID has changed. Either way, trigger a full rewrite to EEPROM
    if (deviceIDDataChanged) {
      LDebug("Device ID data has changed!, attempting to write data to EEPROM");
      storeDeviceIDData(false);
    }

    //if our device ID is currently 255, then we are in searching mode, 
    if (deviceID == 255) {
      if (!startedDeviceIDAcquire) {
        LDebug("Device ID is set to 255, trying to acquire a device ID");
        startedDeviceIDAcquire = true;
        receivedDeviceIDTable = false; 
        deviceIDAcquireStartTime = millis();
      }
      sendDeviceIDQueryMessages();
      if (receivedDeviceIDTable || millis() - deviceIDAcquireStartTime > 10000) {
        LDebug("Device ID table has been received, or we've hit the 10 second timeout, attempting to acquire a device ID");
        chooseOpenDeviceID();
        LDebug("Acquired Device ID!");
        //now that an id has been chosen, send out ID, and force update our table
        storeDeviceIDData(true);
        sendDeviceIDResponseFunc();
      }
    } else {
      startedDeviceIDAcquire = false;
    }

    //Every 60 or so seconds, send out an additional device ID request
    static uint32_t lastRandomDeviceIDRequestSendTime = millis();
    if (millis() - lastRandomDeviceIDRequestSendTime > 60000) {
      LDebug("60 seconds elapsed: sending additional random device ID request");
      sendDeviceIDRequestFunc();
      lastRandomDeviceIDRequestSendTime = millis();
    } 


  } else if (sec_isLoggedIn()) {
    //logged in, but unpaired, so clear the device routing completely
    if (initializedDeviceRouting) {
      LDebug("User is logged in but is not paired, clearing local routing data");
      resetDeviceRouting();
      initializedDeviceRouting = false;
    }
  } else {
    //we are not logged in anymore, so just clear the local variabes, dont need to worry about deleting the eeprom
    deviceID = 255;
    initializedDeviceRouting = false;
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
      Debug(Serial1.printf("First Byte of Data: %d\n", tempBuf[0]));
      Debug(Serial1.printf("Second Byte of Data: %d\n", tempBuf[1]));
      //Data was successfully added, so set the shouldScanRxBuffer condition
      shouldScanRxBuffer = true;
    } else {
      LWarn("Rx Buffer is currently full, not adding data");
    }

    //NOTE - After the rx is completed, what mode is the lora in? We assume it remains in RX mode for now, so no mode change is necessary
  }

  // -------------------------------------------------- Receive Loop Behavior ---------------------------------------------
  if (shouldScanRxBuffer) { //this gets set to true when data gets added to rxBuffer, or if theres still potentially a message in rxBuffer after a scan
    //First, we will scan for start bytes. If we find any, we will then scan from the start byte to j in range(rxBufferLastSize, actual buffer size)
    //If we find a valid message, we will clear any data from the buffer before the valid message.
    /*PseudoCode
      for each start byte:
        if there is a valid message with the end byte in (rxBufferLastSize, actual buffer size)
          process messages
          clear all data in the buffer up to the end of the message
          update rxBufferLastSize to the end of the messages
        if no valid message is found and we've scanned 256 bytes, then clear everything up to and including the start byte
      if no message was ever found, then update rxBufferLastSizeto the end of the data
    

    */
    shouldScanRxBuffer = false;
    bool messageFound = false;
    for (int startByteLocation = 0; startByteLocation < rxBuffer.size(); startByteLocation++) {
      
      if (rxBuffer[startByteLocation] == START_BYTE) {
        //start byte found, scan from rxBufferLastSize to rxBuffer.size() for the end byte
        if (rxBufferLastSize > rxBuffer.size()) {
          LDebug("RXBufferLastSize was not properly updated, and it is now larger than rxBuffer!");
          HALT();
        }
        for (int endByteLocation = max(startByteLocation+1, (int) (rxBufferLastSize - 1)); endByteLocation < min((int) (startByteLocation + 256), (int) rxBuffer.size()); endByteLocation++) {
          if (rxBuffer[endByteLocation] == END_BYTE) {
            const uint8_t messageSize = endByteLocation - startByteLocation + 1;
            if (messageSize < 8 + AES_GCM_OVERHEAD) continue;
            LDebug("Found End Byte in rxBuffer");
            LDebug("Message Identified...");
            //Debug(dumpArrayToSerial(&(rxBuffer[0]), i+1));

            //First, Calculate the CRC and check if its correct 
            uint32_t crc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(rxBuffer[startByteLocation+1])), messageSize - 4))^0xffffffff;
            uint16_t msgCrc = (rxBuffer[endByteLocation-2] << 8) + rxBuffer[endByteLocation-1]; 
            if ((crc & 0xFFFF) != msgCrc) {
              LDebug("Received RX message does not have matching CRC, skipping");
              continue;
            } 

            //check if that packet type is invalid
            const uint8_t packetType = rxBuffer[startByteLocation+1];
            if (packetType > 5) {
              LDebug("Received RX message does not have proper type byte, skipping");
              continue;
            }

            //Since CRC passed, its time to decrypt the message, so lets decrypt it into a temp buffer
            uint8_t tempBuf[256];
            size_t plaintextLen;
            if (!decryptD2DMessage(&(rxBuffer[startByteLocation+2]), messageSize-5, &(tempBuf[0]), 256, &plaintextLen)) {
              LDebug("Decryption Failed, assuming message has been tampered with since CRC still passed");
              //TODO tamper detection OR different key detection
              continue;
            }

            //Verify the plaintextLen is what is expected
            if (plaintextLen != messageSize - 5 - AES_GCM_OVERHEAD) {
              LError("Received plaintext message from rx is unexpected size!");
              HALT();
            }

            //Now, the message should be fully contained in tempBuf with length plainTextLen, which excludes the start/stop bytes, the message type, the encryption overhead, and the CRC
            //since we got this far, we can reasonably assume the message is valid, so we can remove it from the buffer
            messageFound = true;
            rxBuffer.dropFront(endByteLocation+1);
            rxBufferLastSize = 0;
            shouldScanRxBuffer = true; //there could be another message to find, go look again

            //Check if we should filter out the message based on message type and potential receiver field
            bool broadcast = false; //used to indicate if a data message is intended for broadcast, so no ack should be sent out
            bool breakout = false;
            switch (packetType) {
              case 0:
                if (tempBuf[1] == 255) {
                  broadcast = true;
                } else if (tempBuf[1] != deviceID) {
                  LDebug("Received RX Data message is not intended for sender, skipping");
                  //log the message ID
                  const uint16_t messageNumber = (tempBuf[2] << 8) + tempBuf[3]; 
                  previouslySeenIds.pushBack(&messageNumber, 1);
                  if (previouslySeenIds.size() >= 128) {
                    previouslySeenIds.dropFront(1);
                  }

                  //log the deviceID of the sender
                  addDeviceIDToTable(tempBuf[0]);
                  breakout = true; //the message was intended for this device, so indicate we should break out
                }
                break;
              case 1:
                if (tempBuf[1] != deviceID) {
                  LDebug("Received RX Ack message is not intended for sender, skipping");
                  breakout = true;
                }
                break;
              case 2: //device ID scan is a broadcast message, so no receiver field is present
                break;
              case 3: //device ID scan response is also a broadcast message, so no receiver field is present
                break;
              case 4: //device ID full table request DOES have a receiver field, so filter on it
                if (tempBuf[0] != deviceID) {
                  LDebug("Received Device ID Table request is not intended for sender, skipping");
                  breakout = true;
                }
              case 5: //device ID full table response is also a broadcast message, so no receiver field is present
                break;
            }
            if (breakout) break;

            //check if the message was intended to be sent in the last 20 seconds based on the timestamp
            //Since timestamp is dependant on message type, use a switch statement to acquire it
            uint32_t timestamp;
            switch (packetType) {
              case 0:
                //data packet
                timestamp = (tempBuf[6] << 24) + (tempBuf[7] << 16) + (tempBuf[8] << 8) + tempBuf[9];
              break;
              case 1:
                //ack packet
                timestamp = (tempBuf[5] << 24) + (tempBuf[6] << 16) + (tempBuf[7] << 8) + tempBuf[8];
              break;
              case 2:
              case 3:
              case 4:
                timestamp = (tempBuf[1] << 24) + (tempBuf[2] << 16) + (tempBuf[3] << 8) + tempBuf[4];
              break;
              case 5:
                timestamp = (tempBuf[0] << 24) + (tempBuf[1] << 16) + (tempBuf[2] << 8) + tempBuf[3];
              break;
            }
            const uint32_t currentTime = (millis() / 1000) + epochAtBoot;
            if (currentTime + 5 < timestamp) { //5 is added for a bit of leeway
              LWarn("Received RX Message is from the future! someone likely has invalid time configuration");
              //break; //TODO TEMP dont break so we can continue running with invalid times
            }
            if (currentTime > timestamp && currentTime - timestamp > 20) {
              LWarn("received RX Message is very old, possible replay attack attempt");
              Debug(Serial1.printf("current time: %ld\ntime indicated by message: %ld\n", (millis() / 1000) + epochAtBoot, timestamp));
              //TODO logic to log replay attack attempt
              //break; //the message was valid, so lets break out TODO TEMP dont break out so wee can continue running 
            }
            
            //Now that checks have passed, we can attempt to process the message. First, lets see what type of message it is


            if (packetType == 0) {
              ScopeLock(loraRxSpinLock, loraRxLock);
              LDebug("Beginning Normal Message Processing");
              //Normal message
              const uint8_t sequenceCount = tempBuf[5];
              const uint8_t sequenceSize = plaintextLen - 10; //subtracting header size
              const uint16_t messageNumber = (tempBuf[2] << 8) + tempBuf[3]; 
              const uint8_t sequenceNumber = tempBuf[4]; 
              if (sequenceNumber > 7) {
                LError("Invalid sequence number! dropping");
                break;
              }

              //Add the sender ID to our list of known device IDs
              addDeviceIDToTable(tempBuf[1]);
              

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

                //Check if the message ID is in the previouslyProcessedIds list. If it is, its possible we have already processed this message
                if (previouslyProcessedIds.contains(messageNumber)) {
                  LWarn("Received Message has a previously seen ID, ignoring");
                  //since the ID was previously processed, its likely that the message was already received, but the ack failed
                  //Thus, we will still send an ack just in case, but we will otherwise silently drop the message
                  if (!broadcast) sendAck(tempBuf[0], messageNumber, sequenceNumber);
                  continue;
                }

                //if it wasnt, then add it for future use
                previouslyProcessedIds.pushBack(&messageNumber, 1);
                if (previouslyProcessedIds.size() >= 128) {
                  previouslyProcessedIds.dropFront(1);
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

              if (!broadcast) sendAck(tempBuf[0], messageNumber, sequenceNumber);
              
            } else if (packetType == 1) {
              ScopeLock(loraTxSpinLock, loraTxLock);
              LDebug("Beginning ACK Message Processing");
              //Ack Message - we need to process the ack
              

              const uint16_t messageNumber = (tempBuf[2] << 8) + tempBuf[3]; 
              const uint8_t sequenceNumber = tempBuf[4]; 
              if (sequenceNumber > 7) {
                LError("Invalid sequence number! dropping");
                break;
              }

              //Add the sender ID to our list of known device IDs
              addDeviceIDToTable(tempBuf[1]);

              //First, search for the relevant message in the txMessageArray by its message number and sequence number
              for (int i = 0; i < txMessageArray.size(); i++) {
                if ((txMessageArray.get(i)[0] << 8) + txMessageArray.get(i)[1] == messageNumber && txMessageArray.get(i)[2] == sequenceNumber) {
                  LDebug("Found Message - Indicated ACK has been received");
                  //we found the right message, so indicate the ack has been received
                  txMessageArray.get(i)[8] |= 0b10000000;
                }
              }
            } else if (packetType == 2) {
              LDebug("Processing Device ID request");
              if (plaintextLen != 5) {
                LWarn("Received Device ID Scan message with incorrect size!");
                break;
              }
              //we received a valid device ID request, so indicate to the send functionality that we should dispatch the device ID only if we havent received one in 10 seconds
              if ((millis() / 1000) > lastDeviceIDResponseTime + 10) {
                lastDeviceIDResponseTime = millis() / 1000;
                LDebug("Constructing device id response packet");
                sendDeviceIDResponseFunc();      
              } else {
                LDebug("Not setting sendDeviceIDResponse since one has been dispatched in the past 10 seconds");
              }
            } else if (packetType == 3) {
              LDebug("Processing Device ID Response");
              if (plaintextLen != 5) {
                LWarn("Received Device ID Scan Response message with incorrect size!");
                break;
              }
              //we received a valid device ID response, so log the ID has being taken in our device ID list
              const uint8_t receivedDeviceID = tempBuf[0];
              addDeviceIDToTable(receivedDeviceID);
              if (receivedDeviceID == 255) {
                LWarn("Received a device ID response from the broadcast ID, which was unexpected! ignoring");
                break;
              }
            } else if (packetType == 4) {
              LDebug("Processing Device ID Table Request");
              if (plaintextLen != 5) {
                LWarn("Received Device ID Table request message with incorrect size!");
                break;
              }
              //we received a device Table request, so indicate to the send functionality that we should dispatch the full device Table only if we havent received one in 10 seconds
              if ((millis() / 1000) > lastDeviceIDTableResponseTime + 10) {
                LDebug("Creating device id table requst packet");
                lastDeviceIDTableResponseTime = millis() / 1000;
                
                //plaintext buffer
                uint8_t pBuf[36];
                pBuf[0] = lastDeviceIDTableResponseTime >> 24;
                pBuf[1] = (lastDeviceIDTableResponseTime >> 16) & 0xFF;
                pBuf[2] = (lastDeviceIDTableResponseTime >> 8) & 0xFF;
                pBuf[3] = (lastDeviceIDTableResponseTime) & 0xFF;

                memcpy(&(pBuf[4]), &(deviceIDList[0]), 32);

                //encrypt message contents
                size_t ciphertextLen;
                if (encryptD2DMessage(&(pBuf[0]), 36, &(deviceIDTableResponseBuffer[2]), 36 + AES_GCM_OVERHEAD, &ciphertextLen)) {
                  LDebug("Successfully encrypted device id table response message content");
                } else {
                  LError("Failed to encrypt device id table response message content");
                  HALT();
                }
                if (ciphertextLen != 36 + AES_GCM_OVERHEAD) {
                  LError("Unexpected ciphertext length");
                }

                //Calculate CRC on everything after the start byte
                uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(deviceIDTableResponseBuffer[1])), 37 + AES_GCM_OVERHEAD))^0xffffffff;
                deviceIDTableResponseBuffer[38 + AES_GCM_OVERHEAD] = (newCrc & 0x0000FF00) >> 8;
                deviceIDTableResponseBuffer[39 + AES_GCM_OVERHEAD] = newCrc & 0x000000FF;

                sendDeviceIDTableResponse = true;
                
                LDebug("Setting sendDeviceIDTableResponse to true");
              } else {
                LDebug("Not setting sendDeviceIDTableResponse since one has been dispatched in the past 10 seconds");
              }
              
            } else if (packetType == 5) {
              LDebug("Processing Device ID Table response packet");
              if (plaintextLen != 36) {
                LWarn("Received Device ID Table response message with incorrect size!");
              }

              receivedDeviceIDTable = true;
              //we received a full device table, so update our device table 
              for (int byteNum = 0; byteNum < 32; byteNum++) {
                if (~deviceIDList[byteNum] & tempBuf[4+byteNum]) {
                  deviceIDDataChanged = true;
                }
                deviceIDList[byteNum] |= tempBuf[4+byteNum];
              }
            }
            //If we've gotten this far, then a message was successfully processed, so break out of the loop checking this specific start byte
            break;
          }
        }
        //end of end byte for loop. If we got this far with a message detection, we continue the breaks
        if (messageFound) break;
      }
    }

    //end of start and stop byte loops. if we got this far with no message detected, then we need to do some buffer cleaning.
    //first, we should drop the front of the buffer until it is 256 bytes max
    //then, we should update the rxBufferLastSize variable appropriately
    if (!messageFound) {
      if (rxBuffer.size() > 256) {
        shouldScanRxBuffer = true; //there more data that didn't get scanned potentially, so rescan
        rxBuffer.dropFront(rxBuffer.size() - 256);
      }
      rxBufferLastSize = rxBuffer.size();
    }
  }

  //scan through the RX message array and look for any completed messages or any expiring messages
  static uint32_t lastRxProcess = millis();
  if (millis() > lastRxProcess + 500) {
    //LDebug("Attemping to acquire rx scope lock");
    ScopeLock(loraRxSpinLock, loraRxLock);
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
        
        {
          ScopeLock(serialLoraBridgeSpinLock, serialLoraBridgeLock);
          if (serialReadyToSendArray.add(&(tempBuf[0]))) {
            LDebug("Dispatched message to readytosendarray");
          } else {
            LError("Failed to dispatch message ot readytosendarray");
          }
        }
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
    //since all this function does is perform reads from the txMessageBuffer, it doesn't need a lock since the function that handles removing data from txMessageBuffer is located in this thread
    //We just finished CAD, so send a message
    //the dispatch order is this (from highest to lowest precedence): 
    //            data packet  -  ack packet  -  device ID request  -  device ID response  -  device Table request  -  device Table response

    if (readyToSendBuffer.size() > 0) { //if there is a data packet to send...
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
    } else if (ackToSendBuffer.size() > 0) { //if there is a ACK packet to send...
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
    } else if (sendDeviceIDRequest) { //if we should dispatch a device ID request...
      sendDeviceIDRequest = false;
      LoRa.beginPacket();
      LoRa.write(&(deviceIDRequestBuffer[0]), 10 + AES_GCM_OVERHEAD);
      lastDeviceMode = TX_MODE;
      LoRa.endPacket(true);
      LDebug("Finished writing device id request message to LoRa");
    } else if (sendDeviceIDResponse) { //if we should dispatch a device ID response...
      sendDeviceIDResponse = false;
      LoRa.beginPacket();
      LoRa.write(&(deviceIDResponseBuffer[0]), 10 + AES_GCM_OVERHEAD);
      lastDeviceMode = TX_MODE;
      LoRa.endPacket(true);
      LDebug("Finished writing device id response message to LoRa");

    } else if (sendDeviceIDTableRequest) { //if we should dispatch a device id table request...
      sendDeviceIDTableRequest = false;
      LoRa.beginPacket();
      LoRa.write(&(deviceIDTableRequestBuffer[0]), 10 + AES_GCM_OVERHEAD);
      lastDeviceMode = TX_MODE;
      LoRa.endPacket(true);
      LDebug("Finished writing device id table request message to LoRa");

    } else if (sendDeviceIDTableResponse) { //if we should dispatch a device id table response... 
      sendDeviceIDTableResponse = false;
      LoRa.beginPacket();
      LoRa.write(&(deviceIDTableResponseBuffer[0]), 41 + AES_GCM_OVERHEAD);
      lastDeviceMode = TX_MODE;
      LoRa.endPacket(true);
      LDebug("Finished writing device id table response message to LoRa"); 
    }


    //LError("Cad Finished with no data in either buffer!");
    
  }

  // -------------------------------------------- Transmit Loop Behavior ---------------------------------------------
  if (messageDispatched) { //if we sent a TX messsage clean it out of the buffer
    ScopeLock(loraTxSpinLock, loraTxLock);
    LDebug("Clearing sent normal message out of TX buffer");
    messageDispatched = false;
    readyToSendBuffer.dropFront(3);
  } else if (ackDispatched) {
    ScopeLock(loraTxSpinLock, loraTxLock);
    LDebug("Clearing sent ACK message out of TX buffer");
    ackDispatched = false;
    ackToSendBuffer.dropFront(14 + AES_GCM_OVERHEAD);
  }

  static uint32_t lastTxProcess = millis(); //NOTE at some point, this should be made into a looping variable. It will overflow in about 1.5 months
  if (millis() > lastTxProcess + 500) {
    //LDebug("Attempting to acquire tx lock");
    ScopeLock(loraTxSpinLock, loraTxLock);
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
        Debug(Serial1.printf("Diff = %d, 1 = %d, 2 = %d\n", diff(millis() % 65536, lastSendTime, 65536), millis() % 65536, lastSendTime));
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
  

  if (readyToSendBuffer.size() > 0 || ackToSendBuffer.size() > 0 || sendDeviceIDTableResponse || sendDeviceIDResponse || sendDeviceIDRequest || sendDeviceIDTableRequest) {
    //LDebug("One of the TX buffers has data, attempting to enter CAD Mode");
    enterChannelActivityDetectionMode();
  }

  // ------------------------------------------------------------- SERIAL HANDLING ---------------------------------------------------------------

  //NOTE this is temporary code
  //For now, we will just push the code straight to the serial buffer
  /*
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
  */

  //TEST CODE
  /*
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
  */

  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer

  //test code to test sending::
  
}

void resetDeviceRouting() {
  deviceID = 255;
  memset(&(deviceIDList), 0, 32);
  storage.remove("DeviceIDs");
  storeDeviceIDData(true);
}

void storeDeviceIDData(bool forceUpdate) {
  static uint32_t lastEEPROMUpdateTime = 0;
  if (!forceUpdate) {
    if ((millis() / 1000) - lastEEPROMUpdateTime < 10) {
      LDebug("Store Device Data requested, but ignored");
      return;
    }
  }
  deviceIDDataChanged = false;
  uint8_t pBuf[1 + 32];
  uint8_t eBuf[1 + 32 + AES_GCM_OVERHEAD];

  //place id data into plaintext buf
  pBuf[0] = deviceID;
  memcpy(&(pBuf[1]), &(deviceIDList[0]), 32);

  //try to encrypt the data
  size_t ciphertextLen;
  if (!encryptD2DMessage(&(pBuf[0]), 1 + 32, &(eBuf[0]), 1 + 32 + AES_GCM_OVERHEAD, &ciphertextLen)) {
    LError("Failed to encrypt EEPROM data for some reason, device id information will not be stored!");
    return;
  } 

  if (ciphertextLen != 1 + 32 + AES_GCM_OVERHEAD) {
    LError("Unexpected decryption size!!!");
    HALT();
  }

  LDebug("Placed device id and table into EEPROM");
  //now that its been successfully encrypted, store the data the eeprom
  storage.putBytes("DeviceIDs", &(eBuf[0]), 1 + 32 + AES_GCM_OVERHEAD);
  return;
}

void initializeDeviceRouting() {
  //we just logged in, so pull device ID and related data from EEPROM
  if (storage.isKey("DeviceIDs")) {
    LDebug("Found device ID table key, attempting to pull from there");
    //check that the key is the right size
    if (storage.getBytesLength("DeviceIDs") != 1 + 32 + AES_GCM_OVERHEAD) {
      LError("Unexpected device id eeprom data size, resetting device id list");
      resetDeviceRouting();
      return;
    }

    //key does exist, so pull it, decrypt it with the aes-gcm decryption, 
    uint8_t tempBuf[1 + 32 + AES_GCM_OVERHEAD];
    storage.getBytes("DeviceIDs", &(tempBuf[0]), 1 + 32 + AES_GCM_OVERHEAD);
    uint8_t pBuf[1 + 32];
    size_t plaintextLen;
    if (!decryptD2DMessage(&(tempBuf[0]), 1 + 32 + AES_GCM_OVERHEAD, (&pBuf[0]), 1 + 32, &plaintextLen)) {
      LError("Decryption of device id and id table failed, Resetting the device id and table");
      resetDeviceRouting();
      return;
    }

    //assert decryption is the correct size
    if (plaintextLen != 1 + 32) {
      LError("Unexpected decryption size on device id and id table!");
      HALT();
    }

    //now that we have the data, place it.
    LDebug("Successfully pulled device ID and ID Table");
    deviceID = pBuf[0];
    memcpy(&(deviceIDList[0]), &(pBuf[1]), 32);
  } else { //if the device ID table doesnt exist, then just set it to defaults
    LDebug("Failed to find device ID table key, setting default values for the device ID and the device ID List");
    deviceID = 255;
    memset(&(deviceIDList[0]), 0, 32);
  }
}

void sendAck(const uint8_t dstID, const uint16_t messageNumber, const uint8_t sequenceNumber) {
  //Send an ACK. Since the readyToSendBuffer only references data in other buffers, we will have a seperate ACK buffer
  LDebug("Requesting ACK Send: Adding send to ack buffer");
  uint8_t uBuf[9]; //this is the data that will eventually be encrypted
  uBuf[0] = deviceID;
  uBuf[1] = dstID;
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
}

//This function will take the data in src
//NOTE whatever function that calls this needs to handle acquiring the correct lock
bool addMessageToTxArray(uint8_t* src, uint16_t size, uint8_t destinationID) {
  if (lastDeviceMode == SLEEP_MODE) {
    LDebug("Ignoring add to message array request, device is not enabled");
    return false;
  }

  if (destinationID == deviceID) {
    LWarn("Ignoring message attempting to be sent to own device");
    return false;
  }

  if (deviceID == 255 || deviceID == 0) {
    LWarn("Device has invalid ID, ignoring");
    return false;
  }

  //first, make sure the data isn't too big
  //display.clearDisplay();
  //display.setCursor(0,0);
  //display.printf("addMessageToTxArray");
  //display.display();

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
    
    if (attemptCount >= 80) {
      LError("Reached 10 attempts to find a new message number");
      HALT();
    }
    
    for (int i = 0; i < txMessageArray.size(); i++) {
      if (messageNumber == (txMessageArray.get(i)[0] << 8) + txMessageArray.get(i)[1]) {
        foundNumber = false;
        break;
      }
    }
    if (!foundNumber) continue;
    for (int i = 0; i < previouslySeenIds.size(); i++) {
      if (messageNumber == previouslySeenIds[i]) {
        foundNumber = false;
        break;
      }
    }
    if (!foundNumber) continue;
    for (int i = 0; i < previouslyProcessedIds.size(); i++) {
      if (messageNumber == previouslyProcessedIds[i]) {
        foundNumber = false;
        break;
      }
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
  //display.printf("------ done ");
  //display.display();
  return true;
}

void enterChannelActivityDetectionMode() {
  //NOTE - we don't seem to have a way to check if an message is actively being received. Thus, we may accidentally kick the device out of RX mode while is message is transmitting.
  if (millis() > nextCADTime) {
    if (lastDeviceMode == RX_MODE || lastDeviceMode == IDLE_MODE) {
      lastDeviceMode = CAD_MODE;
      LLog("Entering Channel Activity Detection Mode");
      LoRa.idle();
      delay(5);
      LoRa.channelActivityDetection(); 
    }
  }
}

bool sendDeviceIDTableRequestFunc(uint8_t targetDeviceID) {
  LDebug("Request to send device id table request");
  static uint32_t lastSendTime = 0;
  if(millis() - lastSendTime < 8000) {
    LDebug("Ignoring send device id table request, one has already been dispatched in the last 8 seconds");
    return false;
  }
  lastSendTime = millis();

  //plaintext data
  uint8_t pBuf[5 + AES_GCM_OVERHEAD];
  pBuf[0] = targetDeviceID;
  uint32_t timestamp = millis() / 1000;
  pBuf[1] = timestamp >> 24;
  pBuf[2] = (timestamp >> 16) & 0xFF;
  pBuf[3] = (timestamp >> 8) & 0xFF;
  pBuf[4] = timestamp & 0xFF;

  //encrypt the buffer
  size_t ciphertextLen;
  if (encryptD2DMessage(&(pBuf[0]), 5, &(deviceIDTableRequestBuffer[2]), 5 + AES_GCM_OVERHEAD, &ciphertextLen)) {
    LDebug("Successfully encrypted device id table request message content");
  } else {
    LError("Failed to encrypt device id table request message content");
    HALT();
  }
  if (ciphertextLen != 5 + AES_GCM_OVERHEAD) {
    LError("Unexpected ciphertext length");
    return false;
  }

  //calculate the crc
  uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(deviceIDTableRequestBuffer[1])), 6 + AES_GCM_OVERHEAD))^0xffffffff;
  deviceIDTableResponseBuffer[7 + AES_GCM_OVERHEAD] = (newCrc & 0x0000FF00) >> 8;
  deviceIDTableResponseBuffer[8 + AES_GCM_OVERHEAD] = newCrc & 0x000000FF;

  //set the send flag to true
  sendDeviceIDTableRequest = true;
  return true;
}

bool sendDeviceIDResponseFunc() {
  //fill plaintext buffer
  uint8_t pBuf[5]; 
  uint32_t t = millis();
  pBuf[0] = deviceID;
  pBuf[1] = t >> 24;
  pBuf[2] = (t >> 16) & 0xFF;
  pBuf[3] = (t >> 8) & 0xFF;
  pBuf[4] = (t) & 0xFF;
  
  //encrypt message contents
  size_t ciphertextLen;
  if (encryptD2DMessage(&(pBuf[0]), 5, &(deviceIDResponseBuffer[2]), 5 + AES_GCM_OVERHEAD, &ciphertextLen)) {
    LDebug("Successfully encrypted device id response message content");
  } else {
    LError("Failed to encrypt device id response message content");
    HALT();
  }
  if (ciphertextLen != 5 + AES_GCM_OVERHEAD) {
    LError("Unexpected ciphertext length");
  }

  //Calculate CRC on everything after the start byte
  uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(deviceIDResponseBuffer[1])), 6 + AES_GCM_OVERHEAD))^0xffffffff;
  deviceIDResponseBuffer[7 + AES_GCM_OVERHEAD] = (newCrc & 0x0000FF00) >> 8;
  deviceIDResponseBuffer[8 + AES_GCM_OVERHEAD] = newCrc & 0x000000FF;

  //Now that the message is ready to dispatch, set the flag
  sendDeviceIDResponse = true;
  LDebug("Setting sendDeviceIDResponse to true");

  return true;
}

bool sendDeviceIDRequestFunc() {
  //TODO consider adding a rate limit here
  LDebug("Request to send device id request");
  //plaintext data
  uint8_t pBuf[5 + AES_GCM_OVERHEAD];
  pBuf[0] = deviceID;
  uint32_t timestamp = millis() / 1000;
  pBuf[1] = timestamp >> 24;
  pBuf[2] = (timestamp >> 16) & 0xFF;
  pBuf[3] = (timestamp >> 8) & 0xFF;
  pBuf[4] = timestamp & 0xFF;

  //encrypt the buffer
  size_t ciphertextLen;
  if (encryptD2DMessage(&(pBuf[0]), 5, &(deviceIDRequestBuffer[2]), 5 + AES_GCM_OVERHEAD, &ciphertextLen)) {
    LDebug("Successfully encrypted device id request message content");
  } else {
    LError("Failed to encrypt device id request message content");
    HALT();
  }
  if (ciphertextLen != 5 + AES_GCM_OVERHEAD) {
    LError("Unexpected ciphertext length");
    return false;
  }

  //calculate the crc
  uint32_t newCrc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)(&(deviceIDRequestBuffer[1])), 6 + AES_GCM_OVERHEAD))^0xffffffff;
  deviceIDRequestBuffer[7 + AES_GCM_OVERHEAD] = (newCrc & 0x0000FF00) >> 8;
  deviceIDRequestBuffer[8 + AES_GCM_OVERHEAD] = newCrc & 0x000000FF;

  //set the send flag to true
  sendDeviceIDRequest = true;
  return true;
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
    Serial1.printf("[%s]: %s\n", logLevelEnumToChar(level), text);
  }
}

void dumpArrayToSerial(const uint8_t* src, const uint16_t size) {
  Serial1.printf("Dumping Array to Serial: \n");
  for (int i = 0; i < size; i++) {
    Serial1.printf("%d ", src[i]);
  }
  Serial1.printf("\n");
}

void chooseOpenDeviceID() {
  uint8_t id;
  while(1) {
    id = esp_random();
    if (id == 0 || id == 255) break;
    if (deviceIDList[id / 32] >> (7 - (id % 8)) == 0) {
      deviceID = id;
      deviceIDList[id / 32] |= (1 << (7 - (id % 8)));
      return;
    }
  }
}

//This function will do quite a bit of heavy lifting. 
//Every 5 seconds, it will send out a device ID request along with a device ID Table request if a device has been found
//After it detects that at least one device list has been received, it will choose a random ID from those not available before setting it and then sending it out
void sendDeviceIDQueryMessages() {
  static uint32_t lastCallTime = millis()/1000;
  if (millis()/1000 - lastCallTime < 5) {
    LDebug("Not Sending device ID query messages: last one sent too recently");
    return;
  } 
  LDebug("Starting device ID query messages");
  lastCallTime = millis()/1000;
  sendDeviceIDRequestFunc();
  for (int b = 0; b < 32; b++) {
    for (int bit = 0; bit < 8; bit++) {
      if (deviceIDList[b] >> (7 - bit) == 1) {
        //device id set, so send a table request
        LDebug("Found a device ID to send a table request to"); //TODO dont just send to the first ID
        sendDeviceIDTableRequestFunc(b * 8 + bit);
        return;
      }
    }
  }
}

void addDeviceIDToTable(uint8_t id) {
  if (deviceIDList[id / 32] >> (7 - (id % 8)) == 0) {
    deviceIDList[id / 32] |= 1 << (7 - (id % 8));
    deviceIDDataChanged = true;
    LDebug("Adding device ID to table");
  }
}

void enterSleepMode() {

}






