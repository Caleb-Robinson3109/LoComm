from LoCommAPI import *

while(not connect_to_device()):
    pass
enter_password("password")
#send_message("name", "Hello from python")
disconnect_from_device()
