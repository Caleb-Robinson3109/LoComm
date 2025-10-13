#include "LoCommAPI.h"



extern bool message_from_computer_flag = false;
extern bool message_for_computer_flag = false;
extern bool message_from_device_flag = false;
extern bool message_for_device_flag = false;

uint_16 crc_16(const uint_8* data, size_t len){
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000)
            crc = (crc << 1) ^ 0x1021;
            else
            crc <<= 1;
        }
    }
    return crc;   
}

bool build_SACK_packet(uint_8* packet, size_t packet_size, uint_32 tag){
    //check the lenght of the packet buf
    if(packet_size != 14){
        return false;
    }

    //start bytes
    packet[0] = 0x12;
    packet[1] = 0x34;

    //CACK
    packet[2] = 'C';
    packet[3] = 'A';
    packet[4] = 'C';
    packet[5] = 'K';

    //tag 4 bytes, big-endian
    //tag >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    packet[6]  = (tag >> 24) & 0xFF;
    packet[7]  = (tag >> 16) & 0xFF;
    packet[8]  = (tag >> 8) & 0xFF;
    packet[9]  = (tag) & 0xFF;

    //compute CRC of Message Type + Tag (8 bytes total)
    uint16_t crc = crc_16(&packet[2], 8);
    packet[10] = (crc >> 8) & 0xFF;
    packet[11] = crc & 0xFF;

    //end bytes
    packet[12] = 0x56;
    packet[13] = 0x78;

    return true;
}

void recive_packet_from_computer(){

}

void clear_buf(*uint8_t buf, size_t buf_size){
    
}