#include <arduino.h>

#define MAX_PACKET_SIZE 100
byte packet[MAX_PACKET_SIZE];
int packetIndex = 0;

// Helper function: CRC-16 (CRC-CCITT)
uint16_t computeCRC16(const uint8_t *data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x8000)
        crc = (crc << 1) ^ 0x1021;
      else
        crc <<= 1;
    }
  }
  return crc;
}

//TODO create a time out, so that the processes has a chance to check for other work. Because this process will handle comm bewteen bevice and computer it needs to check for messages to send to the computer too
void recive_packet_from_app(){

}

void buildPacket(uint8_t *packet, uint32_t tag) {
  // Start bytes
  packet[0] = 0x12;
  packet[1] = 0x34;

  // Message type "CACK"
  packet[2] = 'C';
  packet[3] = 'A';
  packet[4] = 'C';
  packet[5] = 'K';

  // Tag (4 bytes, big-endian)
  packet[6]  = (tag >> 24) & 0xFF;
  packet[7]  = (tag >> 16) & 0xFF;
  packet[8]  = (tag >> 8) & 0xFF;
  packet[9]  = (tag) & 0xFF;

  // Compute CRC of Message Type + Tag (8 bytes total)
  uint16_t crc = computeCRC16(&packet[2], 8);
  packet[10] = (crc >> 8) & 0xFF;
  packet[11] = crc & 0xFF;

  // End bytes
  packet[12] = 0x56;
  packet[13] = 0x78;
}

void setup() {
  delay(1000);
  Serial.begin(9600);
  delay(1000);

  Wire.begin(OLED_SDA, OLED_SCL);
  //if (!//display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    //Serial.println(F("SSD1306 allocation failed"));
    //for (;;) ; // Halt
  //}

  //display.clear//display();
  //display.setTextColor(SSD1306_WHITE);
  //display.setTextSize(1);
  //display.setCursor(0, 0);
  //display.println("Waiting for packet...");
  //display.//display();
}

void loop() {
  Serial.readBytes(packet, PACKET_SIZE);

  // When the full 14-byte packet is received
  if (packetIndex == PACKET_SIZE) {
    //display.clear//display();
    //display.setCursor(0, 0);
    //display.println("Received packet:");
    
    for (int i = 0; i < PACKET_SIZE; i++) {
      if (packet[i] < 0x10) Serial.print("0");
      Serial.print(packet[i], HEX);
      Serial.print(" ");

      if (packet[i] < 0x10) //display.print("0");
      //display.print(packet[i], HEX);
      //display.print(" ");
    }
    Serial.println();

    //display.//display();

    // Reset index for next packet
    packetIndex = 0;
  }

  delay(100);

  uint8_t packet[14];
  uint32_t tag = 12345; // Example tag

  for (int i = 0; i < 14; i++) {
    if (packet[i] < 0x10) Serial.print("0");
    Serial.print(packet[i], HEX);
    Serial.print(" ");
  }

  buildPacket(packet, tag);
}
