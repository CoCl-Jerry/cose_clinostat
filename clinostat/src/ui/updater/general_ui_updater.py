import src.ui.updater.motion_ui_updater as motion_ui_updater
from PyQt5.QtGui import QPixmap, QIcon

styles = {"color": "r", "font-size": "15px"}

def update_ui_from_config(main_window, config):
    """
    Update the UI based on the provided configuration.
    """
    linked = config.get("linked", True)
    
    # Set initial icon for motion_link_toggle_pushButton
    motion_ui_updater.update_link_icon(main_window, linked)
    
    # Load saved values for spin boxes and sliders
    main_window.motion_frame_motor_value_spinBox.setValue(config.get("frame_motor_speed", 0))
    main_window.motion_core_motor_value_spinBox.setValue(config.get("core_motor_speed", 0))
    main_window.motion_frame_motor_value_verticalSlider.setValue(config.get("frame_motor_speed", 0) * 1000)
    main_window.motion_core_motor_value_verticalSlider.setValue(config.get("core_motor_speed", 0) * 1000)

    # Update motor direction icons
    motion_ui_updater.update_motor_direction_icons(main_window)

    # Load duration values for lighting presets
    main_window.lighting_preset_1_duration_value_spinBox.setValue(config.get("preset_1_duration", 1))
    main_window.lighting_preset_2_duration_value_spinBox.setValue(config.get("preset_2_duration", 1))

    # Apply saved values to the UI
    main_window.imaging_image_sequence_title_value_lineEdit.setText(config.get("imaging_image_sequence_title", ""))
    main_window.imaging_image_capture_interval_value_spinBox.setValue(config.get("imaging_image_capture_interval", 1))
    main_window.imaging_image_capture_interval_units_comboBox.setCurrentIndex(config.get("imaging_image_capture_interval_units_index", 0))
    main_window.imaging_image_sequence_duration_value_spinBox.setValue(config.get("imaging_image_sequence_duration", 1))
    main_window.imaging_image_sequence_duration_units_comboBox.setCurrentIndex(config.get("imaging_image_sequence_duration_units_index", 0))
    main_window.imaging_x_resolution_value_spinBox.setValue(config.get("imaging_x_resolution", 2592))
    main_window.imaging_y_resolution_value_spinBox.setValue(config.get("imaging_y_resolution", 2592))
    main_window.imaging_digital_zoom_horizontalSlider.setValue(config.get("imaging_zoom_level", 0))

    # Load fan speed value
    fan_speed = config.get("fan_speed", 50)
    main_window.lighting_core_fan_speed_horizontalSlider.setValue(fan_speed / 10)
    main_window.lighting_core_fan_speed_value_label.setText(f'Speed: {fan_speed}%')

    # Update ambient sensor offset values
    main_window.ambient_temperature_offset_value_doubleSpinBox.setValue(config.get("temperature_offset", 0.0))
    main_window.ambient_humidity_offset_value_doubleSpinBox.setValue(config.get("humidity_offset", 0.0))
    main_window.ambient_pressure_offset_value_doubleSpinBox.setValue(config.get("pressure_offset", 0.0))

def setup_ambient_temperature_graph(graph_widget):
    graph_widget.setBackground("#fbfbfb")
    graph_widget.showGrid(x=True, y=True)
    graph_widget.setLabel("left", "Temperature (°C)", **styles)
    graph_widget.setLabel("bottom", "Time (s)", **styles)

def setup_ambient_humidity_graph(graph_widget):
    graph_widget.setBackground("#fbfbfb")
    graph_widget.showGrid(x=True, y=True)
    graph_widget.setLabel("left", "Humidity (%)", **styles)
    graph_widget.setLabel("bottom", "Time (s)", **styles)

def setup_ambient_pressure_graph(graph_widget):
    graph_widget.setBackground("#fbfbfb")
    graph_widget.showGrid(x=True, y=True)
    graph_widget.setLabel("left", "Pressure (hPa)", **styles)
    graph_widget.setLabel("bottom", "Time (s)", **styles)

def setup_motion_accelerometer_graph(graph_widget):
    graph_widget.setBackground("#fbfbfb")
    graph_widget.showGrid(x=True, y=True)
    graph_widget.setLabel("left", "Acceleration (m/s²)", **styles)
    graph_widget.setLabel("bottom", "Time (s)", **styles)

def setup_motion_gyroscope_graph(graph_widget):
    graph_widget.setBackground("#fbfbfb")
    graph_widget.showGrid(x=True, y=True)
    graph_widget.setLabel("left", "Speed (rad/s)", **styles)
    graph_widget.setLabel("bottom", "Time (s)", **styles)

def initialize_graphs(main_window):
    setup_ambient_temperature_graph(main_window.ambient_temperature_graphWidget)
    setup_ambient_humidity_graph(main_window.ambient_humidity_graphWidget)
    setup_ambient_pressure_graph(main_window.ambient_pressure_graphWidget)
    setup_motion_accelerometer_graph(main_window.motion_accelerometer_graphWidget)
    setup_motion_gyroscope_graph(main_window.motion_gyroscope_graphWidget)

def display_image(main_window, image_data=None, image_path=None):
    """
    Display an image on the main_image_pushButton. If image_data is provided, it will be used.
    Otherwise, if image_path is provided, it will be loaded from the file.
    """
    pixmap = QPixmap()
    
    if image_data:
        pixmap.loadFromData(image_data)
    elif image_path:
        pixmap.load(image_path)
    else:
        print("No image data or path provided.")
        return
    
    # Calculate the aspect ratio and scale the dimensions
    width = pixmap.width()
    height = pixmap.height()
    if width > height:
        scaled_width = 350
        scaled_height = int((350 / width) * height)
    else:
        scaled_height = 350
        scaled_width = int((350 / height) * width)
    
    scaled_pixmap = pixmap.scaled(scaled_width, scaled_height)
    icon = QIcon(scaled_pixmap)
    main_window.main_image_pushButton.setIcon(icon)
    main_window.main_image_pushButton.setIconSize(scaled_pixmap.size())
    main_window.main_image_pushButton.setFixedSize(scaled_width, scaled_height)