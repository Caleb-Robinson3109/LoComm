from LoCommAPI import *
import threading

recv = True

def recv_thread():
    while(recv):
        name, message, id = receive_message()
        print(f"{id} {name}: {message}")

#run_deviceless_mode()

i = 0
while(not connect_to_device()):
    i = i + 1
    if i == 10:
        raise ValueError(f"tried to connect to device {i} times")

enter_password("password")
store_name_on_device("Bob")
enter_pairing_key('aaaabbbbccccddddeeee')
#print(f"{scan_for_devices()}")

t =threading.Thread(target=recv_thread)
t.start()

print("enter message or press q to stop")
while True:
    cmd = input()
    if cmd.strip().lower() == 'q':
        recv = False
        disconnect_from_device()
        break
    else:
        send_message("Bob", 210, cmd)

t.join()
