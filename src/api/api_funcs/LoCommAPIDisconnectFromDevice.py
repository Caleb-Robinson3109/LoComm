import serial
import random
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)

def build_DCON_packet(tag: int) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = 16
    message_type: bytes = b"DCON"

    #compute the payload to calc the crc
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", tag)
    crc: int = binascii.crc_hqx(payload, 0) 

    end_bytes: int = 0x5678

    packet: bytes = struct.pack(">HH4sIHH", start_bytes, packet_size, message_type, tag, crc, end_bytes)
    return packet

def send_recv_packet(ser: serial.Serial, packet: bytes, tag: int) -> bool:
    print(f"sending DCON packet {packet}")
    ser.write(packet)
    ser.flush()
    recv: bytes = ser.read(16)
    print(f"{recv.hex()}")
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, crc, end_bytes = struct.unpack(">HH4sIHH", recv)

    print(f"{start_bytes} {packet_size} {message_type} {ret_tag} {crc} {end_bytes}")

    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", ret_tag)
    crc_check: int = binascii.crc_hqx(payload, 0)

    #do checks on the package
    if(start_bytes != 0x1234):
        print(f"DCAK start bytes fail - 0x1234, {start_bytes}")
        return False
    
    if(packet_size != 16):
        print(f"DCAK packet size fail - 16, {packet_size}")
        return False
    
    if(message_type != b"DCAK"):
        print(f"DCAK message type fail - DCAK, {message_type}")
        return False
    
    if(ret_tag != tag):
        print(f"DCAK tag mismatch fail - {tag}, {ret_tag}")
        return False
    
    if(crc != crc_check):
        print(f"DCAK crc fail - {crc}, {crc_check}")
        return False
    
    if(end_bytes != 0x5678):
        print(f"DCAK end bytes fail - 0x5678, {end_bytes}")
        return False
    
    return True


def locomm_api_disconnect_from_device(ser: serial.Serial) -> bool:
    if ser == None:
        print(f"no serial connecton to close")
        return False

    try:
        #tell device to delete password on the device
        tag: int = random.randint(0, 0xFFFFFFFF)
        packet: bytes = build_DCON_packet(tag)


        okay: bool = send_recv_packet(ser, packet, tag)
        tries: int = 0

        while(not okay and tries < 10):
            okay = send_recv_packet(ser, packet, tag)
            print(f"try {tries + 1}")
            tries = tries + 1

        if(tries == 10 and not okay):
            raise ValueError("tried to send DCON 10 times and failed each time")

        # Close connection
        ser.close()
        print("Connection closed")

    except Exception as e:
        print(f"closing serial connection error - {e}")
        return False
    
    return True