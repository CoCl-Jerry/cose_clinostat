from src.utils.general_utils import load_static_config, open_file_dialog
from src.ui.updater import sensor_ui_updater
from src.control.sensor_control import (
    clear_old_temp_files,
    sample_ambient_data,
    sample_motion_data,
    ambient_temp_file_names,
    motion_temp_file_names,
    archived_ambient_data_list,
    archived_motion_data_list,
    recent_ambient_data_list,
    recent_motion_data_list,
)
import csv
import threading
import time
import pyqtgraph as pg
import os
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
import board
from src.utils.runtime_state import runtime_state
from src.utils.general_utils import load_dynamic_config, save_dynamic_config

# Load static configuration
static_config = load_static_config()
ambient_sensor_address = static_config["ambient_sensor_address"]

# Event to control the sampling thread
sampling_event = threading.Event()
motion_sampling_event = threading.Event()

# Define the pens
red_pen = pg.mkPen(color=(204, 0, 0), width=2)
green_pen = pg.mkPen(color=(0, 204, 0), width=2)
blue_pen = pg.mkPen(color=(0, 0, 204), width=2)

# Add a global variable to store the start time
start_time = None

def start_ambient_sensors(main_window):
    """
    Start or stop collecting data from the ambient sensors and update the UI.
    """
    global sampling_event, start_time

    if sampling_event.is_set():
        # Stop sampling
        sampling_event.clear()
        main_window.ambient_start_sensors_pushButton.setText("Start Ambient Sensors")
        print("Sampling stopped")
    else:
        # Initialize ambient sensor
        try:
            i2c = board.I2C()
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=ambient_sensor_address)
        except ValueError:
            print("Ambient sensor not connected.")
            main_window.ambient_start_sensors_pushButton.setText("Ambient Sensors not Connected")
            return

        # Clear the data lists when starting sampling
        recent_ambient_data_list.clear()
        archived_ambient_data_list.clear()
        ambient_temp_file_names.clear()

        # Clear old temporary files
        clear_old_temp_files("ambient")

        # Get the update rate from the spin box (seconds per sample)
        update_rate = main_window.ambient_sensor_rate_value_spinBox.value()  # Directly in seconds per sample

        # Print the update rate for debugging
        print(f"Update rate: {update_rate} seconds per sample")

        # Set the start time
        start_time = time.time()

        # Start sampling
        sampling_event.set()
        main_window.ambient_start_sensors_pushButton.setText("Stop Ambient Sensors")
        print("Sampling started")
        sampling_thread = threading.Thread(target=sample_ambient_data, args=(main_window, update_rate, start_time, sampling_event, bme280))
        sampling_thread.start()

def start_motion_sensors(main_window):
    """
    Start or stop collecting data from the motion sensors and update the UI.
    """
    global motion_sampling_event, start_time

    if motion_sampling_event.is_set():
        # Stop sampling
        motion_sampling_event.clear()
        main_window.motion_start_sensors_pushButton.setText("Start Motion Sensors")
        print("Motion sampling stopped")
    else:
        # Initialize motion sensor
        try:
            i2c = board.I2C()
            motion_sensor = ISM330DHCX(i2c)
        except ValueError:
            print("Motion sensor not connected.")
            main_window.motion_start_sensors_pushButton.setText("Motion Sensors not Connected")
            return

        # Clear the data lists when starting sampling
        recent_motion_data_list.clear()
        archived_motion_data_list.clear()
        motion_temp_file_names.clear()

        # Clear old temporary files
        clear_old_temp_files("motion")

        # Get the update rate from the spin box (seconds per sample)
        update_rate = 1 / main_window.motion_sensor_rate_value_spinBox.value()

        # Print the update rate for debugging
        print(f"Motion update rate: {update_rate} seconds per sample")

        # Set the start time
        start_time = time.time()

        # Start sampling
        motion_sampling_event.set()
        main_window.motion_start_sensors_pushButton.setText("Stop Motion Sensors")
        print("Motion sampling started")
        motion_sampling_thread = threading.Thread(target=sample_motion_data, args=(main_window, update_rate, start_time, motion_sampling_event, motion_sensor))
        motion_sampling_thread.start()

def update_ambient_sensor_values(main_window):
    """
    Update the sensor values based on the active tab and graph the data.
    """
    if not recent_ambient_data_list:
        return

    active_tab = main_window.ambient_sensors_tabWidget.currentIndex()
    latest_data = recent_ambient_data_list[-1]

    if active_tab == 0:  # Temperature tab
        sensor_ui_updater.update_temperature(main_window, latest_data["temperature"])
        sensor_ui_updater.update_ambient_graph(main_window.ambient_temperature_graphWidget, "temperature", red_pen, recent_ambient_data_list)
    elif active_tab == 1:  # Humidity tab
        sensor_ui_updater.update_humidity(main_window, latest_data["humidity"])
        sensor_ui_updater.update_ambient_graph(main_window.ambient_humidity_graphWidget, "humidity", green_pen, recent_ambient_data_list)
    elif active_tab == 2:  # Pressure tab
        sensor_ui_updater.update_pressure(main_window, latest_data["pressure"])
        sensor_ui_updater.update_ambient_graph(main_window.ambient_pressure_graphWidget, "pressure", blue_pen, recent_ambient_data_list)

def update_motion_sensor_values(main_window):
    """
    Update the motion sensor values based on the active tab and graph the data.
    """
    if not recent_motion_data_list:
        return

    active_tab = main_window.motion_sensors_tabWidget.currentIndex()
    latest_data = recent_motion_data_list[-1]

    if active_tab == 0:  # Acceleration tab
        sensor_ui_updater.update_acceleration(main_window, latest_data["acceleration"])
        sensor_ui_updater.update_motion_graph(main_window.motion_accelerometer_graphWidget, "acceleration", recent_motion_data_list, red_pen, green_pen, blue_pen)
    elif active_tab == 1:  # Gyro tab
        sensor_ui_updater.update_gyro(main_window, latest_data["gyro"])
        sensor_ui_updater.update_motion_graph(main_window.motion_gyroscope_graphWidget, "gyro", recent_motion_data_list, red_pen, green_pen, blue_pen)

    update_motion_axis_units(main_window, active_tab)

def update_motion_axis_units(main_window, active_tab):
    """
    Update the axis unit labels based on the active tab.
    """
    if active_tab == 0:  # Acceleration tab
        main_window.x_axis_units_text_label.setText('<html><head/><body><p><span style=" font-weight:700;">m/s</span><span style=" font-weight:700; vertical-align:super;">2</span></p></body></html>')
        main_window.y_axis_units_text_label.setText('<html><head/><body><p><span style=" font-weight:700;">m/s</span><span style=" font-weight:700; vertical-align:super;">2</span></p></body></html>')
        main_window.z_axis_units_text_label.setText('<html><head/><body><p><span style=" font-weight:700;">m/s</span><span style=" font-weight:700; vertical-align:super;">2</span></p></body></html>')
    elif active_tab == 1:  # Gyro tab
        main_window.x_axis_units_text_label.setText('<html><head/><body><p><span style=" font-weight:700;">rad/s</span></p></body></html>')
        main_window.y_axis_units_text_label.setText('<html><head/><body><p><span style=" font-weight:700;">rad/s</span></p></body></html>')
        main_window.z_axis_units_text_label.setText('<html><head/><body><p><span style=" font-weight:700;">rad/s</span></p></body></html>')

def handle_motion_tab_change(main_window):
    """
    Handle the tab change event for the motion sensors tab widget.
    """
    active_tab = main_window.motion_sensors_tabWidget.currentIndex()
    update_motion_axis_units(main_window, active_tab)

def export_ambient_sensor_data_to_csv(main_window):
    """
    Export the ambient sensor data to a CSV file.
    """
    global ambient_temp_file_names, recent_ambient_data_list, archived_ambient_data_list

    file_path = open_file_dialog(main_window, file_filter="CSV Files (*.csv);;All Files (*)", mode="data")
    if not file_path:
        return

    # Print the temp file names list
    print("Ambient temp file names before combining:", ambient_temp_file_names)

    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "temperature", "humidity", "pressure"])
        writer.writeheader()

        # Combine data from temp files
        for temp_file_path in ambient_temp_file_names:
            if os.path.exists(temp_file_path):
                with open(temp_file_path, 'r') as temp_file:
                    reader = csv.DictReader(temp_file)
                    for row in reader:
                        writer.writerow(row)

        # Append archived data
        writer.writerows(archived_ambient_data_list)
        # Append recent data
        writer.writerows(recent_ambient_data_list)

    ambient_temp_file_names.clear()
    print(f"Ambient sensor data exported to {file_path}")

def export_motion_sensor_data_to_csv(main_window):
    """
    Export the motion sensor data to a CSV file.
    """
    global motion_temp_file_names, recent_motion_data_list, archived_motion_data_list

    file_path = open_file_dialog(main_window, file_filter="CSV Files (*.csv);;All Files (*)", mode="data")
    if not file_path:
        return

    # Print the temp file names list
    print("Motion temp file names before combining:", motion_temp_file_names)

    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "x_acc", "y_acc", "z_acc", "x_gyro", "y_gyro", "z_gyro"])
        writer.writeheader()

        def write_motion_data(writer, data_list):
            for data in data_list:
                writer.writerow({
                    "timestamp": data["timestamp"],
                    "x_acc": data["acceleration"][0],
                    "y_acc": data["acceleration"][1],
                    "z_acc": data["acceleration"][2],
                    "x_gyro": data["gyro"][0],
                    "y_gyro": data["gyro"][1],
                    "z_gyro": data["gyro"][2],
                })

        # Combine data from temp files
        for temp_file_path in motion_temp_file_names:
            if os.path.exists(temp_file_path):
                with open(temp_file_path, 'r') as temp_file:
                    reader = csv.DictReader(temp_file)
                    for row in reader:
                        writer.writerow({
                            "timestamp": row["timestamp"],
                            "x_acc": row["acceleration"].strip("()").split(", ")[0],
                            "y_acc": row["acceleration"].strip("()").split(", ")[1],
                            "z_acc": row["acceleration"].strip("()").split(", ")[2],
                            "x_gyro": row["gyro"].strip("()").split(", ")[0],
                            "y_gyro": row["gyro"].strip("()").split(", ")[1],
                            "z_gyro": row["gyro"].strip("()").split(", ")[2],
                        })

        # Append archived data
        write_motion_data(writer, archived_motion_data_list)
        # Append recent data
        write_motion_data(writer, recent_motion_data_list)

    motion_temp_file_names.clear()
    print(f"Motion sensor data exported to {file_path}")

def update_ambient_offset(main_window, sensor_type):
    """
    Update the ambient sensor offset value in the runtime state and save it in the dynamic configuration.
    """
    config = load_dynamic_config()
    
    if sensor_type == "temperature":
        new_offset = main_window.ambient_temperature_offset_value_doubleSpinBox.value()
        runtime_state.set_temperature_offset(new_offset)
        config["temperature_offset"] = new_offset
    elif sensor_type == "humidity":
        new_offset = main_window.ambient_humidity_offset_value_doubleSpinBox.value()
        runtime_state.set_humidity_offset(new_offset)
        config["humidity_offset"] = new_offset
    elif sensor_type == "pressure":
        new_offset = main_window.ambient_pressure_offset_value_doubleSpinBox.value()
        runtime_state.set_pressure_offset(new_offset)
        config["pressure_offset"] = new_offset
    
    save_dynamic_config(config)