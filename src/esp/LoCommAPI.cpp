#include "LoCommAPI.h"
#include "functions.h"
#include "globals.h"
#include "security_protocol.h"

uint8_t computer_in_packet[MAX_COMPUTER_PACKET_SIZE];
uint8_t computer_out_packet[MAX_COMPUTER_PACKET_SIZE];
uint8_t device_in_packet[MAX_DEVICE_PACKET_SIZE];
uint8_t device_out_packet[MAX_DEVICE_PACKET_SIZE];
bool message_from_computer_flag = false;
bool message_to_computer_flag = false;
bool message_from_device_flag = false;
bool message_to_device_flag = false;
bool password_entered_flag = false;
bool set_password_flag = false;
size_t computer_out_size = 0;
size_t device_out_size = 0;
size_t computer_in_size = 0;
size_t device_in_size = 0;

extern uint8_t deviceID;
extern SimpleArraySet<SERIAL_READY_TO_SEND_BUFFER_SIZE, 5> serialReadyToSendArray;
extern DefraggingBuffer<2048, 8> rxMessageBuffer;
extern bool addMessageToTxArray(uint8_t* src, uint16_t size, uint8_t destinationID);
extern portMUX_TYPE loraRxSpinLock;
extern bool loraRxLock;
extern portMUX_TYPE loraTxSpinLock;
extern bool loraTxLock;
extern portMUX_TYPE serialLoraBridgeSpinLock;
extern bool serialLoraBridgeLock;

//const uint8_t default_password[32] = {'p', 'a', 's', 's', 'w', 'o', 'r', 'd',
//    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
//    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
//    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

uint8_t password_hash[32] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

    uint8_t password_ascii[32] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};



void recive_packet_from_computer(){
    blinky2();
    size_t serial_index = 0;
    //delay(1000);
    if(Serial.available() == 0){
        return;
    }
    delay(10);
    while(Serial.available() > 0 && serial_index < MAX_COMPUTER_PACKET_SIZE){
        computer_in_packet[serial_index++] = Serial.read();
    }

    message_from_computer_flag = true;

    //set the lenght of the incommed packet
    computer_in_size = serial_index;
}

void handle_message_from_computer(){
    //check start bytes
    if(!(computer_in_packet[0] == 0x12 && computer_in_packet[1] == 0x34)){
        message_from_computer_flag = false;
        computer_in_size = 0;
        blinky(2);
        return;
    }

    //check lenght
    uint16_t packet_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    if(packet_size != computer_in_size){
        message_from_computer_flag = false;
        computer_in_size = 0;
        blinky(2);
        return;
    }

    //chech crc
    //use packet_size - 6 so we dont do the start and end bytes and crc itself
    uint16_t crc = crc_16(&computer_in_packet[2], packet_size - 6);
    uint8_t crc_high = (crc >> 8) & 0xFF;
    uint8_t crc_low  = crc & 0xFF;
    //if the 4th to last byte and 3rd to last byte (packet crc) of the computer in packet are not equal to our crc
    if(crc_high != computer_in_packet[packet_size - 4] || crc_low  != computer_in_packet[packet_size - 3]){
        message_from_computer_flag = false;
        computer_in_size = 0;
        blinky(2);
        return;
    }

    //check end bytes
    if(computer_in_packet[packet_size - 2] != 0x56 && computer_in_packet[packet_size - 1] != 0x78){
        message_from_computer_flag = false;
        computer_in_size = 0;
        blinky(2);
        return;
    }

    //get the message type of the packet
    uint8_t message_type[4];
    for(int i = 0; i < 4; i++){
        message_type[i] = computer_in_packet[i+4];
    }

    //the build_TYPE_packet will build in the device_out_packet[]
    if(message_type_match(message_type, "CONN", MESSAGE_TYPE_SIZE)){
        blinky(3);
        handle_CONN_packet();
    }

    else if(message_type_match(message_type, "PASS", MESSAGE_TYPE_SIZE)){
        handle_PASS_packet();
    }

    else if(message_type_match(message_type, "DCON", MESSAGE_TYPE_SIZE)){
        handle_DCON_packet();
    }

    else if(message_type_match(message_type, "STPW", MESSAGE_TYPE_SIZE)){
        handle_STPW_packet();
    }

    else if(message_type_match(message_type, "SEND", MESSAGE_TYPE_SIZE)){
        handle_SEND_packet();
    }
    else if(message_type_match(message_type, "SNOD", MESSAGE_TYPE_SIZE)){
        handle_SNOD_packet();
    }
    else if(message_type_match(message_type, "EPAR", MESSAGE_TYPE_SIZE)){
        handle_EPAR_packet();
    }
    else if(message_type_match(message_type, "SCAN", MESSAGE_TYPE_SIZE)){
        handle_SCAN_packet();
    }
    else if (message_type_match(message_type, "GPKY", MESSAGE_TYPE_SIZE)){
        handle_GPKY_packet();
    }
    else{
        Serial.write("FAIL");
    }
}

void handle_message_to_computer(){
    //lcd.clear();
    //lcd.setCursor(0,0);
    for(int i = 0; i < 16; i++){
        //lcd.write(computer_out_packet[i]);
    }
    //lcd.setCursor(0,1);
    //lcd.print("out packet");
    //delay(1000);
    Serial.write(computer_out_packet, computer_out_size);
    Serial.flush();
    message_to_computer_flag = false;
    computer_out_size = 0;
}

void handle_PASS_packet(){
    //get the lenght of the password
    uint16_t password_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    password_size -= 16;
    char* input_password = new char[password_size + 1];
    
    //uint8_t input_password_hash[32];

    //get the new password in the packet
    //uint8_t input_password [32];

    for(int i = 0; i < password_size; i++){
        input_password[i] = computer_in_packet[i + 12];
    }
    input_password[password_size] = '\0';

    //fill in with 0x00 with any extra space
    //for(int i = password_size; i < 32; i++){
    //   input_password[i] = 0x00;
    //}

    //get the password hash stored in storage and check it aginst the enterne password.
    //if the password is corrext store it and set the passowrd flag
    //mbedtls_sha256(input_password, 32, input_password_hash, 0);
    //if(memcmp(input_password_hash, password_hash, 32) == 0){
    //    memcpy(password_ascii, input_password, 32);
    //    password_entered_flag = true;
    //}
    //else{
    //    password_entered_flag = false;
    //}
    bool password_okay = sec_login(input_password);
    if(password_okay){
        password_entered_flag = true;
    }
    else{
        password_entered_flag = false;
    }
    build_PWAK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
    delete[] input_password;
}

void handle_DCON_packet(){
    // overwrites the password and the password hash with 0x00
    //for(int i = 0; i < PASSWORD_SIZE; i++){
    //    password_ascii[i] = 0x00;
    //    password_hash[i] = 0x00;
    //}
    sec_logout();
    set_password_flag = false;
    password_entered_flag = false;
    //TODO eventuall the key with 0x00 

    build_DCAK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}

void handle_STPW_packet(){
    //extract password from message
    uint16_t password_size = ((uint16_t)computer_in_packet[2] << 8) | computer_in_packet[3];
    password_size -= 16;
    char* input_password = new char[password_size + 1];

    for(int i = 0; i < password_size; i++){
      input_password[i] = computer_in_packet[i + 12];
    }
    input_password[password_size] = '\0';

    set_password_flag = true;
    //just call the reset function
    if (sec_setInitialPassword(input_password)) {
      build_SPAK_packet();
    } else {
      build_SPAK_packet();
    }
    message_to_computer_flag = true;
    message_from_computer_flag = false;
    delete[] input_password;

    //uint8_t old_password[32];
    /*
    uint8_t old_size = computer_in_packet[12];
    char* old_password = new char[old_size + 1];

    //get the old password and set the blank bytes to 0x00
    for(int i = 0; i < old_size; i++){
        old_password[i] = computer_in_packet[14 + i];
    }
    old_password[old_size] = '\0';
    //for(int i = old_size; i < 32; i++){
    //    old_password[i] = 0x00;
    //}

    //checks aginst the curr password and returns if it is not the same
    //if(memcmp(old_password, password_ascii, 32) == -1){
        //not the same
    //    set_password_flag = false;

    //    build_SPAK_packet();
    //    message_to_computer_flag = true;
    //    message_from_computer_flag = false;

    //    return;
    //}

    //get the new password
    //uint8_t new_password[32];
    //uint8_t new_password_hash[32];
    uint8_t new_size = computer_in_packet[13];
    uint8_t new_start_index = 14 + old_size;
    char* new_password = new char[new_size + 1];


    for(int i = 0; i < new_size; i++){
        new_password[i] = computer_in_packet[new_start_index + i];
    }
    new_password[new_size] = '\0';
    //for(int i = new_size; i < 32; i++){
    //    new_password[i] = 0x00;
    //}

    //sets the new passowrd in storage hash and ascii
    //memcpy(password_ascii, new_password, 32);
    //mbedtls_sha256(new_password, 32, new_password_hash, 0);
    //memcpy(password_hash, new_password_hash, 32);
    //storage.putBytes("password", password_hash, 32);
    //set_password_flag = true;

    //build_SPAK_packet();
    //message_to_computer_flag = true;
    //message_from_computer_flag = false;
    bool set_password_okay = sec_changePassword(old_password, new_password);
    if(set_password_okay){
        set_password_flag = true;
    }
    else{
        set_password_flag = false;
    }
    build_SACK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;

    delete [] old_password;
    delete [] new_password;
    */
}

void handle_CONN_packet(){
    //TODO bring out the encripted keys
    
    //gets the password hash from sorage
    //storage.getBytes("password", password_hash, 32);

    //sets the epoch time
    uint32_t epoch = ((uint32_t)computer_in_packet[12] << 24) |
        ((uint32_t)computer_in_packet[13] << 16) |
        ((uint32_t)computer_in_packet[14] << 8)  |
        ((uint32_t)computer_in_packet[15]);

    epochAtBoot = epoch - (millis() / 1000);

    //display.setCursor(0,0);
    //display.printf("----%d----", epoch);
    //display.display();


    build_CACK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}

void handle_SEND_packet(){
    //puts the computer in packet into device out packet
    //lcd.clear();
    //lcd.setCursor(0,0);
    //lcd.print("handle SEND packet");
    //delay(1000);
    uint16_t packet_size = ((uint16_t)computer_in_packet[2]  << 8) | computer_in_packet[3];
    packet_size++;

    //have to add the device id to the packet
    memcpy(device_out_packet, computer_in_packet, 12);
    device_out_packet[12] = deviceID;

    memcpy(&device_out_packet[13], &computer_in_packet[12], packet_size - 13);
    
    //add in new size and recompute the new crc
    device_out_packet[2] = (packet_size >> 8) & 0xFF;
    device_out_packet[3] = packet_size & 0xFF;

    uint16_t crc = crc_16(&device_out_packet[2], packet_size - 6);
    device_out_packet[packet_size - 4] = (crc >> 8) & 0xFF;
    device_out_packet[packet_size - 3] = crc & 0xFF; 

    //set the message_to_device flag
    message_to_device_flag = true;

    //gets the packet size
    device_out_size = packet_size;



    //build SACK
    //build_SACK_packet();
    //lcd.clear();
    //lcd.setCursor(0,0);
    //lcd.print("device out packet");
    //delay(1000);
    //lcd.clear();
    //lcd.setCursor(0,0);
    //for(int i = 0; i < 16; i++){
        //lcd.write(device_out_packet[i]);
    //}
    //delay(1000);

    //set the other flags to handle the sack to computer message
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}

void handle_message_to_device(){
    //wait for the packet to be handled
    //lcd.clear();
    //lcd.setCursor(0,0);
    //lcd.print("handle message to device");
    //delay(1000);
    //while(message_to_device_flag){
    if (addMessageToTxArray(&(device_out_packet[0]), device_out_size, device_out_packet[13])) {
      build_SACK_packet();
      message_to_device_flag = false; // Completed transfer to Ethans code
      device_out_size = 0;
    }
      //TODO add an else condition here that disgards the message if the attempt to add it to the tx array failed
        //TODO work with Ethan to intergrate his code in this to handle this message needing to go to the other device
    //}
}

void handle_message_from_device(){
    //lcd.clear();
    //lcd.setCursor(0,0);
    //lcd.print("handle mfd");
    //delay(2000);
    //if the password is not set then drop the packet
    /*
    if(!password_entered_flag){
        //lcd.setCursor(0,1);
        //lcd.print("no password!");

        //drop packet if there is no password
        message_from_device_flag = false;
        device_in_size = 0;
        return;
    }
    */

    {
      ScopeLockName(serialLoraBridgeSpinLock, serialLoraBridgeLock, n1);
      ScopeLockName(loraRxSpinLock, loraRxLock, n2);
      const uint16_t addr = (serialReadyToSendArray.get(0)[0] << 8) + serialReadyToSendArray.get(0)[1];
      const uint16_t size = (serialReadyToSendArray.get(0)[2] << 8) + serialReadyToSendArray.get(0)[3];

      Serial.write(&(rxMessageBuffer[addr]), size);
      rxMessageBuffer.free(addr);
      serialReadyToSendArray.remove(0);
    }

    Serial.flush();

    //send the  computer packet out to the computer
    //wait for an ack
    //if no ack in 0.5 secs resend
    //try 10 or so times
    bool ack_recv = false;
    int times_tried = 0;
    //TODO fix ack recv
    //while(!ack_recv || times_tried < 10){

        /*unsigned long start = millis();
        while((millis() - start) < 1000 && Serial.available() == 0){
            //delay(100);
        }

        if(Serial.available() == 0){
            times_tried++;
            continue;
        }

        int serial_index = 0;
        while(Serial.available() > 0 && serial_index < MAX_COMPUTER_PACKET_SIZE){
            computer_in_packet[serial_index++] = Serial.read();
        }
        computer_in_size = serial_index;

        ack_recv = check_SACK();
        if(!ack_recv){
            times_tried++;
            while(Serial.available()) Serial.read(); // clear buffer
        }
    }

    //stop trying to send packet to computer if tries > 10, computer is broke or something
    if(!ack_recv){
        message_from_device_flag = false;
        device_out_size = 0;
        return;
    }

    //check thats its really an ack if not try one more time
    if(!check_SACK()){
        Serial.write(computer_out_packet, computer_out_size);
        Serial.flush();
        //delay(500);
        while(Serial.available()) Serial.read();
    }*/

    //complete and set the appropate flags
    device_out_size = 0;
}

void handle_SNOD_packet(){
    memcpy(device_name, &computer_in_packet[12], 32);

    //displayName();

    build_SNAK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}

void handle_EPAR_packet(){
    char key[21];
    for(int i = 0; i < 20; i++){
        key[i] = computer_in_packet[12 + i];
    }
    key[20] = '\0';

    sec_log_key(key);

    build_EPAK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}

void handle_SCAN_packet(){
    build_SCAK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}

void handle_GPKY_packet(){
    build_GPAK_packet();
    message_to_computer_flag = true;
    message_from_computer_flag = false;
}