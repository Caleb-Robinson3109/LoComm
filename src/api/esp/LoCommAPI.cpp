#include "LoCommAPI.h"

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
size_t computer_in_size = 0;
size_t device_in_size = 0;

void recive_packet_from_computer(){
    size_t serial_index = 0;
    delay(1000);
    if(Serial.available() == 0){
        return;
    }
    lcd.clear();
    lcd.setCursor(0,0);
    while(Serial.available() > 0 && serial_index < MAX_COMPUTER_PACKET_SIZE){
        lcd.write(computer_in_packet[serial_index]);
        computer_in_packet[serial_index++] = Serial.read();
        delay(100);
    }
    message_from_computer_flag = true;
    //set the lenght of the incommed packet
    computer_in_size = serial_index + 1;
}

void handle_message_from_computer(){
    //check start bytes
    if(!(computer_in_packet[0] == 0x12 && computer_in_packet[1] == 0x34)){
        message_from_computer_flag = false;
        computer_in_size = 0;
        return;
    }

    //check lenght
    uint16_t packet_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    if(packet_size != computer_in_size){
        message_from_computer_flag = false;
        computer_in_size = 0;
        return;
    }

    //chech crc
    //use packet_size - 4 so we dont do the start and end bytes
    uint16_t crc = crc_16(&computer_in_packet[2], packet_size - 4);
    //if the 4th to last byte and 3rd to last byte (packet crc) of the computer in packet are not equal to our crc
    if(!((((crc << 8) & 0xFF) == computer_in_packet[packet_size - 4]) && ((crc & 0xFF) == computer_in_packet[packet_size - 3]))){
        message_from_computer_flag = false;
        computer_in_size = 0;
        return;
    }

    //check end bytes
    if(computer_in_packet[packet_size - 2] != 0x56 && computer_in_packet[packet_size - 1] != 0x78){
        message_from_computer_flag = false;
        computer_in_size = 0;
        return;
    }

    //get the message type of the packet
    uint8_t message_type[4];
    for(int i = 0; i < 4; i++){
        message_type[i] = computer_in_packet[i+4];
    }

    //the build_TYPE_packet will build in the device_out_packet[]
    if(message_type_match(message_type, "CONN", 4)){
        build_SACK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
    }
}

void handle_message_to_computer(){
    Serial.write(computer_out_packet, computer_out_size);
    message_to_computer_flag = false;
    computer_out_size = 0;
}

