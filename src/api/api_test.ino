#include <arduino.h>
#include "api.h"

byte computer_packet[MAX_COMPUTER_PACKET_SIZE];
byte device_packet[MAX_DEVICE_PACKET_SIZE];
bool message_from_computer_flag = false;
bool message_from_device_flag = false;

void setup() {
  Serial.begin(9600);
  delay(1000);

void loop() {
  //start process

  //this function has a time out of ~1s rn i think to allow for the device to check for incomming messages
  //maybe even we can have an incomming message break out of the Serial.read() with minulataion of tx? rx? registers
  recive_packet_from_app();
  
  //if a message has been recived from another device hand this as so
  //I think the other processes will change the message_from_device_flag to true if there is a message
  //Some mechanaize to tell the computer to hold all of its packets unil the transmiter message is complete
  if(message_from_device_flag){
    //handle incomming message
  }
}
