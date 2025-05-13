import os
import time
import csv
import threading

from src.utils.general_utils import load_static_config
from src.utils.comms_utils import communication
from src.utils.runtime_state import runtime_state  # Import runtime_state

# Load static configuration
static_config = load_static_config()
ambient_sensor_address = static_config["ambient_sensor_address"]
MAX_AMBIENT_RECENT_DATA_POINTS = static_config["max_ambient_recent_data_points"]
MAX_AMBIENT_ARCHIVED_DATA_POINTS = static_config["max_ambient_archived_data_points"]
MAX_MOTION_RECENT_DATA_POINTS = static_config["max_motion_recent_data_points"]
MAX_MOTION_ARCHIVED_DATA_POINTS = static_config["max_motion_archived_data_points"]

# Global lists to store temporary file names and data
ambient_temp_file_names = []
motion_temp_file_names = []
archived_ambient_data_list = []
archived_motion_data_list = []
recent_ambient_data_list = []
recent_motion_data_list = []

def clear_old_temp_files(file_type):
    global ambient_temp_file_names, motion_temp_file_names
    """
    Clear old temporary files starting with 'ambient_sensor_data' or 'motion_sensor_data'.
    """
    temp_dir = "/home/pi/Documents/clinostat/temp"
    if os.path.exists(temp_dir):
        for temp_file in os.listdir(temp_dir):
            if file_type == "ambient" and temp_file.startswith("ambient_sensor_data") and temp_file.endswith(".csv"):
                os.remove(os.path.join(temp_dir, temp_file))
            elif file_type == "motion" and temp_file.startswith("motion_sensor_data") and temp_file.endswith(".csv"):
                os.remove(os.path.join(temp_dir, temp_file))

def sample_ambient_data(main_window, update_rate, start_time, sampling_event, bme280, max_retries=10):
    global ambient_temp_file_names, archived_ambient_data_list, recent_ambient_data_list
    """
    Sample data from the sensor and add it to the lists.
    """
    clear_old_temp_files("ambient")  # Clear old ambient temp files at the start
    retry_count = 0

    while sampling_event.is_set():
        try:
            # Read data from the sensor
            elapsed_time = round(time.time() - start_time, 3)  # Calculate elapsed time in seconds and round to 3 decimal places
            temperature = round(bme280.temperature + runtime_state.temperature_offset, 3)
            humidity = round(bme280.relative_humidity + runtime_state.humidity_offset, 3)
            pressure = round(bme280.pressure + runtime_state.pressure_offset, 3)

            # Add data to the recent_data_list
            recent_ambient_data_list.append({"timestamp": elapsed_time, "temperature": temperature, "humidity": humidity, "pressure": pressure})

            # If recent_data_list exceeds the maximum size, move the oldest data point to archived_data_list
            if len(recent_ambient_data_list) > MAX_AMBIENT_RECENT_DATA_POINTS:
                archived_ambient_data_list.append(recent_ambient_data_list.pop(0))

            # If archived_ambient_data_list exceeds the maximum size, save it to a temporary CSV file and clear the list
            if len(archived_ambient_data_list) >= MAX_AMBIENT_ARCHIVED_DATA_POINTS:
                threading.Thread(target=save_archived_data_to_csv, args=("ambient_sensor_data",)).start()

            # Emit the custom signal to update the UI
            main_window.new_ambient_sensor_data.emit()

            # Wait for the specified update rate in 1-second intervals
            elapsed_time = 0
            while elapsed_time < update_rate and sampling_event.is_set():
                time.sleep(1)
                elapsed_time += 1

            # Reset retry count after a successful read
            retry_count = 0
        except OSError as e:
            if e.errno == 121:  # Remote I/O error
                print("Ambient sensor not connected.")
                retry_count += 1
                if retry_count >= max_retries:
                    sampling_event.clear()
                    main_window.ambient_sensor_error.emit()
                    break
                else:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    time.sleep(1)  # Wait before retrying

def sample_motion_data(main_window, update_rate, start_time, motion_sampling_event, motion_sensor, max_retries=10):
    global motion_temp_file_names, archived_motion_data_list, recent_motion_data_list
    """
    Sample data from the motion sensor and add it to the lists.
    """
    clear_old_temp_files("motion")  # Clear old motion temp files at the start
    retry_count = 0

    while motion_sampling_event.is_set():
        try:
            # Read data from the motion sensor
            elapsed_time = round(time.time() - start_time, 3)  # Calculate elapsed time in seconds
            acceleration = tuple(round(val, 3) for val in motion_sensor.acceleration)
            gyro = tuple(round(val, 3) for val in motion_sensor.gyro)

            # Add data to the recent_motion_data_list
            recent_motion_data_list.append({"timestamp": elapsed_time, "acceleration": acceleration, "gyro": gyro})

            # If recent_motion_data_list exceeds the maximum size, move the oldest data point to archived_motion_data_list
            if len(recent_motion_data_list) > MAX_MOTION_RECENT_DATA_POINTS:
                archived_motion_data_list.append(recent_motion_data_list.pop(0))

            # If archived_motion_data_list exceeds the maximum size, save it to a temporary CSV file and clear the list
            if len(archived_motion_data_list) >= MAX_MOTION_ARCHIVED_DATA_POINTS:
                threading.Thread(target=save_archived_data_to_csv, args=("motion_sensor_data",)).start()

            # Emit the custom signal to update the UI
            main_window.new_motion_sensor_data.emit()

            # Wait for the specified update rate in 1-second intervals
            elapsed_time = 0
            while elapsed_time < update_rate and motion_sampling_event.is_set():
                time.sleep(0.01)
                elapsed_time += 0.01

            # Reset retry count after a successful read
            retry_count = 0
        except OSError as e:
            if e.errno == 121:  # Remote I/O error
                print("Motion sensor not connected.")
                retry_count += 1
                if retry_count >= max_retries:
                    motion_sampling_event.clear()
                    main_window.motion_sensor_error.emit()
                    break
                else:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    time.sleep(1)  # Wait before retrying

def save_archived_data_to_csv(prefix):
    global ambient_temp_file_names, motion_temp_file_names, archived_ambient_data_list, archived_motion_data_list
    """
    Save the archived data to a temporary CSV file and clear the list.
    """
    # Define the temporary file path
    temp_dir = "/home/pi/Documents/clinostat/temp"
    temp_file_path = os.path.join(temp_dir, f"{prefix}_{int(time.time())}.csv")

    # Ensure the temp directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Save the archived data to the temporary CSV file
    with open(temp_file_path, mode='w', newline='') as file:
        if prefix == "ambient_sensor_data":
            writer = csv.DictWriter(file, fieldnames=["timestamp", "temperature", "humidity", "pressure"])
            writer.writeheader()
            writer.writerows(archived_ambient_data_list)
            ambient_temp_file_names.append(temp_file_path)
            archived_ambient_data_list.clear()
        else:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "acceleration", "gyro"])
            writer.writeheader()
            writer.writerows(archived_motion_data_list)
            motion_temp_file_names.append(temp_file_path)
            archived_motion_data_list.clear()

    # Print the directory where the temporary file is saved
    print(f"Temporary file saved: {temp_file_path}")