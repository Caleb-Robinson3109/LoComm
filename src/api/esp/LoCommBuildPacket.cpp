#include "LoCommBuildPacket.h"

void build_CACK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (CACK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = CACK_SIZE & 0xFF;

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
    computer_out_size = CACK_SIZE;
}

void build_PWAK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (PWAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = PWAK_SIZE & 0xFF;

    //CACK
    computer_out_packet[4] = 'P';
    computer_out_packet[5] = 'W';
    computer_out_packet[6] = 'A';
    computer_out_packet[7] = 'K';

    //tag 4 bytes, big-endian
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];
    computer_out_packet[10]  = computer_in_packet[10];
    computer_out_packet[11]  = computer_in_packet[11];

    //Status
    if(password_entered_flag){
        computer_out_packet[12]  = 'O';
        computer_out_packet[13]  = 'K';
        computer_out_packet[14]  = 'A';
        computer_out_packet[15]  = 'Y';
    }
    else{
        computer_out_packet[12]  = 'F';
        computer_out_packet[13]  = 'A';
        computer_out_packet[14]  = 'I';
        computer_out_packet[15]  = 'L';
    }

    //compute CRC of Message packet size + Type + Tag + message (14 bytes total)
    //crc >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    uint16_t crc = crc_16(&computer_out_packet[2], 14);
    computer_out_packet[16] = (crc >> 8) & 0xFF;
    computer_out_packet[17] = crc & 0xFF;

    //end bytes
    computer_out_packet[18] = 0x56;
    computer_out_packet[19] = 0x78;
    computer_out_size = PWAK_SIZE;
}

void build_DCAK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (DCAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = DCAK_SIZE & 0xFF;

    //CACK
    computer_out_packet[4] = 'D';
    computer_out_packet[5] = 'C';
    computer_out_packet[6] = 'A';
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
    computer_out_size = DCAK_SIZE;
}

void build_SPAK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (SPAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = SPAK_SIZE & 0xFF;

    //CACK
    computer_out_packet[4] = 'S';
    computer_out_packet[5] = 'P';
    computer_out_packet[6] = 'A';
    computer_out_packet[7] = 'K';

    //tag 4 bytes, big-endian
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];
    computer_out_packet[10]  = computer_in_packet[10];
    computer_out_packet[11]  = computer_in_packet[11];

    //Status
    if(set_password_flag){
        computer_out_packet[12]  = 'O';
        computer_out_packet[13]  = 'K';
        computer_out_packet[14]  = 'A';
        computer_out_packet[15]  = 'Y';
    }
    else{
        computer_out_packet[12]  = 'F';
        computer_out_packet[13]  = 'A';
        computer_out_packet[14]  = 'I';
        computer_out_packet[15]  = 'L';
    }

    //compute CRC of Message packet size + Type + Tag + message (14 bytes total)
    //crc >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    uint16_t crc = crc_16(&computer_out_packet[2], 14);
    computer_out_packet[16] = (crc >> 8) & 0xFF;
    computer_out_packet[17] = crc & 0xFF;

    //end bytes
    computer_out_packet[18] = 0x56;
    computer_out_packet[19] = 0x78;
    computer_out_size = SPAK_SIZE;
}

