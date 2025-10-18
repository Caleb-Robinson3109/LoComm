#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1
#define LORA_READY_TO_SEND_BUFFER_SIZE 1024
#define LORA_ACK_BUFFER_SIZE 256
#define LORA_SEND_COUNT_MAX 8
#define SERIAL_READY_TO_SEND_BUFFER_SIZE 128


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
#define HALT() Serial.println("Exiting"); while(1)

#define diff(new, old, size) (new > old) ? new - old : size - old + new

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


uint8_t deviceID = 1; //NOTE This should eventually be stored on the EEPROM

uint8_t lastDeviceMode = 1;
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

SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 3> serialReadyToSendBuffer; //message addr high, message addr low, message size

void setup() {
  //initialize variables
  rxBuffer = CyclicArrayList<LORA_RX_BUFFER_SIZE>();
  rxMessageArray = SimpleArraySet<256, 9>();
  rxMessageBuffer = DefraggingBuffer<2048, 8>();

  txMessageArray = SimpleArraySet<256, 8>();
  txMessageBuffer = DefraggingBuffer<2048, 8>();

  readyToSendBuffer = CyclicArrayList<LORA_READY_TO_SEND_BUFFER_SIZE>();
  ackToSendBuffer = CyclicArrayList<LORA_ACK_BUFFER_SIZE>();

  serialReadyToSendBuffer = SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 3>();


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

  //----------------------------------------------------- MISC State Behavior -------------------------------------------------
  if (lastDeviceMode == CAD_FAILED) {
    LoRa.idle();
    lastDeviceMode = IDLE_MODE;
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
      
      for (int i = 1; i < min((int)rxBuffer.size(), startIndex + 256); i++) { //i+1 is now the total message length
        if (rxBuffer[i] == END_BYTE) {
          LDebug("Found End Byte in rxBuffer");
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
          if (tempBuf[3] != deviceID) {
            LDebug("Received RX message is not intended for sender, skipping");
            continue;
          }

          //Calculate the CRC and check if its correct 
          uint32_t crc = (~esp_rom_crc32_le((uint32_t)~(0xffffffff), (const uint8_t*)tempBuf, i - 1))^0xffffffff;
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
            if (loc != 65535) { //TODO consider updating the time variable here
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
              headerBuf[8] = (millis() / 1000) % 255; // TODO still need code to handle expiring received messages

              if (rxMessageArray.add(headerBuf)) {
                LDebug("Added new rx message to buffer");
                memcpy(&(rxMessageBuffer[bufferLocation + sequenceSize * sequenceNumber]), &(tempBuf[i]), sequenceSize);
              } else {
                LError("Failed to add new rx message to array, rxMessageArray is full! Removing allocation in buffer");
                rxMessageBuffer.free(bufferLocation);
              }

            }

            //Send an ACK. Since the readyToSendBuffer only references data in other buffers, we will have a seperate ACK buffer
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

            //First, search for the relevant message in the txMessageArray by its
            //TODO this might have to be a critical section
            for (int i = 0; i < txMessageArray.size(); i++) {
              if (txMessageArray.get(i)[0] == messageNumber && txMessageArray.get(i)[1] == sequenceNumber) {
                LDebug("Found Message - Indicated ACK has been received");
                //we found the right message, so indicate the ack has been received
                txMessageArray.get(i)[7] |= 0b10000000;
              }
            }
          }
        }
      }

      //Now we have finished processing all possible messages that stem from teh current start byte. So, remove the start byte
      rxBuffer.dropFront(1); //NOTE it might be better to drop more than just one byte
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
        //TODO implement
      }

      //check if a message has expired
      if (diff((millis() / 1000) % 255, rxMessageArray.get(i)[8], 255) > 10) { //TODO should this be 256?
        LLog("Clearing message in RX buffer that has been around for 10 seconds");
        //since it expired, remove its allocation and clear it from the message array
        const uint16_t address = (rxMessageArray.get(i)[1] << 8) + rxMessageArray.get(i)[2]; 
        rxMessageBuffer.free(address);
        rxMessageArray.remove(i); 
      }
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
      const uint8_t sendCount = txMessageArray.get(i)[7] & 0b01111111;
      const uint16_t location = (txMessageArray.get(i)[2] << 8) + txMessageArray.get(i)[3];
      //If we've reached the max number of send attempts, drop the data all together
      if (sendCount > LORA_SEND_COUNT_MAX) {
        LDebug("Message has reached max send attempts, dropping from buffer");
        txMessageBuffer.free(location);
        txMessageArray.remove(i--); //decrement i so that we still iterate over all remaining entries
        continue;
      }

      //If it has been over a second since the previous send, try again //NOTE this 1s resent delay should probably be made shorter and controllable via a constant
      uint16_t lastSendTime = (txMessageArray.get(i)[3] << 8) + txMessageArray.get(i)[4];
      if (diff(millis() % 65535, lastSendTime, 65535) > 1000) {
        LDebug("Resending a message");
        lastSendTime = millis(); //NOTE - the time for CAD to occur is not accounted for in the resend functionality, which is a problem
        txMessageArray.get(i)[5] = lastSendTime >> 8;
        txMessageArray.get(i)[6] = lastSendTime & 0xFF;
        uint8_t tBuf[3];
        tBuf[0] = txMessageArray.get(i)[5]; //location high byte
        tBuf[1] = txMessageArray.get(i)[6]; //location low byte
        tBuf[2] = txMessageArray.get(i)[4]; //size
        if (readyToSendBuffer.pushBack(tBuf, 3)) {
          LDebug("Added message to ready to send buffer");
        } else {
          LError("Failed to add message to ready to send buffer because it was full");
        }
      }
    }
  }
  

  if (readyToSendBuffer.size() > 0 || ackToSendBuffer.size() > 0) {
    LDebug("One of the TX buffers has data, attempting to enter CAD Mode");
    enterChannelActivityDetectionMode();
  }

  //TODO need to write code to add code to the txMessageArray

  // ------------------------------------------------------------------------------------------------------------------------------------------


  // ------------------------------------------------------------- SERIAL HANDLING ---------------------------------------------------------------
  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer

  //test code to test sending::

  //
  
}

bool addMessageToTxArray(uint8_t* src, uint16_t size) {
  //TODO impl
  return false;
}

void enterChannelActivityDetectionMode() {
  //NOTE - we don't seem to have a way to check if an message is actively being received. Thus, we may accidentally kick the device out of RX mode while is message is transmitting.
  if (millis() > nextCADTime) {
    if (lastDeviceMode == RX_MODE || lastDeviceMode == IDLE_MODE || lastDeviceMode == SLEEP_MODE) {
      lastDeviceMode = CAD_MODE;
      LLog("Entering Channel Activity Detection Mode");
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
    LLog("Entering Receive Mode");
    LoRa.receive();
  }
}
void onCadDone(bool detectedSignal) {
  if (detectedSignal) {
    nextCADTime = MIN_CAD_WAIT_INTERVAL_MS * ((esp_random() % 10) + 1);
    lastDeviceMode = CAD_FAILED;
  } else {
    LoRa.beginPacket();
    if (readyToSendBuffer.size() > 0) {
      messageDispatched = true;
      uint8_t array[3];
      if (!readyToSendBuffer.peakFront(&(array[0]), 3)) {
        LError("Ready to send buffer reported data, but peak front failed!");
        HALT();
      }
      const uint16_t src = (array[0] << 8) + array[1];
      const uint16_t size = array[2];
      LoRa.write(&(txMessageBuffer[src]), size);
      LoRa.endPacket(true);
    } else if (ackToSendBuffer.size() > 0) {
      ackDispatched = true;
      uint8_t array[9];
      if (!ackToSendBuffer.peakFront(&(array[0]), 9)) {
        LError("Ack buffer reported data, but peak front failed!");
        HALT();
      }
      LoRa.write(&(array[0]), 9);
      LoRa.endPacket(true);
    } else {
      LError("Cad Finished with no data in either buffer!");
    }
    lastDeviceMode = TX_MODE;
  }
  return;
}
void onTxDone() {
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



