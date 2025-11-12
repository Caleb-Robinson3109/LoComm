import serial
import serial.tools.list_ports
import time #sleep
import random #for gen random tag
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)
from api_funcs.LoCommDebugPacket import print_packet_debug

def craft_CONN_packet(tag: int) -> bytes:
    start_bytes: int = 0x1234
    packet_size: int = 20
    message_type: bytes = b"CONN"
    message: int  = int(time.time())
    #compute checksum for payload
    payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", tag) + struct.pack(">I", message)
    crc: int = binascii.crc_hqx(payload, 0)
    
    end_bytes: int = 0x5678

    packet: bytes = struct.pack(">HH4sIHH", start_bytes, packet_size, message_type, tag, crc, end_bytes)

    return packet

def locomm_api_connect_to_device() -> tuple[bool, serial.Serial | None]:
    try:
        #get list of open ports
        ports: list[serial.tools.list_ports.ListPortInfo] = serial.tools.list_ports.comports()

        #iterates though open ports to see witch ones responds correctory to our CONN request
        conn_port: str = None
        #for _ in range(2):
        for port in ports:
            #send conn and wait for responce
            print("try conn port - " + port.name)

            tag: int = random.randint(0, 0xFFFFFFFF)
            packet: bytes = craft_CONN_packet(tag)
            try:
                ser = serial.Serial(port=port.name, baudrate=115200, timeout=10) #Adjust timout if it is not connection on first try -> make longer
            except Exception as e:
                print(f"{e}")
                continue
            #let ser init in device
            print_packet_debug(packet, True)
            ser.write(packet)
            ser.flush()
            #wait for responce timeout defined in ser def
            data: bytes = ser.read(16)
            print("Meow 1")
            print(data)
            print(len(data))
            print_packet_debug(data, False)
            #check to make sure that SACK has been sent the SACK should be 14 bytes long
            if len(data) == 16:
                start_bytes: int
                packet_size: int
                message_type: bytes
                ret_tag: int
                crc: int
                end_bytes: int 
                start_bytes, packet_size, message_type, ret_tag, crc, end_bytes = struct.unpack(">HH4sIHH", data)

                #crc calc
                payload: bytes = struct.pack(">H", packet_size) + message_type + struct.pack(">I", ret_tag)
                crc_check: int = binascii.crc_hqx(payload, 0)

                #check all of the recived parts are valid
                if start_bytes != 0x1234:
                    print("fail at start bytes")
                    ser.close()
                    continue
                if message_type != b"CACK":
                    print(f"fail at message type - {message_type}")
                    ser.close()
                    continue
                if ret_tag != tag:
                    print("fail at tag")
                    ser.close()
                    continue
                if crc != crc_check:
                    print("fail at crc")
                    ser.close()
                    continue
                if end_bytes != 0x5678:
                    print("fail at end bytes")
                    ser.close()
                    continue

                #all the checks pass this is the correct COM port
                conn_port: str = port.name
                ser.close()
                break
            ser.close()


        if conn_port == None:
            raise ValueError("no COM ports found with device")

        ser = serial.Serial(conn_port, 115200, timeout=None)
        print(f"Connected to {ser.name}")
        
        # Wait for device initialization
        time.sleep(2)   
        
    except Exception as e:
        print(f"Serial error: {e}")
        return False, None
    
    return True, ser