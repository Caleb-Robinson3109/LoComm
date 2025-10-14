#include "blinky.h"

void blinky1(){
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(100);
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
}

void blinky2(){
  digitalWrite(2, HIGH);
  delay(1000);
  digitalWrite(2, LOW);
}

void blinky(int blinks){
    for(int i = 0; i < blinks; i++){
        digitalWrite(2, HIGH);
        delay(250);
        digitalWrite(2, LOW);
        delay(250);
    }
}