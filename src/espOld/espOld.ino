//Libraries for LoRa
#include <SPI.h>
#include "LoRa.h"

//Libraries for OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "esp.h"

#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1
#define VBUF_SIZE 512

#define IDLE_MODE 1
#define RX_MODE 2
#define TX_MODE 3
#define CAD_MODE 4
#define CAD_FINISHED 5
#define SLEEP_MODE 0

//Since the LoRa library doesn't implement buffers at all, we will do them ourselves! The hope is that the TX buffer will have a write command the RX buffer will have a read command.
//To prevent unnecessary buffer reorgs, we will use a cyclic pattern where the start and then end of the data in the buffer cycles around as new messages are pushed/popped
uint8_t loraTxBuffer[LORA_TX_BUFFER_SIZE]; //format: length of data field, placeholder, data
uint32_t lTxBufferStart = 0; //points to the front of the buffer
uint32_t lTxBufferEnd = 0; //points to the end, at the first open position in the buffer

uint8_t loraRxBuffer[LORA_RX_BUFFER_SIZE]; //format: length of data field, rssi, data
uint32_t lRxBufferStart = 0;
uint32_t lRxBufferEnd = 0;

//The buffer is added to by placing and then incrementing the bufferEnd location, making sure it properly wraps around.
//The buffer is removed from by popping from and then incrementing the bufferStart location, making sure it properly also maps around
//Thus, if we pop out the full contents of the buffer, the start and end location should line up


//temporary buffer for various purposes
uint8_t vBuf[VBUF_SIZE];

uint32_t nextCADTime = 0;


uint8_t lastDeviceMode = IDLE_MODE;
uint8_t interruptFlag = 0;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

void setup() {
  //Initialize Serial Connection to Computer
  Serial.begin(9600);

  //Initialize OLED Screen
  delay(1000);
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false)) { 
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
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

  //interrupts();
  LoRa.idle();
  //LoRa.receive();

  //LoRa.beginPacket();
  //LoRa.print("a");
  //LoRa.endPacket(true);

  //delay(5000);
  //LoRa.channelActivityDetection();
  //delay(10000);
  //LoRa.sleep();
}

//TODO check the buffer reading logic

void loop() {
  static uint32_t mill = millis();
  if (mill + 1000 < millis()) {
    //LoRa.channelActivityDetection();
    mill = millis();
    Serial.printf("Current LoRa Operating Mode: %d\nCurrent IRQ Flag: %d\n", LoRa.readMode(), LoRa.readIrqFlag());
    
  }

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
  
  if (Serial.available()) {
    if (Serial.read()) {
      Serial.println("TEST: Attempting to write to TX Buffer");
      vBuf[0] = 1;
      vBuf[1] = 2;
      if (writeDataToLoraBuffer(vBuf, loraTxBuffer, 2, lTxBufferStart, lTxBufferEnd, LORA_TX_BUFFER_SIZE, 0)) {
        Serial.println("TEST: Wrote to tx buffer");
        Serial.printf("Tx buffer start is %d, tx buffer end is %d", lTxBufferStart, lTxBufferEnd);
        Serial.printf("Current mode: %d", lastDeviceMode);
        
        //delay(500);
        //LoRa.idle();
      } else {
        Serial.println("TEST: Failed to write to tx buffer!");
      }
    }
  }
  




  // --------------------------------------------------------------- LoRa MODE HANDLING ---------------------------------------------------------------


  //Run thru lora state logic
  if (lastDeviceMode == CAD_FINISHED) {
    handleSendMessage();
  }
  //if the lora tx buffer is empty...
  if (lTxBufferStart == lTxBufferEnd) {
    //go to receive mode
    enterReceiveMode();
  } else {
    //otherwise, begin the transmission process
    enterChannelActivityDetectionMode();
  }
  
}

void writeToTxBuffer(uint8_t* messageBuffer, uint16_t length) {
  Serial.println("Writing to the LoRa TX Buffer");
  if (length > 256) {
    Serial.println("Attempt to write 256+ byte message to buffer rejected");
  } else if (length == 0) {
    Serial.println("Attempt to write 0 byte message to buffer rejected");
  }

  if (writeDataToLoraBuffer(messageBuffer, loraTxBuffer, length, lTxBufferStart, lTxBufferEnd, LORA_TX_BUFFER_SIZE, 0)) {
    Serial.println("Wrote Message to LoRa TX Buffer");
  } else {
    Serial.println("Failed to write message to LoRa TX Buffer, buffer is full!");
  }
}

void readFromRxBuffer(uint8_t* dst) { //the entire message will be written into the dst, where the first byte is the length, the second is the -rssi, and the last is the data
  Serial.println("Attempting read from LoRa Rx buffer");
  uint16_t messageLength = loraRxBuffer[lRxBufferStart];
  if (messageLength == 0) messageLength = 256;
  //now we will read the next messageLength+2 bytes
  if (lRxBufferStart + messageLength > LORA_RX_BUFFER_SIZE){ //if the message loops around the end of the buffer...
    memcpy(dst, &(loraRxBuffer[lRxBufferStart]), sizeof(uint8_t) * (LORA_RX_BUFFER_SIZE - lRxBufferStart));
    memcpy(&(dst[LORA_RX_BUFFER_SIZE - lRxBufferStart]), loraRxBuffer, sizeof(uint8_t) * (messageLength - (LORA_RX_BUFFER_SIZE - lRxBufferStart)));
    lRxBufferStart = messageLength + lRxBufferStart - LORA_TX_BUFFER_SIZE;
  } else {
    memcpy(dst, &(loraRxBuffer[lRxBufferStart]), sizeof(uint8_t) * messageLength);
    lRxBufferStart += messageLength;
  }
  Serial.println("Read from LoRa RX Buffer");
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

void handleSendMessage() {
  Serial.println("Finished CAD");
  //if we dont detect a signal, then async send a message, and indicate we would like to lock the device into send mode
  if (detectedSignal) {
    //since we detected a signal, lets back off a random amount of time
    nextCADTime = MIN_CAD_WAIT_INTERVAL_MS * ((esp_random() % 10) + 1);
    LoRa.idle(); //go back to the idle state. NOTE - this may not be necessary
    //Serial.printf("Signal Detected when trying to send, waiting %lu MS before trying to send again", nextCADTime);
    lastDeviceMode = IDLE_MODE;
  } else {
    //no signal detected. Time to write directly from the tx buffer to save time
    LoRa.beginPacket();
    uint16_t messageLength = loraTxBuffer[lTxBufferStart++];
    if (messageLength == 0) messageLength = 256;
    if (++lTxBufferStart > LORA_TX_BUFFER_SIZE) lTxBufferStart = 0;
    if (lTxBufferStart + messageLength > LORA_TX_BUFFER_SIZE){ //if the message loops around the end of the buffer...
      LoRa.write(&(loraTxBuffer[lTxBufferStart]), LORA_TX_BUFFER_SIZE - lTxBufferStart);
      LoRa.write(loraTxBuffer, messageLength + lTxBufferStart - LORA_TX_BUFFER_SIZE);
      lTxBufferStart = messageLength + lTxBufferStart - LORA_TX_BUFFER_SIZE;
    } else {
      LoRa.write(&(loraTxBuffer[lTxBufferStart]), messageLength);
      lTxBufferStart += messageLength;
    }
    //now that the packet has been written, enter send mode to disable other callbacks until the message is dispatched
    lastDeviceMode = TX_MODE;
    LoRa.endPacket(true); //NOTE - this sets the callback to the onTxDone, so rec and cad callbacks wont trigger
    //Serial.println("Sending LoRa Message");
  }
}


void onTxDone() {
  //free the device on send mode
  return;
  lastDeviceMode = IDLE_MODE;
  LoRa.idle();
}

void onReceive(int size) {
  //TODO if the size is greater than the vBuf size, then we will have a buffer overflow! add an explicit check
  //dump the length of the packet, the rssi of the packet, and the packet itself into the rx buffer
  //whenever we dump a packet, we should move the variable indicating the end position of the rx buffer
  
  Serial.println("Attempting to read message from LoRa into rx buffer");
  
  //Now, pull the message into our volatile buffer so we can send it to the RX buffer
  LoRa.readBytes(vBuf,size);

  if (size > 256) {
    Serial.println("Received LoRa message larger than 256 bytes! ignoring!");
    lastDeviceMode = IDLE_MODE;
    LoRa.idle();
    return;
  }

  //Write the message to the rxBuffer
  if (writeDataToLoraBuffer(vBuf, loraRxBuffer, size, lRxBufferStart, lRxBufferEnd, LORA_RX_BUFFER_SIZE, LoRa.rssi())) {
    Serial.println("Wrote to RX Buffer!");
  } else {
    Serial.println("Write to LoRa RX Buffer failed! Buffer doesn't have enough space!");
  }

  lastDeviceMode = IDLE_MODE;
  LoRa.idle();
  return;
}

uint32_t getBufferSize(uint8_t* buffer, const uint32_t bufferSize, const uint32_t bufferStart, const uint32_t bufferEnd) {
  if (bufferStart == bufferEnd) {
    return bufferSize;
  }
  if (bufferStart < bufferEnd) { //if the buffer is currently not wrapped around...
    return bufferStart + (bufferSize - bufferEnd);
  } else {
    return bufferStart - bufferEnd;
  }
} 

bool writeDataToLoraBuffer(uint8_t *src, uint8_t *buffer, uint32_t size, uint32_t &bufferStart, uint32_t &bufferEnd, const uint32_t bufferSize, uint8_t rssi) {
  //first, make sure buffer has enough room
  if (getBufferSize(buffer, bufferSize, bufferStart, bufferEnd) < size + 2) {
    return false;
  }


  //first, write the size to the buffer
  if (bufferEnd == bufferSize) { //if the buffer is perfectly at the end, wrap around
    Serial.println("WARNING: Reached unexpected case where bufferEnd was equal to buffer size");
    buffer[0] = size;
    buffer[1] = rssi;
    bufferEnd = 2;
  } else if (bufferEnd == bufferSize - 1) {
    buffer[bufferEnd] = size;
    buffer[0] = rssi;
    bufferEnd = 1;
  } else if (bufferEnd == bufferSize - 2) {
    buffer[bufferEnd++] = size;
    buffer[bufferEnd++] = rssi;
    bufferEnd = 0;
  } else {
    buffer[bufferEnd++] = size;
    buffer[bufferEnd++] = rssi;
  }


  if (bufferSize - bufferEnd < size) { //if adding to the buffer would wrap it around...
    memcpy(&(buffer[bufferEnd]), src, sizeof(uint8_t) * (bufferSize - bufferEnd));
    memcpy(buffer, src, sizeof(uint8_t) * (size - (bufferSize - bufferEnd)));
    
    //LoRa.readBytes(&(loraRxBuffer[lRxBufferEnd]), LORA_RX_BUFFER_SIZE - lRxBufferEnd);
    //LoRa.readBytes(loraRxBuffer, size - (LORA_RX_BUFFER_SIZE - lRxBufferEnd));
    bufferEnd = size - (bufferSize - bufferEnd);
  } else { //otherwise, just write the whole message
    memcpy(&(buffer[bufferEnd]), src, size);
    //LoRa.readBytes(&(loraRxBuffer[lRxBufferEnd]), size);
    bufferEnd += size;
  }

  if (bufferEnd == bufferSize) bufferEnd = 0;
  return true;
}