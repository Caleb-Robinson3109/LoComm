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

const uint8_t default_password[32] = {'p', 'a', 's', 's', 'w', 'o', 'r', 'd',
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

uint8_t password_hash[32] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

    uint8_t password_ascii[32] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

Preferences storage;

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
    computer_in_size = serial_index;
    //lcd.setCursor(1,0);
    //lcd.print("size: ");
    //lcd.print(serial_index + 1);
}

void handle_message_from_computer(){
    //check start bytes
    lcd.setCursor(0,1);
    if(!(computer_in_packet[0] == 0x12 && computer_in_packet[1] == 0x34)){
        message_from_computer_flag = false;
        computer_in_size = 0;
        lcd.print("fbs error");
        return;
    }

    //check lenght
    uint16_t packet_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    if(packet_size != computer_in_size){
        message_from_computer_flag = false;
        computer_in_size = 0;
        lcd.print("size error");
        return;
    }

    //chech crc
    //use packet_size - 6 so we dont do the start and end bytes and crc itself
    uint16_t crc = crc_16(&computer_in_packet[2], packet_size - 6);
    uint8_t crc_high = (crc >> 8) & 0xFF;
    uint8_t crc_low  = crc & 0xFF;
    //if the 4th to last byte and 3rd to last byte (packet crc) of the computer in packet are not equal to our crc
    if(crc_high != computer_in_packet[packet_size - 4] || crc_low  != computer_in_packet[packet_size - 3]){
        message_from_computer_flag = false;
        computer_in_size = 0;
        lcd.print("crc error");
        return;
    }

    //check end bytes
    if(computer_in_packet[packet_size - 2] != 0x56 && computer_in_packet[packet_size - 1] != 0x78){
        message_from_computer_flag = false;
        computer_in_size = 0;
        lcd.print("lbs error");
        return;
    }

    //get the message type of the packet
    uint8_t message_type[4];
    for(int i = 0; i < 4; i++){
        message_type[i] = computer_in_packet[i+4];
        lcd.write(computer_in_packet[i+4]);

    }

    //the build_TYPE_packet will build in the device_out_packet[]
    if(message_type_match(message_type, "CONN", 4)){
        build_CACK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
    }

    if(message_type_match(message_type, "PASS", 4)){
        handle_PASS_packet();
        build_PWAK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
    }
}

void handle_message_to_computer(){
    Serial.write(computer_out_packet, computer_out_size);
    message_to_computer_flag = false;
    computer_out_size = 0;
}

void handle_PASS_packet(){
    //get the lenght of the password
    uint16_t password_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    password_size -= 16;

    //get the new password in the packet
    uint8_t new_password [32];

    for(int i = 0; i < packet_size; i++){
        new_password[i] = computer_in_packet[i + 12];
    }

    //fill in with 0x00 with any extra space
    for(int i = packet_size; i < 32; i++){
        new_password[i] = 0x00;
    }

    //set the new password
    memcpy(password_ascii, new_password, 32);
    mbedtls_sha256(new_password, 32, password_hash, 0);
    storage.putBytes("password", password_hash, 32);
}