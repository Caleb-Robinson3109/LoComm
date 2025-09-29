# LoComm
LoRa communication between ESP devices

Ethan Kleine - ejkmvp@umsystem.edu
Abraham Yirga - aayfn7@umsystem.edu
Caleb Robinson - cmrd2d@umsystem.edu
Kush Solanki - kysp2d@umsystem.edu
Shaun Wolfe - swgw8@umsystem.edu
Arjun Kirubakaran - apkccy@umsystem.edu

## Desktop App
src/app/*

## Device Drivers
src/driver/*

## ESP Code
src/esp/*


## USB Serial Communication Protocol
Serial Communication Protocol
	Start byte - 0x69
	Header - 
		Message length (1 byte)
		Sender - (1 byte)
		Receiver - (1 byte)
		Extra - (1 byte)
	Body - 
		Data
	CRC (checksum on the header and body) - (2 bytes)
	End byte - 0xAF

