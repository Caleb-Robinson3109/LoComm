from api_funcs.LoCommAPIConnectToDevice import locomm_api_connect_to_device
from api_funcs.LoCommAPIEnterPassword import locomm_api_enter_password
from api_funcs.LoCommAPISetPassword import locomm_api_set_password
from api_funcs.LoCommAPIResetPassword import locomm_api_reset_passoword
from api_funcs.LoCommAPISendMessage import locomm_api_send_message
from api_funcs.LoCommAPIReciveMessage import locomm_api_receive_message
from api_funcs.LoCommAPIPairDevices import locomm_api_pair_devices
from api_funcs.LoCommAPIStopPair import locomm_api_stop_pair
from api_funcs.LoCommAPIDisconnectFromDevice import locomm_api_disconnect_from_device

import serial

serial_conn: serial.Serial | None = None

#this function allows you to connect to a device.Returns true if connection is successful, false otherwise.
def connect_to_device() -> bool:
    global serial_conn
    ret, serial_conn = locomm_api_connect_to_device()
    return ret

def disconnect_from_device() -> bool:
    global serial_conn
    return locomm_api_disconnect_from_device(serial_conn)

#this function inputs the password. If the password matches the password stored on the ESP, then the function returns true, false otherwise.
def enter_password(password: str) -> bool:
    global serial_conn
    return locomm_api_enter_password(password, serial_conn)

#this function sets a new password. Returns true if successful, false otherwise.
def set_password(old: str, new: str) -> bool:
    global serial_conn
    return locomm_api_set_password(old, new, serial_conn)

#this function resets the password, this results in all your device-to-device communication keys on the ESP to be deleted. Only use it if you cannot remember the password. Returns true if successful, false otherwise
def reset_passoword(password: str) -> bool:
    return locomm_api_reset_passoword(password)

#this function sends a message to the ESP to be broadcasted. Returns true if successful, false otherwise
def send_message(name: str, message: str) -> bool:
    return locomm_api_send_message(name, message)

#this function receives messages from the ESP. Returns the name of the sender and the message -> name, message.
def receive_message() -> tuple[str, str]:
    global serial_conn
    return locomm_api_receive_message(serial_conn)

#this function sends a signal to the ESP to go into pairing mode. Returns true if there was successful pairing, false otherwise.
def pair_devices() -> bool:
    return locomm_api_pair_devices()

#this function aborts the pairing process. Returns true if successful, false otherwise.
def stop_pair() -> bool:
    return locomm_api_stop_pair()