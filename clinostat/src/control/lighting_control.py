from src.utils.comms_utils import communication
from src.utils.lighting_utils import save_LED_command
from src.utils.general_utils import load_dynamic_config, save_dynamic_config


def send_led_command(start_led, end_led, red, green, blue, white, brightness):
    """
    Send the LED control command to the Arduino.
    """
    payload = [start_led, end_led, red, green, blue, white, brightness]
    communication.send_i2c_command(0x02, payload)
    print(f"Sent LED command: {payload}")

    # Save the command to the dynamic configuration file
    command = {
        "start_led": start_led,
        "end_led": end_led,
        "red": red,
        "green": green,
        "blue": blue,
        "white": white,
        "brightness": brightness
    }
    save_LED_command(command)

def display_led_strip():
    """
    Send the display command to the Arduino to update the LED strip.
    """
    communication.send_i2c_command(0x04, [])
    print("Sent display command")

def send_loaded_led_commands(commands):
    """
    Send the LED commands loaded from the configuration file to the Arduino.
    """
    for command in commands:
        payload = [
            command["start_led"],
            command["end_led"],
            command["red"],
            command["green"],
            command["blue"],
            command["white"],
            command["brightness"]
        ]
        communication.send_i2c_command(0x03, payload)
        print(f"Sent loaded LED command: {payload}")
    display_led_strip()

def load_preset(preset_number):
    """
    Load the preset light settings from the dynamic configuration file and apply them.
    (No popups shown)
    """
    config = load_dynamic_config()
    preset_name = f"preset_{preset_number}"
    if preset_name in config:
        preset_commands = config[preset_name]
        send_loaded_led_commands(preset_commands)
        
        # Update led_commands in the configuration file
        config["led_commands"] = preset_commands
        save_dynamic_config(config)
    else:
        # Optional: do nothing or log a warning
        print(f"Preset {preset_number} not found.")

def turn_off_all_lights():
    """
    Send the command to turn off all lights.
    """
    send_led_command(1, 130, 0, 0, 0, 0, 255)
