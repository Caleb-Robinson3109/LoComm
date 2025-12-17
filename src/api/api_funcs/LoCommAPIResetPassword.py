import serial
import random #for gen random tag
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)
from api_funcs.LoCommContext import LoCommContext
from api_funcs.LoCommDebugPacket import print_packet_debug

def craft_RSPW_packet(tag: int, password: str) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = len(password) + 16
    message_type: bytes = b"STPW"
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

def check_SPAK_packet(packet: bytes, tag: int) -> None:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4sI4sHH", packet)

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
        raise ValueError(f"return packet fail: message type fail - SPAK, {message_type}")
    
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


def check_RSPW_packet(packet: bytes, tag: int) -> None:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: bytes
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, crc, end_bytes = struct.unpack(">HH4sIHH", packet)

    #crc calc
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", ret_tag)
    crc_check: int = binascii.crc_hqx(payload, 0)

    #some part of the packet is wrong, so try again 
    if(start_bytes != 0x1234):
        print(f"start byte fail - {start_bytes}")
        raise ValueError(f"return packet fail: start byte fail - 0x1234, {start_bytes}")
    
    if(packet_size != 20):
        print(f"packet size fail - {packet_size}")
        raise ValueError(f"return packet fail: packet size fail - 20, {packet_size}")
    
    if(message_type != b"RPAK"):
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


def locomm_api_reset_passoword(password: str, ser: serial.Serial, context: LoCommContext) -> bool:
    try:
        tag: int = random.randint(0, 0xFFFFFFFF)
        print("crafting rspw packet")
        packet = craft_RSPW_packet(tag, password)
        print_packet_debug(packet, True)
        ser.write(packet)
        ser.flush()

        print("sent rspw packet")
        #wait for responce
        while(not context.SPAK_flag):
            pass

        print("spak response received")
        print_packet_debug(context.packet, False)
        #check_RSPW_packet(packet, tag)
        print("checking spack packet")
        check_SPAK_packet(context.packet, tag)
        print("finished checking spak packet")

    except Exception as e:
        print(f"reset password enter error: {e}")
        context.SPAK_flag = False
        return False
    
    context.SPAK_flag = False
    return True