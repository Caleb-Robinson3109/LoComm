import api_funcs.LoCommGlobals as LoCommGlobals

def serial_read():
    print("hello from serial read")

    while(LoCommGlobals.connected):
        #reads the input if there is bytes avil
        if(LoCommGlobals.serial_conn.in_waiting > 0):
            data: bytes = LoCommGlobals.serial_conn.read(4)
            packet_size_bytes: bytes = data[-2:]
            packet_size: int = int.from_bytes(packet_size_bytes, byteorder="big")

            data = data + LoCommGlobals.serial_conn.read(packet_size - 4)

            print("read incomming packet")

            #read the first parts of the data to figrue out wherer to send it
            message_type: bytes = data[4:8]
            print(f"message type from master: {message_type}")

            if(message_type == b"PWAK"):
                LoCommGlobals.context.packet = data
                LoCommGlobals.context.PWAK_flag = True
                
            elif(message_type == b"SPAK"):
                LoCommGlobals.context.packet = data
                LoCommGlobals.context.SPAK_flag = True
            
            elif(message_type == b"RPAK"):
                LoCommGlobals.context.packet = data
                LoCommGlobals.context.RPAK_flag = True

            elif(message_type == b"SACK"):
                LoCommGlobals.context.packet = data
                LoCommGlobals.context.SACK_flag = True

            elif(message_type == b"DCAK"):
                LoCommGlobals.context.packet = data
                LoCommGlobals.context.DCAK_flag = True

            elif(message_type == b"SEND"):
                LoCommGlobals.context.SEND_queue.put(data)

            else:
                print("ERROR - NOT RECONICED PACKET TYPE")