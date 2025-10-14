#ifndef BLINKY_H
#define BLINKY_H

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

extern LiquidCrystal_I2C lcd;

void blinky1();
void blinky2();
void blinky(int blinks);

#endif