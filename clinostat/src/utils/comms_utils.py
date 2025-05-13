import smbus2
from smbus2 import i2c_msg
import serial
import time
import json
import threading
from src.utils.core_utils import handle_handshake_response

with open("/home/pi/Documents/clinostat/config/static_config.json", "r") as file:
    static_config = json.load(file)

def calculate_crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

class Communication:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Communication, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, bus_id=1):
        if not hasattr(self, 'initialized'):  # Ensure __init__ is only called once
            self.bus = smbus2.SMBus(bus_id)
            self.address = static_config["i2c_address"]
            self.serial_port = serial.Serial(
                port=static_config["uart_port"], 
                baudrate=static_config["baudrate"], 
                timeout=static_config["timeout"]
            )
            self.initialized = True
            self.listener_thread = threading.Thread(target=self.listen_for_response)
            self.listener_thread.daemon = True
            self.listener_thread_running = True
            self.listener_thread.start()
            self.response_handlers = {}

    def send_i2c_command(self, command, payload):
        packet = [0xFF, len(payload) + 1, command] + payload
        crc = calculate_crc16(packet)
        packet.append((crc >> 8) & 0xFF)
        packet.append(crc & 0xFF)
        try:
            write = i2c_msg.write(self.address, packet)
            self.bus.i2c_rdwr(write)
            time.sleep(0.1)
        except Exception as e:
            print(f"I2C Error: {e}")
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.i2c_communication_error.emit()  # Emit the error signal
                print("I2C communication error emitted.")

    def send_uart_data(self, data):
        try:
            self.serial_port.write(data.encode())
        except Exception as e:
            print(f"UART Error: {e}")

    def read_uart_data(self):
        try:
            data = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
            return data
        except Exception as e:
            print(f"UART Read Error: {e}")
            return ""

    def listen_for_response(self):
        start_time = time.time()
        while self.listener_thread_running and (time.time() - start_time < 10):
            try:
                response = self.read_uart_data()
                if response:
                    received_data, received_crc = response.rsplit(',', 1)
                    received_crc = int(received_crc.split('=')[1], 16)
                    calculated_crc = calculate_crc16(received_data.encode('utf-8'))
                    if calculated_crc == received_crc:
                        print("CRC validation successful.")
                        response_type = received_data.split(',')[0]
                        if response_type in self.response_handlers:
                            self.response_handlers[response_type](received_data)
                            if response_type == "HANDSHAKE_RESPONSE":
                                self.listener_thread_running = False  # Stop the listener thread
                        else:
                            print(f"No handler for response type: {response_type}")
                    else:
                        print("CRC mismatch. Data may be corrupted.")
                else:
                    print("No response received.")
            except Exception as e:
                print(f"Error processing response: {e}")
        if time.time() - start_time >= 10:
            print("UART connection not established.")

    def add_response_handler(self, response_type, handler):
        self.response_handlers[response_type] = handler

    def close(self):
        self.listener_thread_running = False
        self.listener_thread.join()
        self.serial_port.close()
        self.bus.close()

# Create a single instance of the Communication class
communication = Communication()
communication.add_response_handler("HANDSHAKE_RESPONSE", handle_handshake_response)
