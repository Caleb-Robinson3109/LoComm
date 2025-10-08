import serial
import serial.tools.list_ports
import time #sleep
import random #for gen random tag
import struct #creation of the packet
import binascii #crc-16 (crc_hqx)

def craft_CONN_packet(tag: int) -> bytes:
    start_bytes: int = 0x1234
    message_type: bytes = b"CONN"
    
    #compute checksum for payload
    payload: bytes = message_type + struct.pack(">I", tag)
    crc: int = binascii.crc_hqx(payload, 0)
    
    end_bytes: int = 0x5678

    packet: bytes = struct.pack(">H4sIHH", start_bytes, message_type, tag, crc, end_bytes)

    return packet

def locomm_api_connect_to_device() -> tuple[bool, serial.Serial | None]:
    try:
        #get list of open ports
        ports: list[serial.tools.list_ports.ListPortInfo] = serial.tools.list_ports.comports()

        #iterates though open ports to see witch ones responds correctory to our CONN request
        conn_port: str = None
        for port in ports:
            #send conn and wait for responce
            print("try conn port - " + port.name)

            tag: int = random.randint(0, 0xFFFFFFFF)
            packet: bytes = craft_CONN_packet(tag)

            ser = serial.Serial(port, 9600, timeout=5)

            # Wait for device initialization (if there is one lol)
            time.sleep(1)  

            ser.write(packet)

            #wait for responce timeout defined in ser def
            data: bytes = ser.read(14)

            #check to make sure that SACK has been sent the SACK should be 14 bytes long
            if len(data) == 14:
                start_bytes: int
                message_type: bytes
                ret_tag: int
                crc: int
                end_bytes: int 
                start_bytes, message_type, ret_tag, crc, end_bytes = struct.unpack(">H4sIHH", data)

                #crc calc
                payload: bytes = message_type + struct.pack(">I", ret_tag)
                crc_check: int = binascii.crc_hqx(payload, 0)

                #check all of the recived parts are valid
                if start_bytes != 0x1234:
                    ser.close()
                    continue
                if message_type != b"SACK":
                    ser.close()
                    continue
                if ret_tag != tag:
                    ser.close()
                    continue
                if crc != crc_check:
                    ser.close()
                    continue
                if end_bytes != 0x5678:
                    ser.close()
                    continue

                #all the checks pass this is the correct COM port
                conn_port = port.name
                ser.close()
                break


        if conn_port == None:
            raise ValueError("no COM ports found with device")

        ser = serial.Serial(conn_port, 9600, timeout=None)
        print(f"Connected to {ser.name}")
        
        # Wait for device initialization
        time.sleep(1)   
        
    except Exception as e:
        print(f"Serial error: {e}")
        return False, None
    
    return True, ser