import serial
import random #for gen random tag
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)
import math

def craft_SEND_packet(tag: int, name: str, text: str, total_packets: int, curr_packet) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = len(name) + len(text) + 23 # recount to make sure this number is correct
    message_type: bytes = b"SEND"
    #total_packets - 2, curr_packet - 2, name len - 1, text len -2, name, text
    message: bytes = struct.pack(f">HHBH{len(name)}s{len(text)}s", total_packets, curr_packet, len(name), len(text), name, text)

    #computer the payload for the checksum
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", tag) + message 
    crc: int = binascii.crc_hqx(payload, 0)

    end_bytes: int = 0x5678

    packet: bytes = struct.pack(f">HH4sI{len(message)}sHH",
                                start_bytes, 
                                packet_size,
                                message_type,
                                tag,
                                message,
                                crc,
                                end_bytes)
    
    return packet

def check_SACK_packet(packet: bytes, tag: int, packet_num: int) -> bool:
    return False

def locomm_api_send_message(name: str, message: str, ser: serial.Serial) -> bool:
    #split the message into 1000 char chucnks and send each chunk (same tag)
    for i in range (math.ceil(len(message) / 1000)):
        #for each chucnk
        chunk: str

        #last chunk
        if i == (math.ceil(len(message) / 1000)):
        
        #build packet
        #send_recv_packet
            print(f"i")
    return False
