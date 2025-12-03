import queue

class LoCommContext:
    def __init__ (self):
        #these are the message type of the incomming packet
        self.PWAK_flag: bool = False
        self.SPAK_flag: bool = False
        self.RPAK_flag: bool = False
        self.SACK_flag: bool = False
        self.DCAK_flag: bool = False
        self.SNAK_flag: bool = False
        self.EPAK_flag: bool = False
        self.packet: bytes

        self.SEND_flag: bool = False
        self.SEND_packet: bytes | None = None
        self.SEND_message: str | None = None
        self.SEND_name: str | None = None
        self.SEND_return: bool = False