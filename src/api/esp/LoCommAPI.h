#ifndef API_H
#define API_H

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t

#define MAX_COMPUTER_PACKET_SIZE 100
#define MAX_DEVICE_PACKET_SIZE 100

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
extern bool message_for_computer_flag;
//flag for if there is a message from the device to be processed
extern bool message_from_device_flag;
//flag for if there is a message for the device to be sent out
extern bool message_for_device_flag;

//Computues a crc-16 checksum
uint16_t crc_16(const uint8_t* data, size_t len);

//builds the SACK (send ack) packet
bool build_SACK_packet(uint8_t* packet, uint32_t tag);

//This function waits for 1 sec and if there is no message to be recived from the computer continues
//if there is a message it sets the message_from_computer_flag to true, and stores the message in the computer_in_packet buf
void recive_packet_from_computer();

void clear_buf(uint8_t* buf, size_t buf_size);

#endif