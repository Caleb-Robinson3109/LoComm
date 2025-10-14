#include "LoCommAPI.h"
#include "blinky.h"
#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  //blink led
  pinMode(2, OUTPUT);
  blinky1();
  
  //set up serial
  Serial.begin(9600);
  delay(2000);

  Wire.begin(21, 22);
  lcd.begin();
  lcd.backlight(); 
}

void loop() {
  //there is a message from the device and the next 2 if statmetns handle that
  if(message_from_device_flag){
    //handle
    ;;
  }
  if(message_to_computer_flag){
    //blinky(1);
    handle_message_to_computer();
  }

  //there is a message from the device and the subsaquent funcs check and handle that
  recive_packet_from_computer();
  if(message_from_computer_flag){
    handle_message_from_computer();
    //delay(500);
  }
  if(message_to_device_flag){
    //handle
    ;;
  }
  if(message_to_computer_flag){
    //lcd.setCursor(0, 0);
    //lcd.print((char*)computer_in_packet);
    handle_message_to_computer();
    //blinky(3);
  }
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("mtcf - ");                     // Use print for strings
  lcd.print((int)message_to_computer_flag); // Use print for numbers
  //delay(305);
  //lcd.print((char*)computer_in_packet);
}
