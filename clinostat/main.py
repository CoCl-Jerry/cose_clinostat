import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from src.ui.source import clinostat_ui
from src.utils.startup import startup  # Import startup function
from src.utils.general_utils import open_file_dialog  # Import utility functions
import src.ui.handler.lighting_ui_handler as lighting_ui_handlers  # Import lighting UI handlers
import src.ui.handler.motion_ui_handler as motion_ui_handlers  # Import motion UI handlers
import src.ui.handler.core_ui_handler as core_ui_handlers  # Import core UI handlers
from src.ui.updater.lighting_ui_updater import update_lighting_spinboxes
from src.control.lighting_control import load_preset  # Import load_preset function
from src.ui.updater import core_ui_updater
from src.ui.handler.ui_state_manager import UIStateManager
from src.ui.handler import sensor_ui_handler
from src.control.core_control import upload_core_update
import subprocess
from src.ui.updater import general_ui_updater

class MainWindow(QMainWindow, clinostat_ui.Ui_MainWindow):
    image_captured = pyqtSignal(bytes, int, int)
    focal_length_updated = pyqtSignal(float)
    update_progress = pyqtSignal(int, int)  # Signal to update progress
    update_countdown = pyqtSignal(int)      # Signal to update countdown
    disable_ui_elements = pyqtSignal()      # Signal to disable UI elements
    enable_ui_elements = pyqtSignal()       # Signal to enable UI elements
    new_ambient_sensor_data = pyqtSignal()  # Define the custom signal
    new_motion_sensor_data = pyqtSignal()   # Define the custom signal for motion sensor data
    motion_sensor_error = pyqtSignal()      # Define the custom signal for motion sensor error
    ambient_sensor_error = pyqtSignal()     # Define the custom signal for ambient sensor error
    image_capture_error = pyqtSignal()      # Define the custom signal for image capture error
    fan_control_timeout = pyqtSignal()      # Define the custom signal for fan control timeout


    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Set the working directory to the directory containing the UI file
        ui_file_dir = os.path.dirname(os.path.abspath(clinostat_ui.__file__))
        os.chdir(ui_file_dir)
        
        self.setupUi(self)

        # Perform startup tasks
        startup(self)
        self.ui_state_manager = UIStateManager(self)
        self.ui_state_manager.validate_timelapse_settings()
        # Connect UI signals to handlers
        self.setup_signals()

        # Show the window maximized
        self.showMaximized()

    def setup_signals(self):
        """
        Connect UI signals to their respective handlers.
        """
        # Motor control signals
        self.motion_frame_motor_toggle_pushButton.clicked.connect(
            lambda: motion_ui_handlers.toggle_motor_state(self, 1)
        )
        self.motion_core_motor_toggle_pushButton.clicked.connect(
            lambda: motion_ui_handlers.toggle_motor_state(self, 2)
        )
        self.motion_link_toggle_pushButton.clicked.connect(lambda: motion_ui_handlers.toggle_link_icon(self))
        self.motion_frame_motor_reverse_pushButton.clicked.connect(
            lambda: motion_ui_handlers.toggle_motor_direction(self, 1)
        )
        self.motion_core_motor_reverse_pushButton.clicked.connect(
            lambda: motion_ui_handlers.toggle_motor_direction(self, 2)
        )
        self.motion_frame_motor_value_spinBox.valueChanged.connect(
            lambda value: motion_ui_handlers.speed_changed(self, 1, value, True)
        )
        self.motion_core_motor_value_spinBox.valueChanged.connect(
            lambda value: motion_ui_handlers.speed_changed(self, 2, value, True)
        )
        self.motion_frame_motor_value_verticalSlider.valueChanged.connect(
            lambda value: motion_ui_handlers.speed_changed(self, 1, value / 1000, False)
        )
        self.motion_core_motor_value_verticalSlider.valueChanged.connect(
            lambda value: motion_ui_handlers.speed_changed(self, 2, value / 1000, False)
        )
        self.motion_frame_motor_value_verticalSlider.sliderReleased.connect(
            lambda: motion_ui_handlers.speed_changed(self, 1, self.motion_frame_motor_value_verticalSlider.value() / 1000, True)
        )
        self.motion_core_motor_value_verticalSlider.sliderReleased.connect(
            lambda: motion_ui_handlers.speed_changed(self, 2, self.motion_core_motor_value_verticalSlider.value() / 1000, True)
        )

        # Lighting control signals
        self.lighting_LED_confirm_pushButton.clicked.connect(lambda: lighting_ui_handlers.LED_confirmed(self))
        self.lighting_LED_reset_pushButton.clicked.connect(lambda: lighting_ui_handlers.LED_reset(self))
        self.lighting_save_preset_1_pushButton.clicked.connect(lambda: lighting_ui_handlers.save_preset(1))
        self.lighting_save_preset_2_pushButton.clicked.connect(lambda: lighting_ui_handlers.save_preset(2))
        self.lighting_load_preset_1_pushButton.clicked.connect(lambda: load_preset(1))
        self.lighting_load_preset_2_pushButton.clicked.connect(lambda: load_preset(2))
        self.lighting_core_fan_speed_horizontalSlider.valueChanged.connect(
            lambda value: core_ui_handlers.fan_speed_changed(self, value)
        )
        self.lighting_core_fan_speed_horizontalSlider.sliderReleased.connect(
            lambda: core_ui_handlers.fan_speed_released(self)
        )
        self.lighting_IR_toggle_pushButton.clicked.connect(
            lambda: core_ui_handlers.toggle_ir_led(self)
        )
        self.lighting_confirm_cycle_pushButton.clicked.connect(lambda: lighting_ui_handlers.start_lighting_cycle(self))

        self.lighting_source_tabWidget.currentChanged.connect(lambda: update_lighting_spinboxes(self, self.lighting_source_tabWidget.currentIndex()))

        # Snapshot button signal
        self.main_snapshot_pushButton.clicked.connect(
            lambda: core_ui_handlers.capture_image(self)
        )

        # Autofocus button signal
        self.main_autofocus_pushButton.clicked.connect(
            lambda: core_ui_handlers.autofocus_and_capture(self)
        )

        # Image button signal
        self.main_image_pushButton.clicked.connect(
            lambda: core_ui_handlers.open_image_viewer_handler(self)
        )

        # Digital zoom slider signals
        self.imaging_digital_zoom_horizontalSlider.valueChanged.connect(
            lambda value: core_ui_handlers.digital_zoom_changed(self, value)
        )
        # self.imaging_digital_zoom_horizontalSlider.sliderReleased.connect(
        #     lambda: core_ui_handlers.digital_zoom_released(self)
        # )

        self.main_focal_length_doubleSpinBox.valueChanged.connect(
            lambda value: core_ui_updater.update_focal_length(self, value)
        )

        self.main_start_timelapse_pushButton.clicked.connect(
            lambda: core_ui_handlers.start_timelapse(self)
        )

        # Connect signals for timelapse validation
        self.imaging_image_sequence_title_value_lineEdit.textChanged.connect(
            self.ui_state_manager.validate_timelapse_settings
        )
        self.imaging_image_capture_interval_value_spinBox.valueChanged.connect(
            self.ui_state_manager.validate_timelapse_settings
        )
        self.imaging_image_sequence_duration_value_spinBox.valueChanged.connect(
            self.ui_state_manager.validate_timelapse_settings
        )
        self.imaging_image_capture_interval_units_comboBox.currentIndexChanged.connect(
            self.ui_state_manager.validate_timelapse_settings
        )
        self.imaging_image_sequence_duration_units_comboBox.currentIndexChanged.connect(
            self.ui_state_manager.validate_timelapse_settings
        )

        # Connect the combo box change signals to the handler functions
        self.imaging_image_capture_interval_units_comboBox.currentIndexChanged.connect(
            lambda: core_ui_handlers.capture_interval_units_changed(self)
        )
        self.imaging_image_sequence_duration_units_comboBox.currentIndexChanged.connect(
            lambda: core_ui_handlers.sequence_duration_units_changed(self)
        )

        # File dialog signals
        self.actionLoad_Configurations.triggered.connect(lambda: open_file_dialog(self, "JSON Files (*.json);;All Files (*)"))
        self.actionSave_Configurations.triggered.connect(lambda: open_file_dialog(self, "JSON Files (*.json);;All Files (*)", mode="save"))
        self.actionStorage_Directory.triggered.connect(lambda: open_file_dialog(self, mode="directory"))
        self.actionUpdate_Controller.triggered.connect(self.run_update_script)
        self.actionFactory_Reset.triggered.connect(self.run_factory_reset)
        self.actionUpdate_Core.triggered.connect(self.update_core)

        # Connect custom signals to slots
        self.image_captured.connect(lambda image_data: general_ui_updater.display_image(self, image_data=image_data))
        self.focal_length_updated.connect(lambda focal_length: core_ui_updater.update_focal_length(self, focal_length))
        self.update_progress.connect(lambda images_taken, total_images: core_ui_updater.update_progress(self, images_taken, total_images))
        self.update_countdown.connect(lambda countdown_time: core_ui_updater.update_countdown(self, countdown_time))
        self.disable_ui_elements.connect(lambda: core_ui_updater.disable_ui_elements(self))
        self.enable_ui_elements.connect(lambda: core_ui_updater.enable_ui_elements(self))

        # Connect ambient sensor start button
        self.ambient_start_sensors_pushButton.clicked.connect(lambda: sensor_ui_handler.start_ambient_sensors(self))
        # Connect ambient sensor export CSV button
        self.ambient_sensor_export_CSV_pushButton.clicked.connect(lambda: sensor_ui_handler.export_ambient_sensor_data_to_csv(self))
        # Connect the custom signal to the update_sensor_values function
        self.new_ambient_sensor_data.connect(lambda: sensor_ui_handler.update_ambient_sensor_values(self))
        # Connect the tab change signal to update the graph
        self.ambient_sensors_tabWidget.currentChanged.connect(lambda: sensor_ui_handler.update_ambient_sensor_values(self))

        # Connect motion sensor start button
        self.motion_start_sensors_pushButton.clicked.connect(lambda: sensor_ui_handler.start_motion_sensors(self))
        # Connect motion sensor export CSV button
        self.motion_sensor_export_CSV_pushButton.clicked.connect(lambda: sensor_ui_handler.export_motion_sensor_data_to_csv(self))
        # Connect the custom signal to the update_motion_sensor_values function
        self.new_motion_sensor_data.connect(lambda: sensor_ui_handler.update_motion_sensor_values(self))
        # Connect the tab change signal to update the graph
        self.motion_sensors_tabWidget.currentChanged.connect(lambda: sensor_ui_handler.update_motion_sensor_values(self))

        # Connect the custom signal to update the button text
        self.motion_sensor_error.connect(lambda: self.motion_start_sensors_pushButton.setText("Motion Sensors not Connected"))
        self.ambient_sensor_error.connect(lambda: self.ambient_start_sensors_pushButton.setText("Ambient Sensors not Connected"))

        # Connect the clicked signals to the update_ambient_offset function
        self.ambient_confirm_temperature_offset_pushButton.clicked.connect(lambda: sensor_ui_handler.update_ambient_offset(self, "temperature"))
        self.ambient_confirm_humidity_offset_pushButton.clicked.connect(lambda: sensor_ui_handler.update_ambient_offset(self, "humidity"))
        self.ambient_confirm_pressure_offset_pushButton.clicked.connect(lambda: sensor_ui_handler.update_ambient_offset(self, "pressure"))

        # Connect the custom signal to the error handler
        self.image_capture_error.connect(lambda: general_ui_updater.display_image(self, image_path="/home/pi/Documents/clinostat/src/assets/images/camera_error.png"))
        self.fan_control_timeout.connect(lambda: general_ui_updater.display_image(self, image_path="/home/pi/Documents/clinostat/src/assets/images/core_error.png"))

    def run_update_script(self):
        result = subprocess.run(["sudo", "python3", "/home/pi/Documents/clinostat/update.py"], check=True)
        if result.returncode == 0:
            self.close()

    def run_factory_reset(self):
        result = subprocess.run(["sudo", "python3", "/home/pi/Documents/clinostat/update.py", "/home/pi/Documents/backups/clinostat.zip"], check=True)
        if result.returncode == 0:
            self.close()

    def update_core(self):
        upload_core_update(self)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
