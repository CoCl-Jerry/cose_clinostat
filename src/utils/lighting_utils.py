from src.utils.general_utils import load_dynamic_config, save_dynamic_config

def save_LED_command(command):
    """
    Save the LED command to the dynamic configuration file.
    """
    config = load_dynamic_config()
    if "led_commands" not in config:
        config["led_commands"] = []
    config["led_commands"].append(command)
    save_dynamic_config(config)

def clear_LED_commands():
    """
    Clear all LED commands from the dynamic configuration file.
    """
    config = load_dynamic_config()
    config["led_commands"] = []
    save_dynamic_config(config)

def save_LED_preset(preset_name):
    """
    Save the current series of lighting commands as a preset.
    """
    config = load_dynamic_config()
    if "led_commands" in config:
        config[preset_name] = config["led_commands"]
        save_dynamic_config(config)
        print(f"Saved preset: {preset_name}")

def update_preset_durations(main_window, preset_1_duration, preset_2_duration):
    """
    Update the preset duration spin boxes.
    """
    main_window.lighting_preset_1_duration_value_spinBox.setValue(preset_1_duration)
    main_window.lighting_preset_2_duration_value_spinBox.setValue(preset_2_duration)