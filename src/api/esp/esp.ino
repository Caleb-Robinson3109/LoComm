#include "LoCommAPI.h"
#include "LoCommLib.h"
#include "LoCommBuildPacket.h"

#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

void setup() {
  //blink led
  pinMode(2, OUTPUT);
  
  //set up serial
  Serial.begin(9600);
  delay(1000);
  blinky(2);

  Wire.begin(21, 22);
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("LoComm");

  init_password();
  //debug_simulate_device_in_packet();
}

void loop() {
  //there is a message from the device and the next 2 if statmetns handle that
  if(message_from_device_flag){
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("message_from_\ndevice_flag");
    delay(2000);
    handle_message_from_device();
  }

  //there is a message from the device and the subsaquent funcs check and handle that
  recive_packet_from_computer();
  if(message_from_computer_flag){
    handle_message_from_computer();
  }
  if(message_to_device_flag){
    handle_message_to_device();
  }
  if(message_to_computer_flag){
    handle_message_to_computer();
  }
}
