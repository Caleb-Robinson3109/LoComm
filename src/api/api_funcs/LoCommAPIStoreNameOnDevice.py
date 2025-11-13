import serial
import random #for gen random tag
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)
from api_funcs.LoCommContext import LoCommContext
from api_funcs.LoCommDebugPacket import print_packet_debug
import api_funcs.LoCommGlobals as LoCommGlobals

def craft_SNOD_packet(tag: int, name: bytes) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = 48
    message_type: bytes = b"SNOD"

    #computer the payload for the checksum
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", tag) + name 
    crc: int = binascii.crc_hqx(payload, 0)

    end_bytes: int = 0x5678

    packet: bytes = struct.pack(f">HH4sI32sHH",
                                start_bytes, 
                                packet_size,
                                message_type,
                                tag,
                                name,
                                crc,
                                end_bytes)
    
    return packet


def check_SNAK_packet(packet: bytes, tag: int) -> None:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int

    print(f"packet size: {len(packet)}")
    if len(packet) != 16:
        print("weird not 16 bytes")
        return

    start_bytes, packet_size, message_type, ret_tag, crc, end_bytes = struct.unpack(">HH4sIHH", packet)

    #crc calc
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", ret_tag)
    crc_check: int = binascii.crc_hqx(payload, 0)

    #some part of the packet is wrong, so try again 
    if(start_bytes != 0x1234):
        print(f"start byte fail - {start_bytes}")
        raise ValueError(f"return packet fail: start byte fail - 0x1234, {start_bytes}")
    
    if(packet_size != 16):
        print(f"packet size fail - {packet_size}")
        raise ValueError(f"return packet fail: packet size fail - 16, {packet_size}")
    
    if(message_type != b"SNAK"):
        print(f"message type fail - {message_type}")
        raise ValueError(f"return packet fail: message type fail - RPAK, {message_type}")
    
    if(ret_tag != tag):
        print(f"tag fail - {tag} {ret_tag}")
        raise ValueError(f"return packet fail: tag fail - {tag}, {ret_tag}")

    if(crc != crc_check):
        print(f"crc fail - {crc} {crc_check}")
        raise ValueError(f"return packet fail: crc fail - {crc}, {crc_check}")

    if(end_bytes != 0x5678):
        print(f"end byte fail - {end_bytes}")
        raise ValueError(f"return packet fail: end byte fail - 0x5678, {end_bytes}")


def locomm_store_name_on_devide(name: str) -> bool:
    #pad name with 0x00 until it is 32 bytes
    name_padded: bytes = name.encode('ascii')
    for i in range(len(name), 32):
        name_padded += b'\x00'

    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet = craft_SNOD_packet(tag, name_padded)
        print_packet_debug(packet, True)
        LoCommGlobals.serial_conn.write(packet)
        LoCommGlobals.serial_conn.flush()

        #wait for responce
        while(not LoCommGlobals.context.SNAK_flag):
            pass

        print_packet_debug(LoCommGlobals.context.packet, False)
        check_SNAK_packet(LoCommGlobals.context.packet, tag)


    except Exception as e:
        print(f"store name on device error: {e}")
        LoCommGlobals.context.SNAK_flag = False
        return False
    
    LoCommGlobals.context.SNAK_flag = False
    return True