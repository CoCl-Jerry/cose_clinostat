import requests
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from src.utils.general_utils import load_static_config

# Load static configuration
static_config = load_static_config()
core_ip_address = static_config["core_ip_address"]
imaging_timeout = static_config.get("imaging_timeout", 20)  # Default to 20 seconds if not set

def send_fan_speed_command(speed, main_window=None):
    """
    Send the fan speed command to the core.
    """
    try:
        response = requests.post(f"http://{core_ip_address}:5000/fan_speed", data={'speed': speed}, timeout=5)
        if response.status_code == 200:
            print(f"Sent fan speed command: {speed}")
        else:
            print(f"Failed to send fan speed command: {response.text}")
            if main_window:
                main_window.fan_control_timeout.emit()  # Emit the timeout signal
    except Exception as e:
        print(f"Error sending fan speed command: {e}")
        if main_window:
            main_window.fan_control_timeout.emit()  # Emit the timeout signal

def send_ir_led_command(new_state):
    """
    Send the IR LED command to the core.
    """
    try:
        response = requests.post(f"http://{core_ip_address}:5000/ir_led", data={'state': new_state})
        if response.status_code == 200:
            print(f"Sent IR LED command: {new_state}")
        else:
            print(f"Failed to send ir LED command: {response.text}")
    except Exception as e:
        print(f"Error sending ir LED command: {e}")

def capture_image_command(width, height, zoom_percentage, autofocus=True, lens_position=None, main_window=None):
    """
    Send the capture image command to the core.
    """
    data = {
        'width': width,
        'height': height,
        'zoom_percentage': zoom_percentage,
        'autofocus': str(autofocus).lower()
    }
    if lens_position is not None:
        data['lens_position'] = lens_position

    try:
        response = requests.post(f"http://{core_ip_address}:5000/capture_image", data=data, timeout=imaging_timeout)
        if response.status_code == 200:
            lens_position = response.headers.get('Lens-Position')
            if lens_position:
                print(f"Lens Position: {lens_position}")
            return response.content, lens_position
        else:
            print(f"Failed to capture image: {response.text}")
            if main_window:
                main_window.image_capture_error.emit()  # Emit the error signal
            return None, None
    except requests.exceptions.Timeout:
        print("Error capturing image: No response from core (timeout).")
        if main_window:
            main_window.image_capture_error.emit()  # Emit the error signal
        return None, None
    except Exception as e:
        print(f"Error capturing image: {e}")
        if main_window:
            main_window.image_capture_error.emit()  # Emit the error signal
        return None, None

def upload_core_update(main_window):
    """
    Open a file dialog to select the core update file and upload it to the core.
    """
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Select Core Update File",
        "/media/pi",  # Default path
        "ZIP Files (*.zip)"
    )

    if not file_path:
        QMessageBox.warning(main_window, "Update Cancelled", "No file selected.")
        return

    try:
        with open(file_path, 'rb') as file:
            response = requests.post(f"http://{core_ip_address}:5000/update_code", files={'file': file})
            if response.status_code == 200:
                response_data = response.json()
                old_version = response_data.get("old_version", "unknown")
                new_version = response_data.get("new_version", "unknown")
                QMessageBox.information(main_window, "Update Successful", f"Core update uploaded successfully.\nUpdated from version {old_version} to {new_version}.")
            else:
                QMessageBox.critical(main_window, "Update Failed", f"Failed to upload core update: {response.text}")
    except Exception as e:
        QMessageBox.critical(main_window, "Update Failed", f"Error uploading core update: {e}")