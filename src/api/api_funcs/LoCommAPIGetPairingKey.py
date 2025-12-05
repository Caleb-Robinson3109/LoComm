import serial
import struct
import binascii
import random
from api_funcs.LoCommContext import LoCommContext
import api_funcs.LoCommGlobals as LoCommGlobals
from api_funcs.LoCommDebugPacket import print_packet_debug

def build_GPKY_packet(tag: int) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = 16
    message_type: bytes = b"SCAN"

    #computer the payload for the checksum
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", tag)
    crc: int = binascii.crc_hqx(payload, 0)

    end_bytes: int = 0x5678

    packet: bytes = struct.pack(f">HH4sIHH",
                                start_bytes, 
                                packet_size,
                                message_type,
                                tag,
                                crc,
                                end_bytes)
    return packet

def check_GPAK_packet(packet: bytes, tag: int) -> bool:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4s21sIHH", packet)

    if start_bytes != 0x1234:
        return f"start bytes error 0x1234, {start_bytes}", False
    
    if packet_size != packet_size:
        return f"packet size error 14, {packet_size}", False
    
    if message_type != b"GPAK":
        return f"message type error GPAK, {message_type}", False
    
    if ret_tag != tag:
        return f"tag mismatch {tag}, {ret_tag}", False
    
    
    payload: bytes = struct.pack(">HH4sI21s", start_bytes, packet_size, message_type, tag, message)
    crc_check: int = binascii.crc_hqx(payload, 0)

    if crc_check != crc:
        return f"crc fail {crc}, {crc_check}", False
    
    if end_bytes != 0x5678:
        return f"end bytes fail 0x5678, {end_bytes}", False
    
    return "no error", True 

def locomm_api_get_pairing_key() -> list:
    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet = build_GPKY_packet(tag)
        print_packet_debug(packet, True)        
        LoCommGlobals.serial_conn.write(packet)
        LoCommGlobals.serial_conn.flush()

        #wait for responce from LCC
        while(not LoCommGlobals.context.GPAK_flag):
            pass

        print_packet_debug(LoCommGlobals.context.packet, False)
        check_GPAK_packet(LoCommGlobals.context.packet, tag)

    except Exception as e:
        print(f"scan error: {e}")
        LoCommGlobals.context.GPAK_flag = False
        return None
    
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    key_exists: bytes
    pairing_key: bytes
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, key_exists, pairing_key, crc, end_bytes = struct.unpack(">HH4s1s20sIHH", packet)

    if(key_exists == 0x00):
        LoCommGlobals.context.GPAK_flag = False
        return None
     
    LoCommGlobals.context.GPAK_flag = False
    key = pairing_key.decode('ascii')
    return key