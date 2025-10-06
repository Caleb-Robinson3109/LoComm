#pragma once

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

void enterChannelActivityDetectionMode();
void enterReceiveMode();
void onCadDone(bool detectedSignal);
void onTxDone();
void onReceive(int size);
