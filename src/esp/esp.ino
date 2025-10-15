#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1


#define IDLE_MODE 1
#define RX_MODE 2
#define TX_MODE 3
#define CAD_MODE 4
#define CAD_FINISHED 5
#define SLEEP_MODE 0

#define LLog(x) Log(LOG_LEVEL_LOG, x)
#define LDebug(x) Log(LOG_LEVEL_DEBUG, x)
#define LWarn(x) Log(LOG_LEVEL_WARNING, x)
#define LError(x) Log(LOG_LEVEL_ERROR, x)
#define HALT() Serial.println("Exiting"); while(1)

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


uint8_t deviceID = 1; //TODO store this at the EEPROM instead of as a variable here

uint8_t lastDeviceMode = 1;
uint32_t nextCADTime = 0;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

bool receiveReady = false;

CyclicArrayList<LORA_RX_BUFFER_SIZE> rxBuffer;
SimpleArraySet<256, 9> rxMessageArray;
DefraggingBuffer<2048> rxMessageBuffer;

SimpleArraySet<256, 6> txMessageArray;
DefraggingBuffer<2048> txMessageBuffer;

CyclicArrayList<LORA_READY_TO_SEND_BUFFER_SIZE> readyToSendBuffer;

void setup() {
  //initialize variables
  rxBuffer = CyclicArrayList<LORA_RX_BUFFER_SIZE>();
  rxMessageArray = SimpleArraySet<512, 8>();
  rxMessagebuffer = DefraggingBuffer<2048>();


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
  LoRa.idle();
}

void loop() {
  static bool shouldScanRxBuffer = false; 

  //------------------------------------------------------Interrupt flag handling ------------------------------------------------
  if (receiveReady) {
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
      shouldScanRxBuffer = true;

    } else {
      LWarn("Rx Buffer is currently full, not adding data");
    }

  }

  // -------------------------------------------------- Receive Loop Behavior ---------------------------------------------
  if (shouldScanRxBuffer) {
    shouldScanRxBuffer = false;
    uint16_t startIndex = 65535;
    uint16_t endIndex = 65535;
    //First, detect the first start byte
    for (int i = 0; i < rxBuffer.size(); i++) {
      if (rxBuffer[i] == START_BYTE) {
        startIndex = i;
        break;
      }
    }
    if (startIndex != 65535) {
      //clear everything before the first start byte
      rxBuffer.dropFront(startIndex);
      startIndex = 0;
      
      for (int i = 1; i < min((int)rxBuffer.size(), startIndex + 256); i++) { //i+1 is now the total message length
        if (rxBuffer[i] == END_BYTE) {
          uint8_t tempBuf[256];

          //TODO Decrypt the message and store it in tempBuf. 
          //For now we will send unencrypted messages, so we will just copy it over and not touch it
          memcpy(tempBuf, &(rxBuffer[1]), sizeof(uint8_t) * (i - 1)); //copy contents, excluding start and stop byte
          //now tempbuf contains just the message, going from 0 to i-2, so it contains i-1 bytes

          //check if its a data packet or ack packet
          if (tempBuf[0] != 0 && tempBuf[0] != 1) continue;

          //check if the receiver is correct
          if (tempBuf[3] != deviceID) continue;

          //Calculate the CRC and check if its correct 
          uint32_t crc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)tempBuf, i - 1))^0xffffffff;
          uint16_t msgCrc = (tempBuf[i-3] << 8) + tempBuf[i-2]; 
          if ((crc & 0xFFFF) != msgCrc) continue;

          //Since the message is valid, make sure we send an ACK TODO


          //Now that checks have passed, we can attempt to process the message. First, lets see what type of message it is
          if (tempBuf[0] == 0) {
            //Normal message
            const int8_t messageNumber = tempBuf[3];

            //check if the message number is already being tracked in rxMessageArray
            uint16_t loc = rxMessageArray.find(messageNumber)
            if (loc != 65535) {
              //message number was found in rxMessageArray already, check if this sequence is needed stil
              const uint8_t sequenceNumber = tempBuf[4];
              const uint8_t sequenceBitmask = rxMessageArray.get(loc)[6];
              if (sequenceBitmask & (1 << sequenceNumber)) {
                //message already received, so no need to reprocess
              } else {
                //message not received yet, so mark it in the bitmask and then add the data to the buffer allocation
                rxMessageArray.get(loc)[6] = sequenceBitmask & (1 << sequenceNumber);
                const uint16_t bufferStart = rxMessageArray.get(loc)[1] * 256 + rxMessageArray.get(loc)[2];
                const uint8_t sequenceBaseSize = rxMessageArray.get(loc)[7];
                const uint8_t sequenceSize = i-1 - 8;
                if (sequenceSize > sequenceBaseSize) {
                  LError("Received packet with data size bigger than maximum sequence size!");
                  HALT();
                }
                memcpy(&(rxMessageBuffer[bufferStart + sequenceBaseSize * sequenceNumber]), tempBuf[6], sequenceSize);
                //TODO fill the rest of the buffer with 0x00 if we are populating the final packet
              }
            } else {
              //message was not found, so we need to add it
              const uint8_t messageNumber = tempBuf[3];
              const uint8_t sequenceNumber = tempBuf[4];
              const uint8_t sequenceCount = tempBuf[5];
              
              //Unfortunately, if the last packet is received first, its not possible to tell the total size of the data. 
              //For now, we will just drop the packet and wait for an earlier sequence number packet to arrive first
              //UNLESS its just a one packet message. Then we're good.
              if (sequenceNumber != 0 && sequenceNumber == sequenceCount - 1) {
                continue; //attempt next packet
              }

              const uint8_t sequenceSize = i - 1 - 8;
              const uint32_t totalSequenceSize = sequenceSize * sequenceCount;

              //try to allocate space in the buffer
              const uint16_t bufferLocation = rxMessageBuffer.tryReserve(totalSequenceSize);
              if (bufferLocation == 0xFFFFFFFF) {
                LError("No space for new message found in rx message buffer, dropping!");
              }

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
              headerBuf[8] = (millis() / 1000) % 255; //TODO THIS DOESNT WORK - we need to add overflow checking

              if (rxMessageArray.add(headerBuf)) {
                LDebug("Added new rx message to buffer");
              } else {
                LError("Failed to add new rx message to buffer, rxBufferArray is full!");
              }

              //now that the rxMessageArray and rxMessageBuffer were successfully created, lets populate the rxMessageBuffer
              memcpy(&(rxMessageBuffer[bufferLocation + sequenceSize * sequenceNumber]), tempBuf[i], sequenceSize);
            }
          } else {
            //Ack Message
            //TODO implement
          }
        }
      }

      //Now we have finished processing all possible messages that stem from teh current start byte. So, remove the start byte
      rxBuffer.dropFront(1); //TODO it might be better to drop more than just one byte
    } else {
      //Start byte wasn't found at all in the buffer. Clear the buffer
      rxBuffer.clearBuffer();
    }
  }

  // -------------------------------------------- Transmit Loop Behavior ---------------------------------------------
  //TODO we should probably rate limit this
  for (int i = 0; i < txMessageArray.length(); i++) {
    const uint8_t sendCount = txMessageArray.get(i)[4] & 0b01111111;
    const uint16_t location = (txMessageArray.get(i)[0] << 8) + txMessageArray.get(i)[1];
    //If we've reached the max number of send attempts, drop the data all together
    if (sendCount > LORA_SEND_COUNT_MAX) {
      txMessageBuffer.free(location);
      txMessageArray.remove(i--); //decrement i so that we still iterate over all remaining entries
      continue;
    }

    //If it has been over a second since the previous send, try again //TODO move this to a different value
    uint16_t lastSendTime = (txMessageArray.get(i)[3] << 8) + txMessageArray.get(i)[4];
    if ((millis() % 65535) - lastSendTime > 1000) { //TODO THIS WILL NOT WORK - need to do proper overflow checking
      lastSendTime = millis(); //TODO - the time for CAD to occur is not accounted for in the resend functionality, which is a problem
      txMessageArray.get(i)[3] = lastSendTime >> 8;
      txMessageArray.get(i)[4] = lastSendTime & 0xFF;
      int8_t tBuf[3];
      tBuf[0] = txMessageArray.get(i)[0]; //location high byte
      tBuf[1] = txMessageArray.get(i)[1]; //location low byte
      tBuf[2] = txMessageArray.get(i)[2]; //size
      if (readyToSendBuffer.pushBack(tBuf, 3)) {
        LDebug("Added message to ready to send buffer");
      } else {
        LError("Failed to add message to ready to send buffer because it was full");
      }
    }
  }

  if (readyToSendBuffer.size() > 0) {
    enterChannelActivityDetectionMode();
  }

  // ------------------------------------------------------------------------------------------------------------------------------------------


  //TEST CODE
  static uint32_t mill = millis();
  if (mill + 1000 < millis()) {
    //LoRa.channelActivityDetection();
    mill = millis();
    Serial.printf("Current LoRa Operating Mode: %d\nCurrent IRQ Flag: %d\n", LoRa.readMode(), LoRa.readIrqFlag());
  }

  //TEST CODE
  static uint8_t prevDeviceMode = 5;
  if (prevDeviceMode != lastDeviceMode) {
    Serial.printf("Device Mode Changed! New Mode = %d", lastDeviceMode);
    prevDeviceMode = lastDeviceMode;
  }
  // --------------------------------------------------------------- SERIAL HANDLING ---------------------------------------------------------------
  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer

  //test code to test sending::

  //
  
}

void enterChannelActivityDetectionMode() {
  //NOTE - we don't seem to have a way to check if an message is actively being received. Thus, we may accidentally kick the device out of RX mode while is message is transmitting.
  if (millis() > nextCADTime) {
    if (lastDeviceMode == RX_MODE || lastDeviceMode == IDLE_MODE || lastDeviceMode == SLEEP_MODE) {
      lastDeviceMode = CAD_MODE;
      Serial.println("Entering Channel Activity Detection Mode");
      LoRa.idle();
      delay(5);
      LoRa.channelActivityDetection(); //NOTE - this sets the callback to the CAD callback, so rec and txdone callbacks wont trigger
    }
  }
}

void enterReceiveMode() {
  //Under normal flow, if a message is added to the send buffer, the device will go to CAD mode, then to TX mode, and then to IDLE mode. from there, we can reenter rec mode
  if (lastDeviceMode == IDLE_MODE) {
    lastDeviceMode = RX_MODE;
    Serial.println("Entering Receive Mode");
    //LoRa.receive(); //NOTE - this sets the callback to the REC callback, so cad and txdone callbacks wont trigger
    LoRa.receive();
  }
}
void onCadDone(bool detectedSignal) {
  lastDeviceMode = CAD_FINISHED;
  return;
}
void onTxDone() {
  //free the device on send mode
  return;
  lastDeviceMode = IDLE_MODE;
  LoRa.idle();
}

void onReceive(int size) {
  receiveReady = true;
}

void Log(LOG_LEVEL level, const char* text) {
  if (level <= CURRENT_LOG_LEVEL) {
    Serial.printf("[%s]: %s\n", logLevelEnumToChar(level), text);
  }
}



