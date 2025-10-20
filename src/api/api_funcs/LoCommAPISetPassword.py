import serial
import struct
import binascii
import random

def build_STPW_packet(tag: int, old: str, new: str) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = 2 + len(old) + len(new) + 16
    message_type: bytes = b"PASS"
    message: bytes = struct.pack(">B", len(old)) + struct.pack(">B", len(new)) + old.encode('ascii') + new.encode('ascii')

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

def send_recv_packet(tag: int, packet: bytes, ser: serial.Serial) -> None:
    ser.write(packet)
    ser.flush()
    #wait for respoce
    responce: bytes = ser.read(20)

    #check the packet
    if(len(responce) != 20):
        raise ValueError(f"incorrce recv packet len")
    
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
        print(f"start byte fail - {start_bytes}")
        raise ValueError(f"return packet fail: start byte fail - 0x1234, {start_bytes}")
    
    if(packet_size != 20):
        print(f"packet size fail - {packet_size}")
        raise ValueError(f"return packet fail: packet size fail - 20, {packet_size}")
    
    if(message_type != b"SPAK"):
        print(f"message type fail - {message_type}")
        raise ValueError(f"return packet fail: message type fail - PWAK, {message_type}")
    
    if(ret_tag != tag):
        print(f"tag fail - {tag} {ret_tag}")
        raise ValueError(f"return packet fail: tag fail - {tag}, {ret_tag}")
    
    if(message != b"OKAY"):
        print(f"message fail - {message}")
        raise ValueError(f"return packet fail: message fail - OKAY, {message}")

    if(crc != crc_check):
        print(f"crc fail - {crc} {crc_check}")
        raise ValueError(f"return packet fail: crc fail - {crc}, {crc_check}")

    if(end_bytes != 0x5678):
        print(f"end byte fail - {end_bytes}")
        raise ValueError(f"return packet fail: end byte fail - 0x5678, {end_bytes}")

def locomm_api_set_password(old: str, new: str, ser: serial.Serial) -> bool:
    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet = build_STPW_packet(tag, old, new)
        print(f"STPW packet - {packet}")
        send_recv_packet(tag, packet, ser)
        print("send STPW complete")

    except Exception as e:
        print(f"password set error: {e}")
        return False
    
    return True