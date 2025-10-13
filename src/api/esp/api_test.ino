#include <arduino.h>
#include "api.h"

//place to hold the incomming computer packert
uint_8 computer_in_packet[MAX_COMPUTER_PACKET_SIZE];

//place to hold the generated packet for the computer
byte computer_out_packet[MAX_DEVICE_PACKET_SIZE];

//place to store the packet ment to be send to the output buffer
byte device_out_packet[];

//place to store the incomming packet from the recive packet buffer
byte device_in_packet[];


//this flag is for computer to device communacation. If there is a message from the compter this flag turns true.
bool message_from_computer_flag = false;

//this flag is for device to device communication. If there is an incomming message, this flag turns high.
//This will likely have to have some sort of lock, Ethan and Caleb will have to discuess how comm works between reciving messages and output messages
bool message_from_device_flag = false;

//if there is a message ready to transmit for some source
bool message_for_computer_flag = false;
bool message_for_device_flag = false;

void setup() {
  Serial.begin(9600);
  delay(1000);

void loop() {
  //start process

  
  recive_packet_from_app();
  
  //if a message has been recived from another device hand this as so
  //I think the other processes will change the message_from_device_flag to true if there is a message
  //Some mechanaize to tell the computer to hold all of its packets unil the transmiter message is complete
  if(message_from_device_flag){
    //handle incomming message
  }

}
