#include "LoCommLib.h"

LiquidCrystal_I2C lcd(0x27, 16, 2);

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
    storage.begin("LoComm", 0);

    //check to see if there is storage of the password if not add default password
    size_t passowrd_len = storage.getBytesLength("password");
    if(passowrd_len == 0){
        //mbedtls_sha256(default_password, 32, password_hash, 0);
        storage.putBytes("password", password_hash, 32);
    }
    else{
        storage.getBytes("password", password_hash, 32);
    }

}