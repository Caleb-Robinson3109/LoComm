/*
This file contianes the helper functions that the other functions will use e.g. crc-16, message type chech, etc
*/

#ifndef LIB_H
#define LIB_H

#include "LoCommAPI.h"

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t

//for blinking debug stuff
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

//for hashing
#include "mbedtls/sha256.h"

//persistant storage (for password hash sotrage and keys)
#include <Preferences.h>


extern LiquidCrystal_I2C lcd;

void blinky1();
void blinky2();
void blinky(int blinks);

//Computues a crc-16 checksum
uint16_t crc_16(const uint8_t* data, size_t len);

//this checks a message to a string name
bool message_type_match(const uint8_t* mes, const char* str, size_t len);

//this function checks to see if there is a password hash being stored and if not it stores the default password hash
void init_password();

#endif