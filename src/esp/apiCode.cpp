#include "apiCode.h"

void apiCode( void* params ) {
  while (1) {
    delay(1000);
    display.clearDisplay();
    display.setCursor(0,0);
    display.printf("SerialReady2SendArr: %lu", serialReadyToSendArray.size());
    display.display();
    if(serialReadyToSendArray.size() > 0){
      handle_message_from_device();
    }

    //there is a message from the device and the subsaquent funcs check and handle that
    recive_packet_from_computer();
    if(message_from_computer_flag){
      //Serial.println("Received message from computer");
      handle_message_from_computer();
    }
    if(message_to_device_flag){
      handle_message_to_device();
    }
    if(message_to_computer_flag){
      handle_message_to_computer();
    }
  }
  
}