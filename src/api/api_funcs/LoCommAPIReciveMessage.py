import api_funcs.LoCommGlobals as LoCommGlobals
import struct
import binascii
import time

def locomm_api_receive_message() -> tuple[str, str] | tuple[None, None] | None:
    #check the state of the recive message
    if(LoCommGlobals.context.SEND_return):
        LoCommGlobals.context.SEND_message = None
        LoCommGlobals.context.SEND_name = None
        LoCommGlobals.context.SEND_return = False

    #get message
    try:
        while(not LoCommGlobals.context.SEND_flag and LoCommGlobals.connected):
            time.sleep(0.01)

        #if the device disconnected stop trying
        if(not LoCommGlobals.connected):
            return (None, None)
        
        #unpack send message
        start_bytes: int
        packet_size: int
        packet_type: bytes
        tag: int
        id: int
        total_packet: int
        curr_packet: int
        name_len: int
        message_len: int
        name_b: bytes
        message_b: bytes
        crc: int
        end_bytes: int
        
        start_bytes, packet_size, packet_type, tag, id, total_packet, curr_packet, name_len, message_len = struct.unpack(">HH4sIBHHBH", LoCommGlobals.context.SEND_packet[:20])
        name_b, message_b, crc, end_bytes = struct.unpack(f">{name_len}s{message_len}sHH",LoCommGlobals.context.SEND_packet[20:])

        #check SEND packet
        if(start_bytes != 0x1234):
            raise ValueError(f"start bytes fail 0x1234, {start_bytes}")
        if(packet_size != len(LoCommGlobals.context.SEND_packet)):
            raise ValueError(f"packet size fail, {len(LoCommGlobals.context.SEND_packet)}, {packet_size}")
        if(packet_type != b"SEND"):
            raise ValueError(f"packet type fail SEND, {packet_type}")
        if(name_len != len(name_b)):
            raise ValueError(f"name lenght fail {len(name_b)}, {name_len}")
        if(message_len != len(message_b)):
            raise ValueError(f"message lenght fail {len(message_b)}, {message_len}")

        payload:bytes = struct.pack(f">H4sIBHHBH{name_len}s{message_len}s", packet_size, packet_type, tag, id, total_packet, curr_packet, name_len, message_len, name_b, message_b)
        crc_check: int = binascii.crc_hqx(payload, 0)

        if(crc != crc_check):
            raise ValueError(f"crc failed {crc_check}, {crc}")
        if(end_bytes != 0x5678):
            raise ValueError(f"end bytes fail 0x5678, {end_bytes}")

        #handle the information in the send
        if(LoCommGlobals.context.SEND_name == None and name_len != 0):
            LoCommGlobals.context.SEND_name = name_b.decode('ascii')

        if(LoCommGlobals.context.SEND_message == None):
            LoCommGlobals.context.SEND_message = message_b.decode('ascii')
        else:
            LoCommGlobals.context.SEND_message += message_b.decode('ascii')

        if(curr_packet == total_packet):
            LoCommGlobals.context.SEND_return = True   

        #build SACK
        sack_payload: bytes = struct.pack(">H4sIH", 18, b"SACK", tag, curr_packet)
        sack_crc = binascii.crc_hqx(sack_payload, 0)
        SACK_packet: bytes = struct.pack(">HH4sIHHH", 0x1234, 18, b"SACK", tag, curr_packet, sack_crc, 0x5678)

        #TODO fix the ack sending
        #send sack
        #LoCommGlobals.serial_conn.write(SACK_packet)
        #LoCommGlobals.serial_conn.flush()

        #if the message is complete then send if if not wait for more messages
    except Exception as e:
        print(f"Receive Message Error: {e}")
        if(LoCommGlobals.context != None):
            LoCommGlobals.context.SEND_flag = False
        if hasattr(locals(), "total_packet") and hasattr(locals(), "curr_packet"):
            if total_packet == curr_packet:
                LoCommGlobals.context.SEND_return = True
                return LoCommGlobals.context.SEND_name, LoCommGlobals.context.SEND_message

    #return if needed
    if(LoCommGlobals.context != None and LoCommGlobals.context.SEND_return):
        LoCommGlobals.context.SEND_flag = False
        return LoCommGlobals.context.SEND_name, LoCommGlobals.context.SEND_message
    elif(LoCommGlobals.context != None):
        LoCommGlobals.context.SEND_flag = False
        return None, None
    else:
        return None, None