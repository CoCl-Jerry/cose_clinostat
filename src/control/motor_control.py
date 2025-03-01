import math
from src.utils.comms_utils import communication
from src.utils.runtime_state import runtime_state
from src.utils.general_utils import save_dynamic_config, load_dynamic_config
from src.utils.motion_utils import calculate_motor_speed

def set_motor_speed(frame_rpm=None, core_rpm=None):
    """
    Set the motor speed for the frame and core motors.
    """
    if frame_rpm is not None:
        frame_sps, frame_microstepping = calculate_motor_speed(frame_rpm)
        runtime_state.set_motor_sps(1, frame_sps)
        runtime_state.set_motor_microstepping(1, frame_microstepping)
    if core_rpm is not None:
        core_sps, core_microstepping = calculate_motor_speed(core_rpm)
        runtime_state.set_motor_sps(2, core_sps)
        runtime_state.set_motor_microstepping(2, core_microstepping)

    frame_enabled = runtime_state.motor_states[1]["enabled"]
    core_enabled = runtime_state.motor_states[2]["enabled"]

    frame_sps_bytes = [
        (int(runtime_state.motor_states[1]["sps"] * 1000) >> 16) & 0xFF,
        (int(runtime_state.motor_states[1]["sps"] * 1000) >> 8) & 0xFF,
        int(runtime_state.motor_states[1]["sps"] * 1000) & 0xFF,
    ]
    core_sps_bytes = [
        (int(runtime_state.motor_states[2]["sps"] * 1000) >> 16) & 0xFF,
        (int(runtime_state.motor_states[2]["sps"] * 1000) >> 8) & 0xFF,
        int(runtime_state.motor_states[2]["sps"] * 1000) & 0xFF,
    ]

    payload = [
        int(frame_enabled)
    ] + frame_sps_bytes + [
        int(math.log2(runtime_state.motor_states[1]["microstepping"])),
        int(runtime_state.motor_states[1]["direction_cw"]),
        int(core_enabled)
    ] + core_sps_bytes + [
        int(math.log2(runtime_state.motor_states[2]["microstepping"])),
        int(runtime_state.motor_states[2]["direction_cw"])
    ]
    communication.send_i2c_command(0x01, payload)

    # Save the state
    config = load_dynamic_config()
    motor_states = runtime_state.motor_states
    config["frame_motor_speed"] = motor_states[1]["speed"]
    config["core_motor_speed"] = motor_states[2]["speed"]
    config["frame_motor_direction_cw"] = motor_states[1]["direction_cw"]
    config["core_motor_direction_cw"] = motor_states[2]["direction_cw"]
    config["linked"] = runtime_state.linked
    save_dynamic_config(config)