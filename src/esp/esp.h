#pragma once

//define the pins used by the LoRa transceiver module
#define SCK_LORA 5
#define MISO_LORA 19
#define MOSI_LORA 27
#define SS_LORA 18
#define RST_LORA 14
#define DIO0_LORA 26

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
