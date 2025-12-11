import serial
import struct
import binascii
import random
from api_funcs.LoCommContext import LoCommContext
import api_funcs.LoCommGlobals as LoCommGlobals
from api_funcs.LoCommDebugPacket import print_packet_debug

def build_SCAN_packet(tag: int) -> bytes:
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

def check_SCAK_packet(packet: bytes, tag: int) -> bool:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4sI32sHH", packet)

    if start_bytes != 0x1234:
        return f"start bytes error 0x1234, {start_bytes}", False
    
    if packet_size != packet_size:
        return f"packet size error 14, {packet_size}", False
    
    if message_type != b"SCAK":
        return f"message type error SCAN, {message_type}", False
    
    if ret_tag != tag:
        return f"tag mismatch {tag}, {ret_tag}", False
    
    
    payload: bytes = struct.pack(">H4sI32s", packet_size, message_type, tag, message)
    crc_check: int = binascii.crc_hqx(payload, 0)

    if crc_check != crc:
        return f"crc fail {crc}, {crc_check}", False
    
    if end_bytes != 0x5678:
        return f"end bytes fail 0x5678, {end_bytes}", False
    
    return "no error", True 

def locomm_api_scan() -> list:
    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet = build_SCAN_packet(tag)
        print_packet_debug(packet, True)        
        LoCommGlobals.context.SCAK_flag = False
        LoCommGlobals.serial_conn.write(packet)
        LoCommGlobals.serial_conn.flush()

        #wait for responce from LCC
        while(not LoCommGlobals.context.SCAK_flag):
            pass

        print_packet_debug(LoCommGlobals.context.packet, False)
        print(check_SCAK_packet(LoCommGlobals.context.packet, tag))
        

    except Exception as e:
        print(f"scan error: {e}")
        LoCommGlobals.context.SCAK_flag = False
        return []
    
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int
    print("finished checking SCAK packet, unpacking...")
    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4sI32sHH", LoCommGlobals.context.packet)

    devices = []

    print(f"message: {message}")

    for byte_index, byte in enumerate(message):
        for bit_index in range(8):
            bit = (byte >> (7 - bit_index)) & 1
            if bit == 1:
                index = byte_index * 8 + bit_index
                devices.append((f"Device{index}", index))


    LoCommGlobals.context.SCAK_flag = False
    return devices