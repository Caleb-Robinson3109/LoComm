#ifndef GLOBALS_H
#define GLOBALS_H

#include "functions.h"

//Serial TX Related Variables
//TODO for sake of performance, this should probably be a CyclicArrayList
extern SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4> serialReadyToSendArray; //Queue for sending data out to serial //(location in the rxMessageBuffer, size)
extern Adafruit_SSD1306 display;
extern uint32_t epochAtBoot;
extern uint8_t device_name[32];
extern const uint8_t default_password[32];

#endif