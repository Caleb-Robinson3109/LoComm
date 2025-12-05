import api_funcs.LoCommGlobals as LoCommGlobals

def serial_read():
    print("hello from serial read")

    buffer = bytearray()

    while LoCommGlobals.connected:
        if LoCommGlobals.serial_conn.in_waiting > 0:
            # read all available bytes
            chunk = LoCommGlobals.serial_conn.read(LoCommGlobals.serial_conn.in_waiting)
            print(f"Received chunk: {chunk}")
            buffer.extend(chunk)

            # Try to process packets as long as we have enough data
            while True:
                # We need at least 4 bytes to know the size
                if len(buffer) < 4:
                    break

                # Get packet size from last 2 bytes of the header
                packet_size_bytes = buffer[2:4]
                packet_size = int.from_bytes(packet_size_bytes, "big")

                # Wait until we have a full packet
                if len(buffer) < packet_size:
                    break

                # Extract a full packet
                packet = buffer[:packet_size]
                del buffer[:packet_size]

                print(f"Got full packet ({len(packet)} bytes): {packet}")

                # Extract type and handle it
                message_type = packet[4:8]
                print(f"message type from master: {message_type}")

                if message_type == b"PWAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.PWAK_flag = True

                elif message_type == b"SPAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.SPAK_flag = True

                elif message_type == b"RPAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.RPAK_flag = True

                elif message_type == b"SACK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.SACK_flag = True

                elif message_type == b"DCAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.DCAK_flag = True

                elif message_type == b"SEND":
                    LoCommGlobals.context.SEND_packet = packet
                    LoCommGlobals.context.SEND_flag = True

                elif message_type == b"SNAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.SNAK_flag = True

                elif message_type == b"EPAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.EPAK_flag = True
                
                elif message_type == b"SCAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.SKAK_flag = True

                elif message_type == b"GPAK":
                    LoCommGlobals.context.packet = packet
                    LoCommGlobals.context.GPAK_flag = True
   

                else:
                    print("ERROR - NOT RECOGNIZED PACKET TYPE")
