from src.utils.general_utils import save_dynamic_config,load_dynamic_config
from src.control.general_control import audio_feedback
from src.utils.runtime_state import runtime_state
import src.control.motor_control as motor_control  # Import motor control functions
import src.ui.updater.motion_ui_updater as motion_ui_updater  # Correct import

def toggle_link_icon(main_window):
    """
    Toggle the icon on motion_link_toggle_pushButton between linked.ico and broken_link.ico.
    """
    linked = runtime_state.linked
    motion_ui_updater.update_link_icon(main_window, not linked)
    runtime_state.set_linked(not linked)
    config = load_dynamic_config()
    config["linked"] = runtime_state.linked
    save_dynamic_config(config)
    audio_feedback()  # Call audio_feedback when the icon is toggled

def toggle_motor_direction(main_window, motor_id):
    """
    Toggle the motor direction and update the button icon.
    """
    new_direction = not runtime_state.motor_states[motor_id]["direction_cw"]
    linked = runtime_state.linked
    
    if linked:
        runtime_state.set_motor_direction(1, new_direction)
        runtime_state.set_motor_direction(2, new_direction)
    else:
        runtime_state.set_motor_direction(motor_id, new_direction)
    
    motor_control.set_motor_speed(
        runtime_state.motor_states[1]["speed"],
        runtime_state.motor_states[2]["speed"]
    )
    motion_ui_updater.update_motor_direction_icons(main_window)

def toggle_motor_state(main_window, motor_id):
    """
    Toggle the motor state and update the button text.
    """
    new_state = not runtime_state.motor_states[motor_id]["enabled"]
    linked = runtime_state.linked

    if linked:
        runtime_state.set_motor_state(1, new_state)
        runtime_state.set_motor_state(2, new_state)
    else:
        runtime_state.set_motor_state(motor_id, new_state)

    motor_control.set_motor_speed(
        runtime_state.motor_states[1]["speed"],
        runtime_state.motor_states[2]["speed"]
    )
    motion_ui_updater.update_motor_button_text(main_window)

def speed_changed(main_window, motor_id, value, send_command):
    """
    Handle speed change from sliders and spin boxes.
    """
    linked = runtime_state.linked

    if linked:
        runtime_state.set_motor_speed(1, value)
        runtime_state.set_motor_speed(2, value)
    else:
        runtime_state.set_motor_speed(motor_id, value)

    motion_ui_updater.update_speed_controls(main_window)

    if send_command:
        motor_control.set_motor_speed(
            runtime_state.motor_states[1]["speed"],
            runtime_state.motor_states[2]["speed"]
        )