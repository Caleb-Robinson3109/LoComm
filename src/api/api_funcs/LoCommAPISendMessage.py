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

def check_SACK_packet(packet: bytes, tag: int, total_packets: int, packet_num: int) -> tuple[str, bool]:
    start_bytes: int
    packet_size: int
    message_type: bytes
    ret_tag: int
    message: int #we know the message will only contain the chunk number so we set it to int
    crc: int
    end_bytes: int

    start_bytes, packet_size, message_type, ret_tag, message, crc, end_bytes = struct.unpack(">HH4sIHHH")

    if start_bytes != 0x1234:
        return f"start bytes error 0x1234, {start_bytes}", False
    
    if packet_size != 18:
        return f"packet size error 18, {packet_size}", False
    
    if message_type != b"SACK":
        return f"message type error SACK, {message_type}", False
    
    if ret_tag != tag:
        return f"tag mismatch {tag}, {ret_tag}", False
    
    if packet_num != message:
        return f"packet number error {packet_num}, {message}", False
    
    payload: bytes = struct.pack(">H4sIH", packet_size, message_type, tag, message)
    crc_check: int = binascii.crc_hqx(payload, 0)

    if crc_check != crc:
        return f"crc fail {crc}, {crc_check}", False
    
    if end_bytes != 0x5678:
        return f"end bytes fail 0x5678, {end_bytes}"

def locomm_api_send_message(name: str, message: str, ser: serial.Serial) -> bool:
    #split the message into 1000 char chucnks and send each chunk (same tag)
    tag: int = random.randint(0, 0xFFFFFFFF)
    total_packets = math.ceil(len(message) / 1000)
    
    for i in range (total_packets):
        #for each chucnk also checks if its the last chunk
        chunk: str = message[i * 1000 : (i+1) * 1000] if i != total_packets else message[i * 1000 : len(message)]
        
        #build packet
        packet: bytes = craft_SEND_packet(tag, name, chunk, total_packets, i)

        #send_recv_packet
        try:
            print(f"sending pacaket - {packet}")
            ser.write(packet)
            ser.flush()
            recv: bytes = ser.read(18)
            error_code: str
            send_status: bool
            error_code, send_status = check_SACK_packet(recv, tag, total_packets, i)
            if(not send_status):
                raise ValueError(f"FAIL send of packet {i}/{total_packets} - error: {error_code}")
        except Exception as e:
            print(f"Serial error when sending message: {e}")
            return False

    return True
