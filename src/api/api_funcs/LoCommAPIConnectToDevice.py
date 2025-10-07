import serial
import time

def locomm_api_connect_to_device() -> tuple[bool, serial.Serial]:
    try:
        #TODO send CONN message and check all COM ports

        # Open connection
        ser = serial.Serial('COM3', 9600, timeout=10)
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