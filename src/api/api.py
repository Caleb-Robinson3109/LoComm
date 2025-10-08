from LoCommAPI import connect_to_device
from LoCommAPI import disconnect_from_device
from LoCommAPI import receive_message

connect_to_device()
name, message = receive_message()
print(f"{name} - {message}")
disconnect_from_device()
