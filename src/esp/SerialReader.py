import serial
import threading
import sys

def read_from_port(ser):
    """Continuously read from serial port and print incoming data."""
    try:
        while True:
            data = ser.readline().decode(errors='ignore').strip()
            if data:
                print(f"\r<< {data}\n>> ", end="", flush=True)
    except serial.SerialException:
        print("\nConnection lost.")
    except Exception as e:
        print(f"\nError reading: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python serial_terminal.py <COM_PORT> [BAUD_RATE]")
        sys.exit(1)

    port = sys.argv[1]
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 9600

    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"Connected to {port} at {baud} baud.")
        print("Type messages and press Enter to send. Ctrl+C to exit.\n")

        # Start background thread for reading
        reader_thread = threading.Thread(target=read_from_port, args=(ser,), daemon=True)
        reader_thread.start()

        # Main loop for sending data
        while True:
            msg = input(">> ")
            if msg:
                ser.write((msg + "\n").encode())
    except KeyboardInterrupt:
        print("\nClosing connection...")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
