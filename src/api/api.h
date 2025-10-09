#ifndef API_H
#define API_H

#include <arduino.h>

#define MAX_PACKET_SIZE 100

//Computues a crc-16 checksum
uint_16 crc_16(const uint_8* data, size_t len);

//builds the SACK (send ack) packet
bool build_SACK_packet(uint_8* packet, uint_32 tag);

//TODO create a time out, so that the processes has a chance to check for other work. Because this process will handle comm bewteen bevice and computer it needs to check for messages to send to the computer too
void recive_packet_from_app()

#endif