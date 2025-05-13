from src.utils.general_utils import save_dynamic_config, load_dynamic_config
from src.utils.lighting_utils import save_LED_preset, clear_LED_commands
from src.control.lighting_control import send_led_command, load_preset, turn_off_all_lights
from src.ui.updater.lighting_ui_updater import reset_led_spinbox, update_lighting_cycle_ui
from PyQt5.QtCore import QTimer

def LED_confirmed(main_window):
    """
    Get the LED settings from the UI and send the command to the Arduino.
    """
    start_led = main_window.lighting_start_LED_value_spinBox.value()
    end_led = main_window.lighting_end_LED_value_spinBox.value()

    # Check the index of lighting_halo_image_label
    if main_window.lighting_source_tabWidget.currentIndex() == 1:
        start_led += 90
        end_led += 90

    red = main_window.lighting_red_value_spinBox.value()
    green = main_window.lighting_green_value_spinBox.value()
    blue = main_window.lighting_blue_value_spinBox.value()
    white = main_window.lighting_white_value_spinBox.value()
    brightness = main_window.lighting_brightness_value_spinBox.value()

    send_led_command(start_led, end_led, red, green, blue, white, brightness)

def LED_reset(main_window):
    """
    Reset the LEDs and record the default command.
    """
    clear_LED_commands()
    turn_off_all_lights()
    reset_led_spinbox(main_window)

def save_preset(preset_number):
    """
    Save the current series of lighting commands as a preset.
    """
    preset_name = f"preset_{preset_number}"
    save_LED_preset(preset_name)
    clear_LED_commands()
    turn_off_all_lights()

def start_lighting_cycle(main_window):
    """
    Start or stop the lighting cycle between preset 1 and preset 2.
    """
    if getattr(main_window, 'lighting_cycle_running', False):
        # Stop the cycle
        main_window.lighting_cycle_running = False
        
        # Stop the timer if present
        if hasattr(main_window, 'lighting_cycle_timer'):
            main_window.lighting_cycle_timer.stop()
        
        # Turn off LEDs
        turn_off_all_lights()
        
        # Update UI
        update_lighting_cycle_ui(main_window, is_running=False)
        return

    # Otherwise, start the cycle
    main_window.lighting_cycle_running = True
    
    # Store durations in seconds
    main_window.preset_1_duration = main_window.lighting_preset_1_duration_value_spinBox.value() * 60
    main_window.preset_2_duration = main_window.lighting_preset_2_duration_value_spinBox.value() * 60
    
    # Record the values in the dynamic configuration
    config = load_dynamic_config()
    config["preset_1_duration"] = main_window.lighting_preset_1_duration_value_spinBox.value()
    config["preset_2_duration"] = main_window.lighting_preset_2_duration_value_spinBox.value()
    save_dynamic_config(config)
    
    # Initialize cycle state
    main_window.current_preset = 1
    main_window.current_countdown = main_window.preset_1_duration
    
    # Load the first preset immediately
    load_preset(main_window.current_preset)
    
    # Create or reuse a QTimer that ticks every second
    if not hasattr(main_window, 'lighting_cycle_timer'):
        main_window.lighting_cycle_timer = QTimer(main_window)
    
    def cycle_tick():
        if not main_window.lighting_cycle_running:
            return
        
        main_window.current_countdown -= 1
        
        # Update the button text with the remaining time
        update_lighting_cycle_ui(main_window, is_running=True, seconds=main_window.current_countdown)
        
        # If the countdown finishes, switch presets
        if main_window.current_countdown <= 0:
            # Toggle preset
            main_window.current_preset = 2 if main_window.current_preset == 1 else 1
            load_preset(main_window.current_preset)
            
            # Reset countdown to the chosen preset's duration
            if main_window.current_preset == 1:
                main_window.current_countdown = main_window.preset_1_duration
            else:
                main_window.current_countdown = main_window.preset_2_duration
    
    main_window.lighting_cycle_timer.timeout.disconnect() if main_window.lighting_cycle_timer.receivers(main_window.lighting_cycle_timer.timeout) else None
    main_window.lighting_cycle_timer.timeout.connect(cycle_tick)
    main_window.lighting_cycle_timer.start(1000)  # Tick every 1 second
    
    # Update UI to reflect running state
    update_lighting_cycle_ui(main_window, is_running=True, seconds=main_window.current_countdown)