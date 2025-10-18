from LoCommAPI import connect_to_device
from LoCommAPI import disconnect_from_device
from LoCommAPI import receive_message
from LoCommAPI import enter_password
from LoCommAPI import set_password

import threading

stop_flag = False

def print_input():
    while not stop_flag:
        name, message = receive_message()
        print(f"{name} - {message}")


#main
while(not connect_to_device()):
    pass

enter_password("password")
#set_password("password", "admin")

disconnect_from_device()

"""
while not connect_to_device():
    pass

enter_password("admin")

disconnect_from_device()
"""

""""
thread = threading.Thread(target=print_input, daemon=True)
thread.start()

while True:
    user_input = input("Press 'q' to quit: ").strip().lower()
    if user_input == "q":
        stop_flag = True
        break

"""