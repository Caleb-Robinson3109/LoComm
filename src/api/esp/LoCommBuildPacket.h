/*
This file contianes the functions that build the packets like SACK, SEND, PACK, etc
*/

#ifndef BUILD_PACKET_H
#define BUILD_PACKET_H

#include "LoCommAPI.h"
#include "LoCommLib.h"

#include <stdint.h> //uint8_t, uint32_t, ...
#include <stddef.h> //size_t

//builds the SACK (send ack) packet
void build_CACK_packet();

//pass word ack
void build_PWAK_packet();

#endif