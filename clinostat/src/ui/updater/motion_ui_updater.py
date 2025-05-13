from PyQt5.QtGui import QIcon
import os
from src.utils.runtime_state import runtime_state

def update_link_icon(main_window, linked):
    """
    Update the icon on motion_link_toggle_pushButton based on the current state.
    """
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/icons')
    icon_path = os.path.join(icons_dir, 'linked.ico' if linked else 'broken_link.ico')
    main_window.motion_link_toggle_pushButton.setIcon(QIcon(icon_path))

def update_motor_button_text(main_window):
    """
    Update the text on the motor toggle buttons based on the runtime status of the motors.
    """
    frame_motor_state = runtime_state.motor_states[1]["enabled"]
    core_motor_state = runtime_state.motor_states[2]["enabled"]
    
    main_window.motion_frame_motor_toggle_pushButton.setText("DISABLE MOTOR" if frame_motor_state else "ENABLE MOTOR")
    main_window.motion_core_motor_toggle_pushButton.setText("DISABLE MOTOR" if core_motor_state else "ENABLE MOTOR")

def update_motor_direction_icons(main_window):
    """
    Update the icons on the motor direction buttons based on the runtime direction of the motors.
    """
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/icons')
    frame_direction_cw = runtime_state.motor_states[1]["direction_cw"]
    core_direction_cw = runtime_state.motor_states[2]["direction_cw"]

    frame_icon = 'clockwise.ico' if frame_direction_cw else 'counter_clockwise.ico'
    core_icon = 'clockwise.ico' if core_direction_cw else 'counter_clockwise.ico'

    main_window.motion_frame_motor_reverse_pushButton.setIcon(QIcon(os.path.join(icons_dir, frame_icon)))
    main_window.motion_core_motor_reverse_pushButton.setIcon(QIcon(os.path.join(icons_dir, core_icon)))

def update_speed_controls(main_window):
    """
    Update the sliders and spin boxes to reflect the new speeds.
    """
    frame_speed = runtime_state.motor_states[1]["speed"]
    core_speed = runtime_state.motor_states[2]["speed"]

    # Block signals to prevent triggering valueChanged
    main_window.motion_frame_motor_value_spinBox.blockSignals(True)
    main_window.motion_core_motor_value_spinBox.blockSignals(True)
    main_window.motion_frame_motor_value_verticalSlider.blockSignals(True)
    main_window.motion_core_motor_value_verticalSlider.blockSignals(True)

    main_window.motion_frame_motor_value_spinBox.setValue(frame_speed)
    main_window.motion_core_motor_value_spinBox.setValue(core_speed)
    main_window.motion_frame_motor_value_verticalSlider.setValue(int(frame_speed * 1000))
    main_window.motion_core_motor_value_verticalSlider.setValue(int(core_speed * 1000))

    # Unblock signals after updating values
    main_window.motion_frame_motor_value_spinBox.blockSignals(False)
    main_window.motion_core_motor_value_spinBox.blockSignals(False)
    main_window.motion_frame_motor_value_verticalSlider.blockSignals(False)
    main_window.motion_core_motor_value_verticalSlider.blockSignals(False)

    print(f"Updated speed controls: Frame motor speed: {frame_speed}, Core motor speed: {core_speed}")