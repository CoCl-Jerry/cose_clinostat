import os
from src.utils.general_utils import load_dynamic_config

class UIStateManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def validate_timelapse_settings(self):
        """
        Validate the timelapse settings and enable/disable the start timelapse button.
        """
        title = self.main_window.imaging_image_sequence_title_value_lineEdit.text().strip()
        interval = self.main_window.imaging_image_capture_interval_value_spinBox.value()
        duration = self.main_window.imaging_image_sequence_duration_value_spinBox.value()

        # Check the units for interval and duration
        interval_units_index = self.main_window.imaging_image_capture_interval_units_comboBox.currentIndex()
        duration_units_index = self.main_window.imaging_image_sequence_duration_units_comboBox.currentIndex()

        # Convert interval and duration to seconds if necessary
        if interval_units_index == 1:  # "min"
            interval *= 60
        elif interval_units_index == 2:  # "hour"
            interval *= 3600

        if duration_units_index == 1:  # "min"
            duration *= 60
        elif duration_units_index == 2:  # "hour"
            duration *= 3600

        if not title:
            self.main_window.main_start_timelapse_pushButton.setEnabled(False)
            self.main_window.imaging_directory_value_label.setText("Sequence Title Required")
        elif interval > duration:
            self.main_window.imaging_directory_value_label.setText("Duration Must be Greater Than Interval")
        else:
            self.main_window.main_start_timelapse_pushButton.setEnabled(True)
            config = load_dynamic_config()
            storage_directory = config.get("save_directory", "/default/path/to/storage")  # Replace with the actual default path if needed
            subdirectory = os.path.join(storage_directory, title)
            self.main_window.imaging_directory_value_label.setText(subdirectory)

        # Calculate the number of images to be taken
        if interval > 0:
            num_images = duration // interval
        else:
            num_images = 0

        self.main_window.imaging_progress_value_label.setText(f"Progress: 0 / {num_images}")