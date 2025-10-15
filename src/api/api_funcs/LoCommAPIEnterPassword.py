import serial
import random #for gen random tag
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)

def craft_PASS_packet(tag: int, password: str) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = len(password) + 16
    message_type: bytes = b"PASS"
    message: bytes = password.encode('ascii')

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


def try_send_packet(packet: bytes, ser: serial.Serial, tag: int, tries: int) -> None:
    if(tries > 10):
        raise ValueError("exceed max number of tries")

    ser.write(packet)
    #wait for respoce
    responce: bytes = ser.read(20)

    #check the packet
    if(len(responce) != 20):
        ser.write(packet)
    
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4sI4sHH", responce)

    #crc calc
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", ret_tag) + message
    crc_check: int = binascii.crc_hqx(payload, 0)

    #some part of the packet is wrong, so try again 
    if(start_bytes != 0x1234):
        return try_send_packet(packet, ser, tag, tries + 1)
    
    if(packet_size != 20):
        return try_send_packet(packet, ser, tag, tries + 1)
    
    if(message_type != b"PWAK"):
        return try_send_packet(packet, ser, tag, tries + 1)
    
    if(ret_tag != tag):
        return try_send_packet(packet, ser, tag, tries + 1)
    
    if(message != b"OKAY"):
        return try_send_packet(packet, ser, tag, tries + 1)

    if(crc != crc_check):
        return try_send_packet(packet, ser, tag, tries + 1)

    if(end_bytes != 0x5678):
        return try_send_packet(packet, ser, tag, tries + 1)

def locomm_api_enter_password(password: str, ser: serial.Serial) -> bool:
    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet = craft_PASS_packet(tag, password)
        try_send_packet(packet, ser, tag, 0)

    except Exception as e:
        print(f"password set error: {e}")
        return False
    
    return True
