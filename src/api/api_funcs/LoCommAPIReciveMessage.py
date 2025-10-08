import serial

def locomm_api_receive_message(ser: serial.Serial) -> tuple[str, str]:
    response = ser.readline()
    message: str = response.decode('utf-8').strip()
    name: str = "noname"
    return name, message