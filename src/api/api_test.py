from LoCommAPI import connect_to_device
from LoCommAPI import disconnect_from_device
from LoCommAPI import receive_message
from LoCommAPI import enter_password
from LoCommAPI import set_password

while(not connect_to_device()):
    pass
enter_password("password")
set_password("password", "admin")
disconnect_from_device()
connect_to_device()
enter_password("admin")
set_password("admin", "password")
disconnect_from_device()