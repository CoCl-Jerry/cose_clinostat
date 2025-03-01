from src.utils.general_utils import load_dynamic_config, update_runtime_state_from_config, check_storage
import src.ui.updater.general_ui_updater as general_ui_updater
from src.utils.comms_utils import communication  # Import the communication instance
from src.utils.lighting_utils import clear_LED_commands  # Correct import
from src.utils.comms_utils import calculate_crc16  # Import the calculate_crc16 function

styles = {"color": "r", "font-size": "15px"}

def initialize_runtime_state():
    """
    Initialize the runtime state based on the motion configuration.
    """
    config = load_dynamic_config()
    update_runtime_state_from_config(config)

def initialize_ui(main_window):
    """
    Initialize the UI based on the motion configuration.
    """
    # Load motion configuration
    config = load_dynamic_config()
    
    # Update the UI from the configuration
    general_ui_updater.update_ui_from_config(main_window, config)

    # Read version number from version.txt using an absolute path
    version_file_path = "/home/pi/Documents/clinostat/version.txt"
    try:
        with open(version_file_path, "r") as file:
            version_number = file.read().strip()
            main_window.setWindowTitle(f"Clinostat Control Center v{version_number}")
    except FileNotFoundError:
        print("Error: version.txt file not found.")
        main_window.setWindowTitle("Clinostat Control Center vUnknown")

def initialize_hardware():
    """
    Initialize hardware components.
    """
    # Send reset command to Arduino
    communication.send_i2c_command(0x00, [])
    clear_LED_commands()

    # Send handshake message
    handshake_message = "HANDSHAKE"
    crc = calculate_crc16(handshake_message.encode('utf-8'))
    handshake_message_with_crc = f"{handshake_message},CRC={crc:04X}"
    communication.send_uart_data(handshake_message_with_crc)
    print(f"Sent UART handshake message: {handshake_message_with_crc}")

def startup(main_window):
    """
    Perform all startup tasks.
    """
    
    initialize_runtime_state()
    initialize_ui(main_window)
    initialize_hardware()
    general_ui_updater.initialize_graphs(main_window)
    check_storage(main_window)
    # Add any other startup tasks here