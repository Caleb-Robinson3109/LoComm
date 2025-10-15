/*
This file contianes the helper functions that the other functions will use e.g. crc-16, message type chech, etc
*/

#ifndef LIB_H
#define LIB_H

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t

//for blinking debug stuff
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

extern LiquidCrystal_I2C lcd;

void blinky1();
void blinky2();
void blinky(int blinks);

//Computues a crc-16 checksum
uint16_t crc_16(const uint8_t* data, size_t len);

//this checks a message to a string name
bool message_type_match(const uint8_t* mes, const char* str, size_t len);


#endif