import queue

class LoCommContext:
    def __init__ (self):
        #these are the message type of the incomming packet
        self.PWAK_flag: bool = False
        self.SPAK_flag: bool = False
        self.RPAK_flag: bool = False
        self.SACK_flag: bool = False
        self.DCAK_flag: bool = False
        self.packet: bytes

        self.SEND_queue: queue.Queue[bytes] = queue.Queue()