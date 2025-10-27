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

print("press q to stop")
while True:
    cmd = input().strip().lower()
    if cmd == 'q':
        recv = False
        disconnect_from_device()
        break

t.join()
