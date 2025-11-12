from api_funcs.LoCommAPIConnectToDevice import locomm_api_connect_to_device
from api_funcs.LoCommAPIEnterPassword import locomm_api_enter_password
from api_funcs.LoCommAPISetPassword import locomm_api_set_password
from api_funcs.LoCommAPIResetPassword import locomm_api_reset_passoword
from api_funcs.LoCommAPISendMessage import locomm_api_send_message
from api_funcs.LoCommAPIReciveMessage import locomm_api_receive_message
from api_funcs.LoCommAPIPairDevices import locomm_api_pair_devices
from api_funcs.LoCommAPIStopPair import locomm_api_stop_pair
from api_funcs.LoCommAPIDisconnectFromDevice import locomm_api_disconnect_from_device
from api_funcs.LoCommContext import LoCommContext
from api_funcs.LoCommSerailRead import serial_read
import api_funcs.LoCommGlobals as LoCommGlobals

import threading

#this function allows you to connect to a device.Returns true if connection is successful, false otherwise.
def connect_to_device() -> bool:
    ret, LoCommGlobals.serial_conn = locomm_api_connect_to_device()
    if(ret):
        LoCommGlobals.connected = True
        LoCommGlobals.context = LoCommContext()
        LoCommGlobals.serial_read_thread = threading.Thread(target=serial_read, daemon=True)
        LoCommGlobals.serial_read_thread.start()
    else:
        LoCommGlobals.connected = False
    return ret

#disconnects from the device, tells the device to overwight keys and password from memory
def disconnect_from_device() -> bool:
    ret: bool =  locomm_api_disconnect_from_device(LoCommGlobals.serial_conn, LoCommGlobals.context)
    LoCommGlobals.connected = False
    LoCommGlobals.context = None
    if LoCommGlobals.serial_read_thread is not None:
        LoCommGlobals.serial_read_thread.join()
        print("Thread stopped.")
        LoCommGlobals.serial_read_thread = None

    # Close connection
    LoCommGlobals.serial_conn.close()
    print("Connection closed")
    return True

#this function inputs the password. If the password matches the password stored on the ESP, then the function returns true, false otherwise.
def enter_password(password: str) -> bool:
    return locomm_api_enter_password(password, LoCommGlobals.serial_conn, LoCommGlobals.context)

#this function sets a new password. Returns true if successful, false otherwise.
def set_password(old: str, new: str) -> bool:
    return locomm_api_set_password(old, new, LoCommGlobals.serial_conn, LoCommGlobals.context)

#this function resets the password, this results in all your device-to-device communication keys on the ESP to be deleted. Only use it if you cannot remember the password. Returns true if successful, false otherwise
def reset_passoword(password: str) -> bool:
    return locomm_api_reset_passoword(password, LoCommGlobals.serial_conn)

#this function sends a message to the ESP to be broadcasted. Returns true if successful, false otherwise
def send_message(sender_name: str, reciver_id: int ,message: str) -> bool:
    return locomm_api_send_message(sender_name, message, LoCommGlobals.serial_conn, LoCommGlobals.context)

#this function receives messages from the ESP. Returns the name of the sender and the message -> sender_name, message.
def receive_message() -> tuple[str, str] | tuple[None, None]:
    return locomm_api_receive_message()

#these functions are not going to be in use rn
"""
#this function sends a signal to the ESP to go into pairing mode. Returns true if there was successful pairing, false otherwise.
def pair_devices() -> bool:
    return locomm_api_pair_devices()

#this function aborts the pairing process. Returns true if successful, false otherwise.
def stop_pair() -> bool:
    return locomm_api_stop_pair()

#this function deletes all the keys that are stored on the device. Returns ture if successful, false otherwise
def delete_keys() -> bool:
    return False
"""

#this function stores the name of the device on the device. returns true if successful, false if not
def store_name(name: str) -> bool:
    return True


#show pairing key
def show_pairing_key() -> bool:
    return True

#hides the pairing key (shows LoComm Devices or something)
def hide_pairing_key() -> bool:
    return True

#generate a key (don't show pairing key)
def generate_pairing_key() -> bool:
    return True


#enter a key
def enter_pairing_key(key: str) -> bool:
    return True

#delete pairing key from the device
def delete_pairing_key() -> bool:
    return True

#scan returns list of ids 
def scan_for_devices() -> list[tuple[str, int]]:
    return 