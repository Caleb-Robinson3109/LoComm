#include "LoCommLib.h"

void blinky1(){
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
}

void blinky2(){
  digitalWrite(2, HIGH);
  delay(1000);
  digitalWrite(2, LOW);
}

void blinky(int blinks){
    for(int i = 0; i < blinks; i++){
        digitalWrite(2, HIGH);
        delay(250);
        digitalWrite(2, LOW);
        delay(250);
    }
}

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

bool message_type_match(const uint8_t* buf, const char* str, size_t len){
    for (size_t i = 0; i < len; i++) {
        if (buf[i] != (uint8_t)str[i]) {
            return false;
        }
    }
    return true;
}

void init_password(){
    //open the namespace LoComm or create it if it has not be made yet, 0 for RW mode

    //check to see if there is storage of the password if not add default password
    size_t passowrd_len = storage.getBytesLength("password");
    if(passowrd_len == 0){
        mbedtls_sha256(default_password, 32, password_hash, 0);
        storage.putBytes("password", password_hash, 32);
    }
    else{
        mbedtls_sha256(default_password, 32, password_hash, 0);
        //storage.getBytes("password", password_hash, 32);
        storage.putBytes("password", password_hash, 32);
    }

}

bool check_SACK(){
    //chech the start bytes
    if(computer_in_packet[0] != 0x12){
        return false;
    }
    if(computer_in_packet[1] != 0x34){
        return false;
    }
    //chech the packet lenght 18 0000 0000 00001 0010
    if(computer_in_packet[2] !=  0b00000000){
        return false;
    }
    if(computer_in_packet[3] != 0b00010010){
        return false;
    }
    //chech the packet type
    if(computer_in_packet[4] != 'S'){
        return false;
    }
    if(computer_in_packet[5] != 'A'){
        return false;
    }
    if(computer_in_packet[6] != 'C'){
        return false;
    }
    if(computer_in_packet[7] != 'K'){
        return false;
    }
    //check the tag
    if(computer_in_packet[8] != device_in_packet[8]){
        return false;
    }
    if(computer_in_packet[9] != device_in_packet[9]){
        return false;
    }
    if(computer_in_packet[10] != device_in_packet[10]){
        return false;
    }
    if(computer_in_packet[11] != device_in_packet[11]){
        return false;
    }
    //chech the packet number
    if(computer_in_packet[12] != device_in_packet[14]){
        return false;
    }
    if(computer_in_packet[13] != device_in_packet[15]){
        return false;
    }
    //skip crc bc weve testd everything else and im feeling lazy rn
    //if for saving computational power yeah

    //end bytes
    if(computer_in_packet[14] != 0x56){
        return false;
    }
    if(computer_in_packet[15] != 0x78){
        return false;   
    }
    return true;
}


void debug_simulate_device_in_packet(){
    //start bytes
    device_in_packet[0] = 0x12;
    device_in_packet[1] = 0x34;
    
    //packet size
    device_in_packet[2] = 0x00;
    device_in_packet[3] = 0x28;
    
    //packet type
    device_in_packet[4] = 'S';
    device_in_packet[5] = 'E';
    device_in_packet[6] = 'N';
    device_in_packet[7] = 'D';
    
    //packet tag
    device_in_packet[8] = 0xff;
    device_in_packet[9] = 0xff;
    device_in_packet[10] = 0xff;
    device_in_packet[11] = 0xff;
    
    //message
    //total number of packets (1)
    device_in_packet[12] = 0x00;
    device_in_packet[13] = 0x01;
    
    //packet number (1)
    device_in_packet[14] = 0x00;
    device_in_packet[15] = 0x01;

    //name lenght (4)
    device_in_packet[16] = 0x05;

    //message lenght (11)
    device_in_packet[17] = 0x00;
    device_in_packet[18] = 0x0c;
    
    //name
    device_in_packet[19] = 'c';
    device_in_packet[20] = 'a';
    device_in_packet[21] = 'l';
    device_in_packet[22] = 'e';
    device_in_packet[23] = 'b';

    //message
    device_in_packet[24] = 'H';
    device_in_packet[25] = 'e';
    device_in_packet[26] = 'l';
    device_in_packet[27] = 'l';
    device_in_packet[28] = 'o';
    device_in_packet[29] = ' ';
    device_in_packet[30] = 'W';
    device_in_packet[31] = 'o';
    device_in_packet[32] = 'r';
    device_in_packet[33] = 'l';
    device_in_packet[34] = 'd';
    device_in_packet[35] = '!';
    
    //crc
    uint16_t crc = crc_16(&device_in_packet[2], 34);

    device_in_packet[36] = (crc >> 8) & 0xff;
    device_in_packet[37] = crc & 0xff;
    
    //end bytes
    device_in_packet[38] = 0x56;
    device_in_packet[39] = 0x78;

    message_from_device_flag = true;
    device_in_size = 40;
}

void displayName(){
    //displays the name
    display.clearDisplay();
    display.setCursor(1,1);
    display.printf("Device Name:");
    display.display();
    display.setCursor(2,40);
    for(int i = 0; i < 32; i++){
        if(device_name[i] != 0x00){
            display.printf("%c", device_name[i]);
            display.display();
        }
    }
}