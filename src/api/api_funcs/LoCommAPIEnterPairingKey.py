import serial
import struct
import binascii
import random
from api_funcs.LoCommContext import LoCommContext
import api_funcs.LoCommGlobals as LoCommGlobals
from api_funcs.LoCommDebugPacket import print_packet_debug

def build_EPAR_packet(tag: int, key: str) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = 36
    message_type: bytes = b"EPAR"
    message: bytes = struct.pack(">20s",key)

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

def check_EPAK_packet(packet: bytes, tag: int) -> bool:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4sIHH", packet)

    if start_bytes != 0x1234:
        return f"start bytes error 0x1234, {start_bytes}", False
    
    if packet_size != 16:
        return f"packet size error 14, {packet_size}", False
    
    if message_type != b"EPAK":
        return f"message type error EPAK, {message_type}", False
    
    if ret_tag != tag:
        return f"tag mismatch {tag}, {ret_tag}", False
    
    
    payload: bytes = struct.pack(">H4sIH", packet_size, message_type, tag, message)
    crc_check: int = binascii.crc_hqx(payload, 0)

    if crc_check != crc:
        return f"crc fail {crc}, {crc_check}", False
    
    if end_bytes != 0x5678:
        return f"end bytes fail 0x5678, {end_bytes}", False
    
    return "no error", True 

def locomm_api_enter_pairing_key(key: str) -> bool:
    #confirm base85
    base85 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#'
    for char in key:
        if char not in base85:
            return False
        
    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet = build_EPAR_packet(tag, key)
        print_packet_debug(packet, True)        
        LoCommGlobals.serial_conn.write(packet)
        LoCommGlobals.serial_conn.flush()

        #wait for responce from LCC
        while(not LoCommGlobals.context.EPAK_flag):
            pass

        print_packet_debug(LoCommGlobals.context.packet, False)
        check_EPAK_packet(LoCommGlobals.context.packet, tag)

    except Exception as e:
        print(f"password set error: {e}")
        LoCommGlobals.context.EPAK_flag = False
        return False
    
    LoCommGlobals.context.EPAK_flag = False
    return True