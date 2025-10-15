#include "LoCommBuildPacket.h"

void build_SACK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    uint16_t packet_size = 16;
    computer_out_packet[2] = (packet_size >> 8) & 0xFF; 
    computer_out_packet[3] = packet_size & 0xFF;

    //CACK
    computer_out_packet[4] = 'S';
    computer_out_packet[5] = 'A';
    computer_out_packet[6] = 'C';
    computer_out_packet[7] = 'K';

    //tag 4 bytes, big-endian
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];
    computer_out_packet[10]  = computer_in_packet[10];
    computer_out_packet[11]  = computer_in_packet[11];

    //compute CRC of Message packet size + Type + Tag (10 bytes total)
    //crc >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    uint16_t crc = crc_16(&computer_out_packet[2], 10);
    computer_out_packet[12] = (crc >> 8) & 0xFF;
    computer_out_packet[13] = crc & 0xFF;

    //end bytes
    computer_out_packet[14] = 0x56;
    computer_out_packet[15] = 0x78;
    computer_out_size = 16;
}