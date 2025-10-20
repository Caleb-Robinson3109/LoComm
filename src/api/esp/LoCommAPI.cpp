#include "LoCommAPI.h"

uint8_t computer_in_packet[MAX_COMPUTER_PACKET_SIZE];
uint8_t computer_out_packet[MAX_COMPUTER_PACKET_SIZE];
uint8_t device_in_packet[MAX_DEVICE_PACKET_SIZE];
uint8_t device_out_packet[MAX_DEVICE_PACKET_SIZE];
bool message_from_computer_flag = false;
bool message_to_computer_flag = false;
bool message_from_device_flag = false;
bool message_to_device_flag = false;
bool password_entered_flag = false;
bool set_password_flag = false;
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
    //lcd.clear();
    //lcd.setCursor(0,0);
    //lcd.print("read");
    while(Serial.available() > 0 && serial_index < MAX_COMPUTER_PACKET_SIZE){
        computer_in_packet[serial_index++] = Serial.read();
        //lcd.setCursor(6,0);
        //lcd.print(serial_index);
    }
    //lcd.setCursor(0,0);
    //lcd.print("done");
    message_from_computer_flag = true;
    //set the lenght of the incommed packet
    computer_in_size = serial_index;
}

void handle_message_from_computer(){
    //check start bytes
    lcd.setCursor(0,1);
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
    //use packet_size - 6 so we dont do the start and end bytes and crc itself
    uint16_t crc = crc_16(&computer_in_packet[2], packet_size - 6);
    uint8_t crc_high = (crc >> 8) & 0xFF;
    uint8_t crc_low  = crc & 0xFF;
    //if the 4th to last byte and 3rd to last byte (packet crc) of the computer in packet are not equal to our crc
    if(crc_high != computer_in_packet[packet_size - 4] || crc_low  != computer_in_packet[packet_size - 3]){
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
    if(message_type_match(message_type, "CONN", MESSAGE_TYPE_SIZE)){
        build_CACK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
    }

    else if(message_type_match(message_type, "PASS", MESSAGE_TYPE_SIZE)){
        handle_PASS_packet();
        build_PWAK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
    }

    else if(message_type_match(message_type, "DCON", MESSAGE_TYPE_SIZE)){
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("DCON - ");
        lcd.print((char*)password_ascii);
        //delay(2000);
        handle_DCON_packet();
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print((char*)password_ascii);
        build_DCAK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
        lcd.setCursor(0,1);
        //delay(200);
    }

    else if(message_type_match(message_type, "STPW", MESSAGE_TYPE_SIZE)){
        handle_STPW_packet();
        build_SPAK_packet();
        message_to_computer_flag = true;
        message_from_computer_flag = false;
    }
}

void handle_message_to_computer(){
    lcd.clear();
    lcd.setCursor(0,0);
    for(int i = 0; i < 16; i++){
        lcd.write(computer_out_packet[i]);
    }
    lcd.setCursor(0,1);
    lcd.print("out packet");
    delay(2000);
    Serial.write(computer_out_packet, computer_out_size);
    message_to_computer_flag = false;
    computer_out_size = 0;
}

void handle_PASS_packet(){
    //get the lenght of the password
    uint16_t password_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    password_size -= 16;
    uint8_t input_password_hash[32];

    //get the new password in the packet
    uint8_t input_password [32];

    for(int i = 0; i < password_size; i++){
        input_password[i] = computer_in_packet[i + 12];
    }

    //fill in with 0x00 with any extra space
    for(int i = password_size; i < 32; i++){
        input_password[i] = 0x00;
    }

    //get the password hash stored in storage and check it aginst the enterne password.
    //if the password is corrext store it and set the passowrd flag
    mbedtls_sha256(input_password, 32, input_password_hash, 0);
    if(memcmp(input_password_hash, password_hash, 32) == 0){
        memcpy(password_ascii, input_password, 32);
        password_entered_flag = true;
    }
    else{
        password_entered_flag = false;
    }
}

void handle_DCON_packet(){
    // overwrites the password and the password hash with 0x00
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("clearing passes");
    for(int i = 0; i < PASSWORD_SIZE; i++){
        password_ascii[i] = 0x00;
        password_hash[i] = 0x00;
    }
    lcd.setCursor(0,1);
    lcd.print("done - del pass");
    //delay(2000);
    //TODO eventuall the key with 0x00 
}

void handle_STPW_packet(){
    uint8_t old_password[32];
    uint8_t old_size = computer_in_packet[12];

    //get the old password and set the blank bytes to 0x00
    for(int i = 0; i < old_size; i++){
        old_password[i] = computer_in_packet[13 + i];
    }
    for(int i = old_size; i < 32; i++){
        old_password[i] = 0x00;
    }

    //checks aginst the curr password and returns if it is not the same
    if(memcmp(old_password, password_ascii, 32) == -1){
        //not the same
        set_password_flag = false;
        return;
    }

    //get the new password
    uint8_t new_password[32];
    uint8_t new_password_hash[32];
    uint8_t new_size = computer_in_packet[12 + old_size];
    uint8_t new_start_index = 14 + old_size;

    for(int i = 0; i < new_size; i++){
        new_password[i] = computer_in_packet[new_start_index + i];
    }
    for(int i = new_size; i < 32; i++){
        new_password[i] = 0x00;
    }

    //sets the new passowrd in storage hash and ascii
    memcpy(password_ascii, new_password, 32);
    mbedtls_sha256(new_password, 32, new_password_hash, 0);
    memcpy(password_hash, new_password_hash, 32);
    storage.putBytes("password", password_hash, 32);
    set_password_flag = true;
}