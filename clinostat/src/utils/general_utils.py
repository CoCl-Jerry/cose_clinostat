import os
import json
import shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QStandardPaths
from src.utils.runtime_state import runtime_state
import src.ui.updater.general_ui_updater as general_ui_updater

# Define the constant path to the motion configuration file
DYNAMIC_CONFIG_PATH = "/home/pi/Documents/clinostat/config/dynamic_config.json"

# Define the constant path to the static configuration file
STATIC_CONFIG_PATH = "/home/pi/Documents/clinostat/config/static_config.json"

def load_static_config():
    """
    Load the static configuration from the JSON file.
    """
    if os.path.exists(STATIC_CONFIG_PATH):
        with open(STATIC_CONFIG_PATH, "r") as file:
            config = json.load(file)
        return config
    else:
        raise FileNotFoundError(f"Static configuration file not found: {STATIC_CONFIG_PATH}")

def load_dynamic_config():
    """
    Load the dynamic configuration from the JSON file.
    """
    if os.path.exists(DYNAMIC_CONFIG_PATH):
        with open(DYNAMIC_CONFIG_PATH, "r") as file:
            config = json.load(file)
        return config
    else:
        return {}

def save_dynamic_config(config):
    """
    Save the dynamic configuration to the JSON file.
    """
    with open(DYNAMIC_CONFIG_PATH, "w") as file:
        json.dump(config, file, indent=4)
    
    print(config)

def update_runtime_state_from_config(config):
    runtime_state.set_motor_speed(1, config.get("frame_motor_speed", 1.00))
    runtime_state.set_motor_speed(2, config.get("core_motor_speed", 1.00))
    runtime_state.set_motor_direction(1, config.get("frame_motor_direction_cw", True))
    runtime_state.set_motor_direction(2, config.get("core_motor_direction_cw", True))
    runtime_state.set_linked(config.get("linked", True))
    runtime_state.set_temperature_offset(config.get("temperature_offset", 0.0))
    runtime_state.set_humidity_offset(config.get("humidity_offset", 0.0))
    runtime_state.set_pressure_offset(config.get("pressure_offset", 0.0))

def open_file_dialog(main_window, file_filter="All Files (*)", mode="open"):
    """
    Open a file dialog to select a file or directory and load or save the settings.
    """
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    
    # Load the dynamic configuration to get the save_directory
    config = load_dynamic_config()
    save_directory = config.get("save_directory", QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
    
    if mode == "open":
        file_name, _ = QFileDialog.getOpenFileName(main_window, "Open File", save_directory, file_filter, options=options)
        if file_name:
            load_settings_from_file(main_window, file_name)
    elif mode == "save":
        file_name, _ = QFileDialog.getSaveFileName(main_window, "Save File", save_directory, file_filter, options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    config = load_dynamic_config()
                    json.dump(config, file, indent=4)
                QMessageBox.information(main_window, "Success", "Configuration saved successfully.")
            except Exception as e:
                QMessageBox.critical(main_window, "Error", f"Failed to save configuration: {e}")
        return file_name  # Return the selected file path
    elif mode == "data":
        file_name, _ = QFileDialog.getSaveFileName(main_window, "Save Data File", save_directory, "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name and not file_name.endswith(".csv"):
            file_name += ".csv"
        return file_name  # Return the selected file path
    elif mode == "directory":
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory", save_directory, options=options)
        if directory:
            config["save_directory"] = directory
            save_dynamic_config(config)
            QMessageBox.information(main_window, "Success", "Storage directory updated successfully.")
            main_window.ui_state_manager.validate_timelapse_settings()  # Call validate_timelapse_settings

def load_settings_from_file(main_window, file_name):
    """
    Load settings from the selected JSON file and apply them.
    """
    from src.control.lighting_control import send_loaded_led_commands
    try:
        with open(file_name, 'r') as file:
            config = json.load(file)
            # Save the loaded configuration to dynamic_config.json
            with open(DYNAMIC_CONFIG_PATH, 'w') as dynamic_config_file:
                json.dump(config, dynamic_config_file, indent=4)
            
            # Update runtime state
            update_runtime_state_from_config(config)
            
            # Update UI
            general_ui_updater.update_ui_from_config(main_window, config)
            
            # Send LED commands to the Arduino
            if "led_commands" in config:
                send_loaded_led_commands(config["led_commands"])
            
            QMessageBox.information(main_window, "Success", "Configuration loaded and saved successfully.")
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to load configuration: {e}")

def check_storage(main_window):
    """
    Check the available storage and print the value in MB.
    Display storage_error.png if the available storage is less than the critical storage value.
    Return True if the available storage is larger than the critical storage value in static config, False otherwise.
    """
    total, used, free = shutil.disk_usage("/")
    free_mb = free // (2**20)  # Convert bytes to MB
    print(f"Available storage: {free_mb} MB")

    static_config = load_static_config()
    critical_storage_value = static_config.get("critical_storage_value", 500)  # Default to 500 MB if not set

    if free_mb < critical_storage_value:
        general_ui_updater.display_image(main_window, image_path="/home/pi/Documents/clinostat/src/assets/images/storage_error.png")
        return False

    return True