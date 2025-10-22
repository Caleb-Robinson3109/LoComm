import serial
import threading
from api_funcs.LoCommContext import LoCommContext

connected: bool = False
serial_conn: serial.Serial | None = None
context: LoCommContext | None = None
serial_read_thread = None | threading.Thread