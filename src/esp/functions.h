#pragma once

#define CURRENT_LOG_LEVEL LOG_LEVEL_DEBUG

#define LORA_RX_BUFFER_SIZE 1024
#define LORA_TX_BUFFER_SIZE 1024
#define MIN_CAD_WAIT_INTERVAL_MS 1
#define LORA_READY_TO_SEND_BUFFER_SIZE 1024
#define LORA_ACK_BUFFER_SIZE 256
#define LORA_SEND_COUNT_MAX 8
#define SERIAL_READY_TO_SEND_BUFFER_SIZE 128
#define SEQUENCE_MAX_SIZE 128

#define IDLE_MODE 1
#define RX_MODE 2
#define TX_MODE 3
#define CAD_MODE 4
#define CAD_FINISHED 5
#define CAD_FAILED 6
#define SLEEP_MODE 0

#define LLog(x) Log(LOG_LEVEL_LOG, x)
#define LDebug(x) Log(LOG_LEVEL_DEBUG, x)
#define LWarn(x) Log(LOG_LEVEL_WARNING, x)
#define LError(x) Log(LOG_LEVEL_ERROR, x)
#define HALT() Serial.println("Halting"); while(1)
#define Debug(x) if (CURRENT_LOG_LEVEL == LOG_LEVEL_DEBUG) x

#define diff(new, old, size) (new >= old) ? new - old : size - old + new

#define START_BYTE 0xc1
#define END_BYTE 0x8c

#define RUN_UNIT_TESTS false


#include <stdio.h>
#include "esp.h"
#include "CyclicArrayList.h"
#include "SimpleArraySet.h"
#include "DefraggingBuffer.h"
#include <SPI.h>
#include "LoRa.h"

//Libraries for OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <esp_rom_crc.h>

enum LOG_LEVEL {LOG_LEVEL_NONE, LOG_LEVEL_ERROR, LOG_LEVEL_WARNING, LOG_LEVEL_LOG, LOG_LEVEL_DEBUG };

void Log(LOG_LEVEL level, const char* text);
const char* logLevelEnumToChar(LOG_LEVEL level);
void runTests();