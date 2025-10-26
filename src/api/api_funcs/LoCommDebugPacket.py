import struct

def print_packet_debug(packet: bytes, sent: bool) -> None:
    start_bytes = struct.unpack(">H", packet[0:2])[0]
    packet_size = struct.unpack(">H", packet[2:4])[0]
    packet_type = struct.unpack(">4s", packet[4:8])[0]
    tag = struct.unpack(">I", packet[8:12])[0]
    message_len = packet_size - 16
    message = struct.unpack(f">{message_len}s", packet[12:12 + message_len])[0]
    crc = struct.unpack(">H", packet[-4:-2])[0]
    end_bytes = struct.unpack(">H", packet[-2:])[0]

    print(f"{'Sending' if sent else 'Receiving'} {packet_type.decode('ascii')} Packet")
    print(packet)
    print(" ".join(f"{b:02X}" for b in packet))
    print(f"Start Bytes: {hex(start_bytes)}")
    print(f"Packet Size: {packet_size}")
    print(f"Packet Type: {packet_type.decode('ascii')}")
    print(f"Tag: {hex(tag)}")
    print(f"Message: {message.decode('ascii', errors='replace')}")
    print(f"CRC: {hex(crc)}")
    print(f"End Bytes: {hex(end_bytes)}\n")
