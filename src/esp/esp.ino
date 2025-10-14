#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1


#define IDLE_MODE 1
#define RX_MODE 2
#define TX_MODE 3
#define CAD_MODE 4
#define CAD_FINISHED 5
#define SLEEP_MODE 0

//Libraries for LoRa
#include <SPI.h>
#include "LoRa.h"
#include "functions.h"

//Libraries for OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "esp.h"




uint8_t lastDeviceMode = 1;
uint32_t nextCADTime = 0;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

bool receiveReady = false;

CyclicArrayList<LORA_RX_BUFFER_SIZE> rxBuffer;

void setup() {
  //initialize variables
  rxBuffer = CyclicArrayList<LORA_RX_BUFFER_SIZE>();


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
  LoRa.idle();
}

void loop() {
  //Interrupt flags
  if (receiveReady) {
    int size = LoRa.available();
    receiveReady = false;
    
    //Dump the data into a temporary buffer
    uint8_t tempBuf[256];
    LoRa.readBytes(tempBuf, size);

    //Consider adding a debug check to see if there is still data in the buffer
    if (rxBuffer.pushBack(tempBuf, size)) {
      Serial.println("");
    } else {
      
    }

    //If there is room, add it to the end of the buffer
  }


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



