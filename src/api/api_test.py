from LoCommAPI import *
import threading

recv = True

def recv_thread():
    while(recv):
        name, message = receive_message()
        print(f"{name}: {message}")

while(not connect_to_device()):
    pass
enter_password("password")

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
        send_message("test name", cmd)

t.join()
