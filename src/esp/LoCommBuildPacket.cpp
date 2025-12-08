#include "LoCommBuildPacket.h"

void build_CACK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (CACK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = CACK_SIZE & 0xFF;

    //CACK
    computer_out_packet[4] = 'C';
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

    //PWAK
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

void build_SACK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (SACK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = SACK_SIZE & 0xFF;

    //SACK
    computer_out_packet[4] = 'S';
    computer_out_packet[5] = 'A';
    computer_out_packet[6] = 'C';
    computer_out_packet[7] = 'K';

    //tag 4 bytes, big-endian
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];
    computer_out_packet[10]  = computer_in_packet[10];
    computer_out_packet[11]  = computer_in_packet[11];

    //message - the chuck #
    computer_out_packet[12] = computer_in_packet[15];
    computer_out_packet[13] = computer_in_packet[16];

    //compute CRC of Message packet size + Type + Tag (10 bytes total)
    //crc >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    uint16_t crc = crc_16(&computer_out_packet[2], 12);
    computer_out_packet[14] = (crc >> 8) & 0xFF;
    computer_out_packet[15] = crc & 0xFF;

    //end bytes
    computer_out_packet[16] = 0x56;
    computer_out_packet[17] = 0x78;
    computer_out_size = SACK_SIZE;
}

void build_SNAK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (SNAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = SNAK_SIZE & 0xFF;

    //CACK
    computer_out_packet[4] = 'S';
    computer_out_packet[5] = 'N';
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
    computer_out_size = SNAK_SIZE;
}


void build_EPAK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (EPAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = EPAK_SIZE & 0xFF;

    //ePAK
    computer_out_packet[4] = 'E';
    computer_out_packet[5] = 'P';
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
    computer_out_size = EPAK_SIZE;
}

void build_SCAK_packet(){
     //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (SCAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = SCAK_SIZE & 0xFF;

    //SCAK
    computer_out_packet[4] = 'S';
    computer_out_packet[5] = 'C';
    computer_out_packet[6] = 'A';
    computer_out_packet[7] = 'K';

    //tag 4 bytes, big-endian
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];
    computer_out_packet[10]  = computer_in_packet[10];
    computer_out_packet[11]  = computer_in_packet[11];

    //the bytes of the aviables devies 32 is the table size
    for(int i = 0; i < 32; i++){
        computer_out_packet[i + 12] = deviceIDList[i];
    }

    //compute CRC of Message packet size + Type + Tag (10 bytes total)
    //crc >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    uint16_t crc = crc_16(&computer_out_packet[2], 42);
    computer_out_packet[44] = (crc >> 8) & 0xFF;
    computer_out_packet[45] = crc & 0xFF;

    //end bytes
    computer_out_packet[46] = 0x56;
    computer_out_packet[47] = 0x78;
    computer_out_size = SCAK_SIZE;
   
}

void build_GPAK_packet(){
     //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //packet size
    computer_out_packet[2] = (SCAK_SIZE >> 8) & 0xFF; 
    computer_out_packet[3] = SCAK_SIZE & 0xFF;

    //SCAK
    computer_out_packet[4] = 'G';
    computer_out_packet[5] = 'P';
    computer_out_packet[6] = 'A';
    computer_out_packet[7] = 'K';

    //tag 4 bytes, big-endian
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];
    computer_out_packet[10]  = computer_in_packet[10];
    computer_out_packet[11]  = computer_in_packet[11];

    if(sec_isPaired()){
       
        char key_buf[21];
        bool okay = sec_display_key(&key_buf[0], 21);
        if(okay){ 
            computer_out_packet[12] = 0xFF;
            for(int i = 0; i < 20; i++){
                computer_out_packet[12 + i] = key_buf[i];
            }
        }
        else{
            computer_out_packet[12] = 0x00;
        } 
    }
    else{
        computer_out_packet[12] = 0x00;
    }

    //compute CRC of Message packet size + Type + Tag (10 bytes total)
    //crc >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    uint16_t crc = crc_16(&computer_out_packet[2], 31);
    computer_out_packet[33] = (crc >> 8) & 0xFF;
    computer_out_packet[34] = crc & 0xFF;

    //end bytes
    computer_out_packet[35] = 0x56;
    computer_out_packet[36] = 0x78;
    computer_out_size = GPAK_SIZE;  
}