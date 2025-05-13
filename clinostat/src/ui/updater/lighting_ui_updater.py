import os
import json
from src.control.lighting_control import send_led_command as send_led_cmd

def reset_led_spinbox(main_window):
    """
    Read the LED settings from the JSON configuration file and set the values to the UI.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "../../../config/static_config.json")
    
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
        
        led_settings = config["led_settings"]
        main_window.lighting_start_LED_value_spinBox.setValue(led_settings["default_start_led"])
        main_window.lighting_end_LED_value_spinBox.setValue(led_settings["default_end_led"])
        main_window.lighting_red_value_spinBox.setValue(led_settings["default_red"])
        main_window.lighting_green_value_spinBox.setValue(led_settings["default_green"])
        main_window.lighting_blue_value_spinBox.setValue(led_settings["default_blue"])
        main_window.lighting_white_value_spinBox.setValue(led_settings["default_white"])
        main_window.lighting_brightness_value_spinBox.setValue(led_settings["default_brightness"])
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the configuration file: {config_path}")

def update_lighting_cycle_ui(main_window, is_running, seconds=None):
    """
    Update the UI for the lighting cycle.
    """
    if is_running and seconds is not None:
        main_window.lighting_confirm_cycle_pushButton.setText(f"STOP ({seconds} s)")
        main_window.lighting_LED_frame.setEnabled(False)
        main_window.lighting_MISC_frame.setEnabled(False)
        main_window.lighting_preset_1_duration_value_spinBox.setEnabled(False)
        main_window.lighting_preset_2_duration_value_spinBox.setEnabled(False)
    else:
        main_window.lighting_confirm_cycle_pushButton.setText("CONFIRM CYCLE")
        main_window.lighting_LED_frame.setEnabled(True)
        main_window.lighting_MISC_frame.setEnabled(True)
        main_window.lighting_preset_1_duration_value_spinBox.setEnabled(True)
        main_window.lighting_preset_2_duration_value_spinBox.setEnabled(True)
        send_led_cmd(1, 130, 0, 0, 0, 0, 255)  # Turn off all LEDs

def update_preset_durations(main_window, preset_1_duration, preset_2_duration):
    """
    Update the preset duration spin boxes.
    """
    main_window.lighting_preset_1_duration_value_spinBox.setValue(preset_1_duration)
    main_window.lighting_preset_2_duration_value_spinBox.setValue(preset_2_duration)

def update_lighting_spinboxes(main_window, index):
    """
    Update the lighting spin boxes based on the selected tab index.
    """
    if index == 0:
        main_window.lighting_start_LED_value_spinBox.setValue(1)
        main_window.lighting_start_LED_value_spinBox.setMaximum(90)
        main_window.lighting_end_LED_value_spinBox.setMaximum(90)
        main_window.lighting_end_LED_value_spinBox.setValue(90)
    elif index == 1:
        main_window.lighting_start_LED_value_spinBox.setValue(1)
        main_window.lighting_start_LED_value_spinBox.setMaximum(40)
        main_window.lighting_end_LED_value_spinBox.setMaximum(40)
        main_window.lighting_end_LED_value_spinBox.setValue(40)
