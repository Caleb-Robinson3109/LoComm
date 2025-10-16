/*
This file contianes the functions that hande the state of the device to computer communcation
*/

#ifndef API_H
#define API_H

#include "LoCommBuildPacket.h"
#include "LoCommLib.h"

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t
#include <Arduino.h> //delay, ...
//persistant storage (for password hash sotrage and keys)
#include <Preferences.h>
#include <string.h> //memcpy
#include "mbedtls/sha256.h" // sha256

#define MAX_COMPUTER_PACKET_SIZE 100
#define MAX_DEVICE_PACKET_SIZE 100
#define MESSAGE_TYPE_SIZE 4
#define PASSWORD_SIZE 32

//a place to store the packet that has come from the computer
extern uint8_t computer_in_packet[MAX_COMPUTER_PACKET_SIZE];
//a place to store the packet that will be going to the computer
extern uint8_t computer_out_packet[MAX_COMPUTER_PACKET_SIZE];
//a place to store the packet that has come in from the device
extern uint8_t device_in_packet[MAX_DEVICE_PACKET_SIZE];
//a place to store the packet that will be going out from the device
extern uint8_t device_out_packet[MAX_DEVICE_PACKET_SIZE];

//flag for if there is a message from the computer to be processed
extern bool message_from_computer_flag;
//flag for if there is a message for the computer to be sent 
extern bool message_to_computer_flag;
//flag for if there is a message from the device to be processed
extern bool message_from_device_flag;
//flag for if there is a message for the device to be sent out
extern bool message_to_device_flag;
//if the correct password is put in then we put the flag to true
extern bool password_entered_flag;

//this is the size of the packet going out to the computer 
extern size_t computer_out_size;
//this is the size of the packet going out to the other device
extern size_t device_out_size;
//this is the size of the computer incomming packet
extern size_t computer_in_size;
//this is the size of the incomming device packet
extern size_t device_in_size;

//this is the defalt password
extern const uint8_t default_password[32];

//this is where the password hash is held the default is the hash of password
extern uint8_t password_hash[32];

//this is used to encript the keys. also good to have it stored on the device (volitile)
extern uint8_t password_ascii[32];

//this is the storage that will be used to store the password hash and the keys
extern Preferences storage;

//This function waits for 1 sec and if there is no message to be recived from the computer continues
//if there is a message it sets the message_from_computer_flag to true, and stores the message in the computer_in_packet buf
void recive_packet_from_computer();

//this funcion if we see that the message from computer flag is high then call this function. it "answers" message, sending out a message to the device out buf if needed
//setting the approprate flags to handle the message
void handle_message_from_computer();

//this functions handles the message that is in the computer out buf sending it to the computer
void handle_message_to_computer();

//this handles a incomming PASS packet and changes the password on the device
void handle_PASS_packet();

//this handles an incomming DCON packet, overwritting the password from memory
void handle_DCON_packet();

#endif