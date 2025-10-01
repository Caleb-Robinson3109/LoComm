//Libraries for LoRa
#include <SPI.h>
#include <LoRa.h>

//Libraries for OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1

#define IDLE_MODE 1
#define RX_MODE 2
#define TX_MODE 3
#define CAD_MODE 4

uint8_t loraTxBuffer[LORA_TX_BUFFER_SIZE]; //format: length, data
uint32_t lTxBufferStart = 0; //points to the front of the buffer
uint32_t lTxBufferEnd = 0; //points to the end, at the first open position in the buffer

uint8_t loraRxBuffer[LORA_RX_BUFFER_SIZE]; //format: length (not including data), rssi, data
uint32_t lRxBufferStart = 0;
uint32_t lRxBufferEnd = 0;

uint32_t nextCADTime = 0;


uint8_t lastDeviceMode = IDLE_MODE;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  //TODO register all callbacks
  //TODO figure out what initial state we should use for the LoRa
}

//TODO go thru all conditionals and make sure we are using the correct < <= or > >=
//TODO check all buffer logic

void loop() {
  // --------------------------------------------------------------- SERIAL HANDLING ---------------------------------------------------------------
  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer


  // --------------------------------------------------------------- LoRa MODE HANDLING ---------------------------------------------------------------

  if (lTxBufferStart != lTxBufferEnd) { //if there is data in the tx buffer...
    //try to enter activity detection mode
    enterChannelActivityDetectionMode();
  } else {
    //otherwise, go to receive mode
    enterReceiveMode();
  }
  
}

void writeToTxBuffer(uint8_t* buffer, uint16_t length) {

}

void enterChannelActivityDetectionMode() {
  //NOTE - we don't seem to have a way to check if an message is actively being received. Thus, we may accidentally kick the device out of RX mode while is message is transmitting.
  if (millis() > nextCADTime) {
    if (lastDeviceMode == RX_MODE || lastDeviceMode == IDLE_MODE) {
      lastDeviceMode = CAD_MODE;
      LoRa.channelActivityDetection(); //NOTE - this sets the callback to the CAD callback, so rec and txdone callbacks wont trigger
    }
  }
}

void enterReceiveMode() {
  //Under normal flow, if a message is added to the send buffer, the device will go to CAD mode, then to TX mode, and then to IDLE mode. from there, we can reenter rec mode
  if (lastDeviceMode == IDLE_MODE) {
    lastDeviceMode = RX_MODE;
    LoRa.receive(); //NOTE - this sets the callback to the REC callback, so cad and txdone callbacks wont trigger
  }
}


void onCadDone(bool detectedSignal) {
  //if we dont detect a signal, then async send a message, and indicate we would like to lock the device into send mode
  if (detectedSignal) {
    //since we detected a signal, lets back off a random amount of time
    nextCADTime = MIN_CAD_WAIT_INTERVAL_MS * ((esp_random() % 10) + 1);
    idle(); //go back to the idle state. NOTE - this may not be necessary
    lastDeviceMode = IDLE_MODE;
  } else {
    //not signal detected. Time to write!
    LoRa.beginPacket();
    uint8_t messageLength = loraTxBuffer[lTxBufferStart];
    if (lTxBufferStart + messageLength > LORA_TX_BUFFER_SIZE){ //if the message loops around the end of the buffer...
      LoRa.write(&(loraTxBuffer[lTxBufferStart]), LORA_TX_BUFFER_SIZE - lTxBufferStart);
      LoRa.write(loraTxBuffer, messageLength + lTxBufferStart - LORA_TX_BUFFER_SIZE);
      lTxBufferStart = messageLength + lTxBufferStart - LORA_TX_BUFFER_SIZE;
    } else {
      LoRa.write(&(loraTxBuffer[lTxBufferStart]), messageLength);
      lTxBufferStart += messageLength;
    }
    //now that the packet has been written, enter send mode!
    lastDeviceMode = TX_MODE;
    LoRa.endPacket(true); //NOTE - this sets the callback to the onTxDone, so rec and cad callbacks wont trigger
  }
}

void onTxDone() {
  //free the device on send mode
  lastDeviceMode = IDLE_MODE;
  idle();
}

void onReceive(int size) {
  //dump the length of the packet, the rssi of the packet, and the packet itself into the rx buffer
  //whenever we dump a packet, we should move the variable indicating the end position of the rx buffer
  
  //First, make sure we have enough space in the buffer
  uint32_t remainingBufferSize;
  if (lRxBufferStart <= lRxBufferEnd) { //if the buffer is currently not wrapped around...
    remainingBufferSize = lRxBufferStart + (LORA_RX_BUFFER_SIZE - lRxBufferEnd);
  } else {
    remainingBufferSize = lRxBufferStart - lRxBufferEnd;
  }

  if (size + 2 > remainingBufferSize) { //if the message would overflow the buffer, ignore it
    lastDeviceMode = IDLE_MODE;
    idle();
    return;
  }

  //Write the message to the buffer
  if (LORA_RX_BUFFER_SIZE - lRxBufferEnd < size + 2) { //if adding to the buffer would wrap it around...
    //TODO need to do some additional checking for those first two bits
    
    LoRa.readBytes(&(loraRxBuffer[lRxBufferEnd]), LORA_RX_BUFFER_SIZE - lRxBufferEnd);
    
    memcpy(&(loraRxBuffer[lRxBufferEnd]),   )
  }

  //return in idle mode
}

//void writeToBuffer(uint8_t *buffer, uint32_t *bufferStart, uint32_t *bufferEnd, const uint32_t bufferSize, const)
