/*
This file contianes the functions that build the packets like SACK, SEND, PACK, etc
*/

#ifndef BUILD_PACKET_H
#define BUILD_PACKET_H

#include "LoCommAPI.h"
#include "LoCommLib.h"

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t

#define CACK_SIZE 16
#define PWAK_SIZE 20
#define DCAK_SIZE 16
#define SPAK_SIZE 20

//builds the CACK (send ack) packet
void build_CACK_packet();

//pass word ack
void build_PWAK_packet();

//disconnect ack
void build_DCAK_packet();

//set password ack
void build_SPAK_packet();

#endif