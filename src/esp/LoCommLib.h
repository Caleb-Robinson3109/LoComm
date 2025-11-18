/*
This file contianes the helper functions that the other functions will use e.g. crc-16, message type chech, etc
*/

#ifndef LIB_H
#define LIB_H

#include "LoCommAPI.h"
#include "globals.h"
//#include <string.h> //memcpy
#include "string.h" //memcpy

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t

//for blinking debug stuff
#include <Arduino.h>

//for hashing
#include "mbedtls/sha256.h"

//persistant storage (for password hash sotrage and keys)
#include <Preferences.h>


void blinky1();
void blinky2();
void blinky(int blinks);

//puts a SEND message in the device in packet and sets all the correct vars for that, so that we can test how to handle it
void debug_simulate_device_in_packet();

//Computues a crc-16 checksum
uint16_t crc_16(const uint8_t* data, size_t len);

//this checks a message to a string name
bool message_type_match(const uint8_t* mes, const char* str, size_t len);

//this function checks to see if there is a password hash being stored and if not it stores the default password hash
//handle the storge of the hash in memeory in the handle_CONN_packet  function 
void init_password();

//this function chechs the send ack to confirm that it is all good
bool check_SACK();

void displayName();

#endif