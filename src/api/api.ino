void setup(){
  Serial.begin(9600);
  delay(1000);
}

void loop(){
  Serial.print("hello from esp\n");
  delay(1000);
}