import serial
import time

def test_serial():
    try:
        # Open connection
        ser = serial.Serial('COM3', 9600, timeout=10)
        print(f"Connected to {ser.name}")
        
        # Wait for device initialization
        time.sleep(1)
        
        # Read response
        response = ser.readline()
        print(f"Received: {response.decode('utf-8').strip()}")
        
        # Close connection
        ser.close()
        print("Connection closed")
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except FileNotFoundError:
        print("Port not found - check device connection")
    except PermissionError:
        print("Permission denied - see troubleshooting guide")

if __name__ == "__main__":
    test_serial()