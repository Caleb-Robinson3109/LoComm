//Libraries for LoRa
#include <SPI.h>
#include <LoRa.h>

//Libraries for OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

//define the pins used by the LoRa transceiver module
#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26

//Frequency Band
#define BAND 915E6

//OLED pins
#define OLED_SDA 21
#define OLED_SCL 22 
#define OLED_RST -1
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

//packet counter
int lastSendTime = 0;
int byteCount = 0;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

void setup() {
  //initialize Serial Monitor
  Serial.begin(9600);

  //initialize OLED
  delay(1000);
  Serial.println("Beginning OLED Init");
  Serial.flush();
  
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false)) { 
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.drawPixel(10, 10, SSD1306_WHITE);
  display.setTextSize(1);
  
  
  Serial.println("Beginning LoRa Init");
  //Initialize LoRa device
  SPI.begin(SCK, MISO, MOSI, SS);
  //setup LoRa transceiver module
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(BAND)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("LoRa Initializing OK!");
  display.setCursor(0,10);
  display.print("LoRa Initializing OK!");
  display.display();
  Serial.println("Output to screen!");
  delay(2000);
  
}

//Notes for programming...

//Display - 
  //set cursor is used to place the cursor from the top left of the screen
  //display.setCursor(0,0);

  //Print is used to print text
  //display.print("LORA SENDER ");

  //Display is used to push the buffer to the screen itself
  //display.display();

//LoRa
  //Start a packet
  //LoRa.beginPacket();

  //Add data to the packet
  //LoRa.print("")
  
  //End a packet and send it out
  //LoRa.endPacket()

  //Try to receive a packet
  //LoRa.parsePacket(); //will return the length of the received packet. if its zero, then no packet was received
  
  //LoRa.available(); //true if a byte is available
  //LoRa.read(); //pop a byte of the packet
  //LoRa.packetRssi(); //read the rssi of the packet 

//


void loop() {
  if (millis() - lastSendTime > 10000) {
    lastSendTime = millis();
    LoRa.beginPacket();
    LoRa.print("meow");
    LoRa.endPacket(0);
    Serial.println("Sending Packet");
  }

  if (LoRa.parsePacket()) {
    Serial.println("Received Packet");
    display.setCursor(0, 0);
    while (LoRa.available()) {
      display.print(LoRa.read());
      byteCount++;
    }
    display.setCursor(0, 32);
    display.print(byteCount);
    display.display();
  }
}