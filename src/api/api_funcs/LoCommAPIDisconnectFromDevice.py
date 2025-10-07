import serial

def locomm_api_disconnect_from_device(ser: serial.Serial) -> bool:
    if ser == None:
        print(f"no serial connecton to close")
        return False

    try:
        # Close connection
        ser.close()
        print("Connection closed")

    except Exception as e:
        print(f"closing serial connection error - {e}")
        return False
    
    return True