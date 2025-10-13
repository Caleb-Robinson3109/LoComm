#include "LoCommAPI.h"
#include <Arduino.h>

void setup() {
  //blink led
  pinMode(2, OUTPUT);

  //set up serial
  Serial.begin(9600);
  delay(1000);
}

void loop() {
  //there is a message from the device and the next 2 if statmetns handle that
  if(message_from_device_flag){
    //handle
    ;;
  }
  if(message_to_computer_flag){
    handle_message_to_computer();
  }

  //there is a message from the device and the subsaquent funcs check and handle that
  recive_packet_from_computer();
  if(message_from_computer_flag){
    handle_message_from_computer();
  }
  if(message_to_device_flag){
    //handle
    ;;
  }
  if(message_to_computer_flag){
    handle_message_to_computer();
    blinky1();
  }
}
