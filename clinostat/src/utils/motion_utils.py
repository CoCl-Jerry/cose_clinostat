import json
import os

# Load motor settings from the static configuration file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "../../config/static_config.json")

with open(config_path, "r") as file:
    config = json.load(file)

motor_settings = config["motor_settings"]
motor_steps = motor_settings["motor_steps"]
gear_ratio = motor_settings["gear_ratio"]
microstepping_options = motor_settings["microstepping_options"]

def calculate_motor_speed(rpm):
    best_sps, best_microstepping = None, None
    for microstepping in microstepping_options:
        steps_per_rotation = motor_steps * gear_ratio * microstepping
        sps = round((rpm * steps_per_rotation) / 60, 3)
        if 400 <= sps <= 1000 and (best_sps is None or sps < best_sps):
            best_sps, best_microstepping = sps, microstepping
    print(f"Best SPS: {best_sps}, Best Microstepping: {best_microstepping}")
    return best_sps, best_microstepping