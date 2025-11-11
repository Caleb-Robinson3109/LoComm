#include "globals.h"

SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 4> serialReadyToSendArray;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);