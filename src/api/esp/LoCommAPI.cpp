#include "LoCommAPI.h"
#include "blinky.h"
#include <LiquidCrystal_I2C.h>

uint8_t computer_in_packet[MAX_COMPUTER_PACKET_SIZE];
uint8_t computer_out_packet[MAX_COMPUTER_PACKET_SIZE];
uint8_t device_in_packet[MAX_DEVICE_PACKET_SIZE];
uint8_t device_out_packet[MAX_DEVICE_PACKET_SIZE];
bool message_from_computer_flag = false;
bool message_to_computer_flag = false;
bool message_from_device_flag = false;
bool message_to_device_flag = false;
size_t computer_out_size = 0;
size_t device_out_size = 0;

uint16_t crc_16(const uint8_t* data, size_t len){
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

void build_SACK_packet(){
    //start bytes
    computer_out_packet[0] = 0x12;
    computer_out_packet[1] = 0x34;

    //CACK
    computer_out_packet[2] = 'S';
    computer_out_packet[3] = 'A';
    computer_out_packet[4] = 'C';
    computer_out_packet[5] = 'K';

    //tag 4 bytes, big-endian
    //tag >> x bit shifts the tag by a byte 2, 3 to isolate the correct byte. x & 0xFF ensures that it is only one byte
    computer_out_packet[6]  = computer_in_packet[6];
    computer_out_packet[7]  = computer_in_packet[7];
    computer_out_packet[8]  = computer_in_packet[8];
    computer_out_packet[9]  = computer_in_packet[9];

    //compute CRC of Message Type + Tag (8 bytes total)
    uint16_t crc = crc_16(&computer_out_packet[2], 8);
    computer_out_packet[10] = (crc >> 8) & 0xFF;
    computer_out_packet[11] = crc & 0xFF;

    //end bytes
    computer_out_packet[12] = 0x56;
    computer_out_packet[13] = 0x78;
    computer_out_size = 14;
}

void recive_packet_from_computer(){
    size_t serial_index = 0;
    delay(1000);
    if(Serial.available() == 0){
        return;
    }
    //blinky(Serial.available());
    while(Serial.available() > 0 && serial_index < MAX_COMPUTER_PACKET_SIZE){
        computer_in_packet[serial_index++] = Serial.read();
        //blinky(2);
    }
    message_from_computer_flag = true;
}

void handle_message_from_computer(){
    //start bytes failed
    if(!(computer_in_packet[0] == 0x12 && computer_in_packet[1] == 0x34)){
        message_from_computer_flag = false;
        return;
    }

    //check end bytes

    //check lenght

    //chech crc

    //more checks

    //get the message type of the packet
    uint8_t message_type[4];
    for(int i = 0; i < 4; i++){
        message_type[i] = computer_in_packet[i+2];
    }

    //the build_TYPE_packet will build in the device_out_packet[]
    //blinky(2);
    //delay(1000);
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print((char*)message_type);
    if(message_type_match(message_type, "CONN", 4)){
        //blinky(5);
        build_SACK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
        //lcd.clear();
        //lcd.setCursor(0, 0);
        //lcd.print("mtcf :() - ");                     // Use print for strings
        //lcd.print((int)message_to_computer_flag); // Use print for numbers
        //delay(305);
        //blinky(4);
    }
}

void handle_message_to_computer(){
    Serial.write(computer_out_packet, computer_out_size);
    message_to_computer_flag = false;
    computer_out_size = 0;
}

bool message_type_match(const uint8_t* buf, const char* str, size_t len){
    for (size_t i = 0; i < len; i++) {
        /*
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("buf: ");
        lcd.write((char)buf[i]);   // show byte as character
        lcd.print("  str: ");
        lcd.print(str[i]);         // show matching char
        delay(700);
        */
        if (buf[i] != (uint8_t)str[i]) {
            return false;
        }
    }
    return true;
}

//void clear_buf(*uint8_t buf, size_t buf_size){