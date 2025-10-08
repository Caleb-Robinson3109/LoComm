import serial
import serial.tools.list_ports
import time

def locomm_api_connect_to_device() -> tuple[bool, serial.Serial]:
    try:
        #get list of open ports
        ports: list[serial.tools.list_ports.ListPortInfo] = serial.tools.list_ports.comports()

        #iterates though open ports to see witch ones responds correctory to our CONN request
        conn_port: str
        for port in ports:
            #send conn and wait for responce
            print("conn port - " + port.name)
            conn_port = port.name


        ser = serial.Serial(conn_port, 9600, timeout=10)
        print(f"Connected to {ser.name}")
        
        # Wait for device initialization
        time.sleep(1)
        
        #Read response
        #response = ser.readline()
        #print(f"Received: {response.decode('utf-8').strip()}")
        
        
    except Exception as e:
        print(f"Serial error: {e}")
        return False, None
    
    return True, ser