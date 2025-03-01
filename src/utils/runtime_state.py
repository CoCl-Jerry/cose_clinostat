class RuntimeState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RuntimeState, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Ensure __init__ is only called once
            self.motor_states = {
                1: {"speed": 0, "direction_cw": True, "enabled": False, "sps": 0, "microstepping": 1},
                2: {"speed": 0, "direction_cw": True, "enabled": False, "sps": 0, "microstepping": 1},
            }
            self.linked = True
            self.temperature_offset = 0.0
            self.humidity_offset = 0.0
            self.pressure_offset = 0.0
            self.latest_captured_image_path = ""
            self.initialized = True

    def set_motor_speed(self, motor_id, speed):
        if motor_id in self.motor_states:
            self.motor_states[motor_id]["speed"] = speed

    def set_motor_direction(self, motor_id, direction_cw):
        if motor_id in self.motor_states:
            self.motor_states[motor_id]["direction_cw"] = direction_cw

    def set_motor_state(self, motor_id, enabled):
        if motor_id in self.motor_states:
            self.motor_states[motor_id]["enabled"] = enabled

    def set_motor_sps(self, motor_id, sps):
        if motor_id in self.motor_states:
            self.motor_states[motor_id]["sps"] = sps

    def set_motor_microstepping(self, motor_id, microstepping):
        if motor_id in self.motor_states:
            self.motor_states[motor_id]["microstepping"] = microstepping

    def set_linked(self, linked):
        self.linked = linked

    def set_temperature_offset(self, offset):
        self.temperature_offset = offset

    def set_humidity_offset(self, offset):
        self.humidity_offset = offset

    def set_pressure_offset(self, offset):
        self.pressure_offset = offset

# Initialize a single instance of RuntimeState
runtime_state = RuntimeState()