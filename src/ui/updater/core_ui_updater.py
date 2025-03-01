def update_fan_speed_label(main_window, value):
    """
    Update the fan speed label with the current slider value.
    """
    main_window.lighting_core_fan_speed_value_label.setText(f"Speed: {value*10}%")

def update_ir_toggle_button(main_window, new_text):
    """
    Update the IR toggle button text.
    """
    main_window.lighting_IR_toggle_pushButton.setText(new_text)

def save_captured_image(image_data, image_path):
    """
    Save the captured image to a file.
    """
    with open(image_path, "wb") as file:
        file.write(image_data)

def update_focal_length(main_window, focal_length):
    """
    Update the focal length value.
    """
    main_window.main_focal_length_doubleSpinBox.blockSignals(True)
    main_window.main_focal_length_doubleSpinBox.setValue(focal_length)
    main_window.main_focal_length_doubleSpinBox.blockSignals(False)

def update_digital_zoom_label(main_window, value):
    """
    Update the digital zoom value label.
    """
    main_window.imaging_digital_zoom_value_label.setText(f"{value} %")

def update_progress(main_window, images_taken, total_images):
    """
    Update the progress label and progress bar.
    """
    main_window.imaging_progress_value_label.setText(f"Progress: {images_taken} / {total_images}")
    progress_percentage = (images_taken / total_images) * 100
    main_window.imaging_progress_progressBar.setValue(progress_percentage)

def update_countdown(main_window, countdown_time):
    """
    Update the countdown timer for the next image capture.
    """
    if countdown_time > 0:
        main_window.imaging_countdown_value_label.setText(f"Next Image: {countdown_time} s")
    else:
        main_window.imaging_countdown_value_label.setText("Next Image: N/A s")

def disable_ui_elements(main_window):
    """
    Disable the timelapse setup and imaging settings frames.
    """
    main_window.timelapse_setup_frame.setEnabled(False)
    main_window.imaging_settings_frame.setEnabled(False)

def enable_ui_elements(main_window):
    """
    Enable the timelapse setup and imaging settings frames.
    """
    main_window.timelapse_setup_frame.setEnabled(True)
    main_window.imaging_settings_frame.setEnabled(True)

def update_capture_interval_minimum(main_window):
    """
    Update the minimum value of imaging_image_capture_interval_value_spinBox based on the selected units.
    """
    if main_window.imaging_image_capture_interval_units_comboBox.currentIndex() == 0:  # "sec"
        main_window.imaging_image_capture_interval_value_spinBox.setMinimum(5)
    else:
        main_window.imaging_image_capture_interval_value_spinBox.setMinimum(1)

def update_sequence_duration_minimum(main_window):
    """
    Update the minimum value of imaging_image_sequence_duration_value_spinBox based on the selected units.
    """
    if main_window.imaging_image_sequence_duration_units_comboBox.currentIndex() == 0:  # "sec"
        main_window.imaging_image_sequence_duration_value_spinBox.setMinimum(5)
    else:
        main_window.imaging_image_sequence_duration_value_spinBox.setMinimum(1)