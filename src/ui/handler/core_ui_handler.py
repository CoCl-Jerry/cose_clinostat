from src.ui.updater import core_ui_updater, general_ui_updater
from src.utils.general_utils import load_static_config, load_dynamic_config, save_dynamic_config, check_storage
from src.control.core_control import send_fan_speed_command, send_ir_led_command, capture_image_command
import threading
from PyQt5.QtCore import QTimer
from src.utils.runtime_state import runtime_state
import os

# Load static configuration
static_config = load_static_config()
core_ip_address = static_config["core_ip_address"]

timelapse_timer = None
timelapse_remaining_time = 0
countdown_timer = None
countdown_time = 0
images_taken = 0
total_images = 0

def fan_speed_changed(main_window, value):
    """
    Handle the fan speed change from the slider.
    """
    core_ui_updater.update_fan_speed_label(main_window, value)

def fan_speed_released(main_window):
    """
    Handle the fan speed slider release event.
    """
    speed = main_window.lighting_core_fan_speed_horizontalSlider.value() * 10
    send_fan_speed_command(speed, main_window)
    config = load_dynamic_config()
    config["fan_speed"] = speed
    save_dynamic_config(config)

def toggle_ir_led(main_window):
    """
    Handle the IR LED toggle button click event.
    """
    current_text = main_window.lighting_IR_toggle_pushButton.text()
    if "TURN ON" in current_text:
        new_state = 1
        new_text = "TURN OFF IR LED"
    else:
        new_state = 0
        new_text = "TURN ON IR LED"

    core_ui_updater.update_ir_toggle_button(main_window, new_text)
    send_ir_led_command(new_state)

def capture_image(main_window, autofocus=False):
    """
    Handle the snapshot button click event.
    """
    def capture_and_display():
        width = main_window.imaging_x_resolution_value_spinBox.value()
        height = main_window.imaging_y_resolution_value_spinBox.value()
        zoom_percentage = main_window.imaging_digital_zoom_horizontalSlider.value()
        
        # Calculate the desired lens position from the focal length
        focal_length = main_window.main_focal_length_doubleSpinBox.value()
        lens_position = 100 / focal_length if focal_length != 0 else None
        
        image_data, lens_position = capture_image_command(width, height, zoom_percentage, autofocus, lens_position, main_window)
        if image_data:
            main_window.image_captured.emit(image_data, width, height)
            image_path = "/home/pi/Documents/clinostat/temp/captured_image.jpg"
            core_ui_updater.save_captured_image(image_data, image_path)
            runtime_state.latest_captured_image_path = image_path  # Update the latest captured image path
            print("Image captured, saved, and displayed.")
            if lens_position:
                print(f"Lens Position: {lens_position}")
                print(f"Lens Position*100: {float(lens_position) * 100}")
                focal_length = round(1 / float(lens_position) * 100, 2)
                main_window.focal_length_updated.emit(focal_length)
                print(f"Focal Length: {focal_length}")
            general_ui_updater.display_image(main_window, image_data=image_data)  # Use the new function
        main_window.main_imaging_frame.setEnabled(True)
    main_window.main_imaging_frame.setEnabled(False)
    threading.Thread(target=capture_and_display).start()

def open_image_viewer_handler(main_window):
    """
    Handle the main_image_pushButton click event to open the image in GPicView.
    """
    image_path = runtime_state.latest_captured_image_path
    if os.path.exists(image_path):
        os.system(f"xdg-open {image_path}")  # Use appropriate command for your OS
    else:
        print("No image found or the path is invalid.")

def digital_zoom_changed(main_window, value):
    """
    Handle the digital zoom slider value change event.
    """
    core_ui_updater.update_digital_zoom_label(main_window, value)

# def digital_zoom_released(main_window):
#     """
#     Handle the digital zoom slider release event.
#     """
#     capture_image(main_window)

def autofocus_and_capture(main_window):
    """
    Handle the autofocus button click event.
    """
    capture_image(main_window, autofocus=True)

def start_timelapse(main_window):
    """
    Start the timelapse functionality.
    """
    global timelapse_timer, timelapse_remaining_time, countdown_timer, countdown_time, images_taken, total_images, interval

    # Save current values to dynamic config
    config = load_dynamic_config()
    config["imaging_image_sequence_title"] = main_window.imaging_image_sequence_title_value_lineEdit.text().strip()
    config["imaging_image_capture_interval"] = main_window.imaging_image_capture_interval_value_spinBox.value()
    config["imaging_image_capture_interval_units_index"] = main_window.imaging_image_capture_interval_units_comboBox.currentIndex()
    config["imaging_image_sequence_duration"] = main_window.imaging_image_sequence_duration_value_spinBox.value()
    config["imaging_image_sequence_duration_units_index"] = main_window.imaging_image_sequence_duration_units_comboBox.currentIndex()
    config["imaging_x_resolution"] = main_window.imaging_x_resolution_value_spinBox.value()
    config["imaging_y_resolution"] = main_window.imaging_y_resolution_value_spinBox.value()
    config["imaging_zoom_level"] = main_window.imaging_digital_zoom_horizontalSlider.value()
    save_dynamic_config(config)

    # Get interval and duration values
    interval = main_window.imaging_image_capture_interval_value_spinBox.value()
    duration = main_window.imaging_image_sequence_duration_value_spinBox.value()

    # Convert interval and duration to milliseconds based on the selected units
    interval_units_index = main_window.imaging_image_capture_interval_units_comboBox.currentIndex()
    duration_units_index = main_window.imaging_image_sequence_duration_units_comboBox.currentIndex()

    if interval_units_index == 1:  # "min"
        interval *= 60 * 1000
    elif interval_units_index == 2:  # "hour"
        interval *= 3600 * 1000
    else:  # "sec"
        interval *= 1000

    if duration_units_index == 1:  # "min"
        duration *= 60 * 1000
    elif duration_units_index == 2:  # "hour"
        duration *= 3600 * 1000
    else:  # "sec"
        duration *= 1000

    timelapse_remaining_time = duration
    countdown_time = interval // 1000  # Convert milliseconds to seconds
    images_taken = 0
    total_images = duration // interval

    # Emit signal to disable frames
    main_window.disable_ui_elements.emit()

    # Capture the first image immediately
    capture_timelapse_image(main_window)

    if timelapse_timer is None:
        timelapse_timer = QTimer(main_window)
        timelapse_timer.timeout.connect(lambda: capture_timelapse_image(main_window))

    if countdown_timer is None:
        countdown_timer = QTimer(main_window)
        countdown_timer.timeout.connect(lambda: update_countdown_handler(main_window))

    timelapse_timer.start(interval)
    countdown_timer.start(1000)  # Tick every 1 second

    main_window.main_start_timelapse_pushButton.setText("STOP TIMELAPSE")
    main_window.main_start_timelapse_pushButton.clicked.disconnect()
    main_window.main_start_timelapse_pushButton.clicked.connect(lambda: stop_timelapse(main_window))

def stop_timelapse(main_window):
    """
    Stop the timelapse functionality.
    """
    global timelapse_timer, countdown_timer, images_taken

    if timelapse_timer is not None:
        timelapse_timer.stop()
        timelapse_timer = None

    if countdown_timer is not None:
        countdown_timer.stop()
        countdown_timer = None

    main_window.imaging_countdown_value_label.setText("Next Image: N/A s")
    main_window.imaging_progress_value_label.setText(f"Progress: {images_taken} / {total_images}")
    main_window.imaging_progress_progressBar.setValue(0)

    # Emit signal to enable frames
    main_window.enable_ui_elements.emit()

    main_window.main_start_timelapse_pushButton.setText("START TIMELAPSE")
    main_window.main_start_timelapse_pushButton.clicked.disconnect()
    main_window.main_start_timelapse_pushButton.clicked.connect(lambda: start_timelapse(main_window))

def capture_timelapse_image(main_window):
    """
    Capture an image for the timelapse.
    """
    global timelapse_remaining_time, images_taken, countdown_time

    if timelapse_remaining_time <= 0:
        stop_timelapse(main_window)
        return

    def capture_and_save_image():
        global images_taken, timelapse_remaining_time, countdown_time

        # Capture the image
        width = main_window.imaging_x_resolution_value_spinBox.value()
        height = main_window.imaging_y_resolution_value_spinBox.value()
        zoom_percentage = main_window.imaging_digital_zoom_horizontalSlider.value()
        
        # Calculate the desired lens position from the focal length
        focal_length = main_window.main_focal_length_doubleSpinBox.value()
        lens_position = 100 / focal_length if focal_length != 0 else None
        
        image_data, lens_position = capture_image_command(width, height, zoom_percentage, autofocus=False, lens_position=lens_position, main_window=main_window)
        
        if image_data:
            # Check storage before saving the image
            if not check_storage(main_window):
                print("Insufficient storage space. Image not saved.")
                return

            # Save the image
            config = load_dynamic_config()
            storage_directory = config.get("save_directory", "/default/path/to/storage")
            sequence_title = config.get("imaging_image_sequence_title", "sequence")
            sequence_directory = os.path.join(storage_directory, sequence_title)
            os.makedirs(sequence_directory, exist_ok=True)
            os.chmod(sequence_directory, 0o777)  # Set directory permissions

            image_number = images_taken + 1
            image_filename = f"{sequence_title}_{image_number:05d}.jpg"
            image_path = os.path.join(sequence_directory, image_filename)
            with open(image_path, "wb") as file:
                file.write(image_data)
            os.chmod(image_path, 0o777)  # Set file permissions
            
            # Emit signal to display the image on the main_image_pushButton
            main_window.image_captured.emit(image_data, width, height)
            runtime_state.latest_captured_image_path = image_path  # Update the latest captured image path
            
            images_taken += 1
            main_window.update_progress.emit(images_taken, total_images)

            # Update the remaining time and countdown
            timelapse_remaining_time -= interval
            countdown_time = interval // 1000  # Reset countdown time in seconds
    threading.Thread(target=capture_and_save_image).start()

def update_countdown(main_window):
    """
    Update the countdown timer for the next image capture.
    """
    global countdown_time

    if countdown_time > 0:
        countdown_time -= 1
        main_window.imaging_countdown_value_label.setText(f"Next Image: {countdown_time} s")
    else:
        main_window.imaging_countdown_value_label.setText("Next Image: N/A s")

def update_countdown_handler(main_window):
    """
    Decrement the global countdown_time, then emit the signal
    to update the UI with the new value.
    """
    global countdown_time, timelapse_remaining_time

    if countdown_time > 0:
        countdown_time -= 1
    main_window.update_countdown.emit(countdown_time)

    # Check if the timelapse is complete
    if timelapse_remaining_time <= 0:
        stop_timelapse(main_window)

def capture_interval_units_changed(main_window):
    """
    Handle changes to the imaging_image_capture_interval_units_comboBox.
    """
    core_ui_updater.update_capture_interval_minimum(main_window)

def sequence_duration_units_changed(main_window):
    """
    Handle changes to the imaging_image_sequence_duration_units_comboBox.
    """
    core_ui_updater.update_sequence_duration_minimum(main_window)