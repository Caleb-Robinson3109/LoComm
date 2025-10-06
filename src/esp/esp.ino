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
  LoRa.idle();
}

//TODO check all buffer logic

void loop() {
  // --------------------------------------------------------------- SERIAL HANDLING ---------------------------------------------------------------
  //check for data on the serial rx buffer
  
  //if the data makes a message, handle the messages

  //if there is something to send over serial, write to the tx buffer


  // --------------------------------------------------------------- LoRa MODE HANDLING ---------------------------------------------------------------

  //if the lora tx buffer is empty...
  if (lTxBufferStart + 1 == lTxBufferEnd || (lTxBufferStart == LORA_TX_BUFFER_SIZE - 1 && lTxBufferEnd == 0)) { 
    //go to receive mode
    enterReceiveMode();
  } else {
    //otherwise, begin the transmission process
    enterChannelActivityDetectionMode();
  }
  
}

void writeToTxBuffer(uint8_t* buffer, uint16_t length) {
  if (length > 256) {
    Serial.println("Attempt to write 256+ byte message to buffer rejected");
  } else if (length == 0) {
    Serial.println("Attempt to write 0 byte message to buffer rejected");
  }

  //TODO Finish
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
    LoRa.idle(); //go back to the idle state. NOTE - this may not be necessary
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
  LoRa.idle();
}

void onReceive(int size) {
  //TODO ensure size < 256
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
    LoRa.idle();
    return;
  }

  //handle getting the first two bytes written first (size, RSSI)
  loraRxBuffer[lRxBufferEnd++] = size;
  if (lRxBufferEnd >= LORA_RX_BUFFER_SIZE) { //if there is no room left in the buffer, then place the two bytes at the start of the buffer and set the new buffer end
    loraRxBuffer[0] = size;
    loraRxBuffer[1] = (-1) * LoRa.packetRssi();
    lRxBufferEnd = 2;
  } else if (lRxBufferEnd = LORA_RX_BUFFER_SIZE - 1) { //if theres only room for one
    loraRxBuffer[LORA_RX_BUFFER_SIZE - 1] = size;
    loraRxBuffer[0] = (-1) * LoRa.packetRssi();
    lRxBufferEnd = 1;
  } else {
    loraRxBuffer[lRxBufferEnd++] = size;
    loraRxBuffer[lRxBufferEnd++] = LoRa.packetRssi();
  }

  //Write the message to the buffer
  if (LORA_RX_BUFFER_SIZE - lRxBufferEnd < size) { //if adding to the buffer would wrap it around...
    LoRa.readBytes(&(loraRxBuffer[lRxBufferEnd]), LORA_RX_BUFFER_SIZE - lRxBufferEnd);
    LoRa.readBytes(loraRxBuffer, size - (LORA_RX_BUFFER_SIZE - lRxBufferEnd));
    lRxBufferEnd = size - (LORA_RX_BUFFER_SIZE - lRxBufferEnd);
  } else { //otherwise, just write the whole message
    LoRa.readBytes(&(loraRxBuffer[lRxBufferEnd]), size);
    lRxBufferEnd += size;
  }

  lastDeviceMode = IDLE_MODE;
  LoRa.idle();
  return;
}

//void writeToBuffer(uint8_t *buffer, uint32_t *bufferStart, uint32_t *bufferEnd, const uint32_t bufferSize, const)
