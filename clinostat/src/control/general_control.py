from src.utils.comms_utils import communication

def audio_feedback(duration=200):
    """
    Send the 0x05 command to the Arduino to make it beep for the specified duration.
    """
    if duration > 255:
        raise ValueError("Duration must be between 0 and 255 milliseconds.")
    
    communication.send_i2c_command(0x05, [duration])
    print(f"Sent audio feedback command with duration {duration} ms")