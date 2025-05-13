#include <TMC2208Stepper.h>
#include <AccelStepper.h>
#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <avr/wdt.h>

#define DIR_PIN_FRAME 3
#define STEP_PIN_FRAME 4
#define EN_PIN_FRAME 5

#define DIR_PIN_CORE 10
#define STEP_PIN_CORE 11
#define EN_PIN_CORE 12

#define LED_PIN 6
#define NUM_LEDS 130

#define BUZZER_PIN A8

#define RMS_CURRENT 400
#define TOFF_VALUE 2
#define MICROSTEP_RESOLUTION 16
#define MAX_SPEED 1000
#define INITIAL_SPEED 533.333

#define SLAVE_ADDRESS 0x08
#define PACKET_MAX_SIZE 32
#define START_BYTE 0xFF

TMC2208Stepper core_driver = TMC2208Stepper(&Serial1);
AccelStepper core_stepper = AccelStepper(core_stepper.DRIVER, STEP_PIN_CORE, DIR_PIN_CORE);

TMC2208Stepper frame_driver = TMC2208Stepper(&Serial2);
AccelStepper frame_stepper = AccelStepper(frame_stepper.DRIVER, STEP_PIN_FRAME, DIR_PIN_FRAME);

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRBW + NEO_KHZ800);

uint8_t packet[PACKET_MAX_SIZE];
boolean ms_change = false;

uint8_t frame_microstepping;
uint8_t core_microstepping;

uint16_t calculateCRC16(const uint8_t *data, uint16_t length) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void setup() {
    pinMode(BUZZER_PIN, OUTPUT);
    Serial.begin(9600);
    Serial1.begin(115200);
    Serial2.begin(115200);
    strip.setBrightness(255);
    strip.begin();
    strip.show();
    initMotors();
    Wire.begin(SLAVE_ADDRESS);
    Wire.onReceive(receivePacket);
    Wire.setWireTimeout(1000, true);
    startupSequence();
}

void loop() {
    if (ms_change) {
        frame_driver.microsteps(1 << frame_microstepping);
        core_driver.microsteps(1 << core_microstepping);
        ms_change = false;
    }
    frame_stepper.runSpeed();
    core_stepper.runSpeed();
}

void initMotors() {
    frame_driver.pdn_disable(true);
    frame_driver.I_scale_analog(false);
    frame_driver.rms_current(RMS_CURRENT);
    frame_driver.toff(TOFF_VALUE);
    frame_driver.mstep_reg_select(true);
    frame_driver.microsteps(MICROSTEP_RESOLUTION);

    core_driver.pdn_disable(true);
    core_driver.I_scale_analog(false);
    core_driver.rms_current(RMS_CURRENT);
    core_driver.toff(TOFF_VALUE);
    core_driver.mstep_reg_select(true);
    core_driver.microsteps(MICROSTEP_RESOLUTION);

    frame_stepper.setEnablePin(EN_PIN_FRAME);
    frame_stepper.setPinsInverted(false, false, true);
    frame_stepper.setMaxSpeed(MAX_SPEED);
    frame_stepper.setSpeed(INITIAL_SPEED);

    core_stepper.setEnablePin(EN_PIN_CORE);
    core_stepper.setPinsInverted(false, false, true);
    core_stepper.setMaxSpeed(MAX_SPEED);
    core_stepper.setSpeed(INITIAL_SPEED);
}

void startupSequence() {
    for (long firstPixelHue = 0; firstPixelHue < 65536; firstPixelHue += 256) {
        for (int i = 0; i < strip.numPixels(); i++) {
            int pixelHue = firstPixelHue + (i * 65536L / strip.numPixels());
            strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue)));
        }
        strip.show();
    }
    colorWipe(strip.Color(0, 0, 0, 0), 1);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(80);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
}

void receivePacket(int byteCount) {
    bool timeout = false;
    digitalWrite(BUZZER_PIN, HIGH);
    if (byteCount < 5) {
        Serial.println("Error: Packet too short");
        timeout = true;
    } else {
        for (int i = 0; i < byteCount; i++) {
            packet[i] = Wire.read();
        }

        if (packet[0] != START_BYTE) {
            Serial.println("Error: Invalid start byte");
            timeout = true;
        } else {
            uint8_t length = packet[1];

            if (length != (byteCount - 4)) {
                Serial.println("Error: Length mismatch");
                timeout = true;
            } else {
                uint16_t computedCRC = calculateCRC16(packet, byteCount - 2);
                uint16_t receivedCRC = (packet[byteCount - 2] << 8) | packet[byteCount - 1];

                if (computedCRC != receivedCRC) {
                    Serial.println("Error: CRC mismatch");
                    timeout = true;
                } else {
                    processCommand(packet[2], &packet[3], length - 1);
                }
            }
        }
    }
    digitalWrite(BUZZER_PIN, LOW);
    if (timeout) {
        // Handle timeout or error case
        Serial.println("Timeout or error occurred, turning off buzzer");
        digitalWrite(BUZZER_PIN, LOW);
    }
}

void processCommand(uint8_t command, uint8_t *data, uint8_t dataLength) {
    Serial.print("Processing command: ");
    Serial.println(command, HEX);

    switch (command) {
        case 0x00:
            resetArduino();
            break;
        case 0x01:
            setMotorStateAndSpeed(data, dataLength);
            break;
        case 0x02:
            updateLEDStrip(data, dataLength);
            break;
        case 0x03:
            setLEDColors(data, dataLength);
            break;
        case 0x04:
            displayLEDStrip();
            break;
        case 0x05:
            activateBuzzer(data, dataLength);
            break;
        default:
            break;
    }
}

void resetArduino() {
    wdt_enable(WDTO_15MS);
    while (1);
}

void setMotorStateAndSpeed(uint8_t *data, uint8_t length) {
    if (length < 12) {
        return;
    }

    bool frame_enabled = data[0];
    uint32_t frame_sps_raw = ((uint32_t)data[1] << 16) | ((uint32_t)data[2] << 8) | (uint32_t)data[3];
    float frame_sps = frame_sps_raw / 1000.0;
    frame_microstepping = data[4];
    bool frame_direction_cw = data[5];

    bool core_enabled = data[6];
    uint32_t core_sps_raw = ((uint32_t)data[7] << 16) | ((uint32_t)data[8] << 8) | (uint32_t)data[9];
    float core_sps = core_sps_raw / 1000.0;
    core_microstepping = data[10];
    bool core_direction_cw = data[11];

    // Apply direction
    if (!frame_direction_cw) {
        frame_sps = -frame_sps;
    }
    if (!core_direction_cw) {
        core_sps = -core_sps;
    }

    if (frame_enabled) {
        frame_stepper.enableOutputs();
    } else {
        frame_stepper.disableOutputs();
    }
    frame_stepper.setSpeed(frame_sps);

    if (core_enabled) {
        core_stepper.enableOutputs();
    } else {
        core_stepper.disableOutputs();
    }
    core_stepper.setSpeed(core_sps);

    ms_change = true;

    // Debugging printouts
    Serial.print("Frame motor speed set to: ");
    Serial.println(frame_sps);
    Serial.print("Frame motor microstepping set to: ");
    Serial.println(1 << frame_microstepping);
    Serial.print("Core motor speed set to: ");
    Serial.println(core_sps);
    Serial.print("Core motor microstepping set to: ");
    Serial.println(1 << core_microstepping);
}

void updateLEDStrip(uint8_t *data, uint8_t length) {
    if (length < 7) return; // Ensure there are enough bytes for start, end, red, green, blue, white, and brightness
    uint8_t start = data[0] - 1;
    uint8_t end = data[1] - 1;
    uint8_t red = data[2];
    uint8_t green = data[3];
    uint8_t blue = data[4];
    uint8_t white = data[5];
    uint8_t brightness = data[6];

    for (uint8_t i = start; i <= end; i++) {
        strip.setPixelColor(i, strip.Color(red, green, blue, white));
    }
    strip.setBrightness(brightness);
    strip.show();
}

void setLEDColors(uint8_t *data, uint8_t length) {
    if (length < 7) return; // Ensure there are enough bytes for start, end, red, green, blue, white, and brightness
    uint8_t start = data[0] - 1;
    uint8_t end = data[1] - 1;
    uint8_t red = data[2];
    uint8_t green = data[3];
    uint8_t blue = data[4];
    uint8_t white = data[5];
    uint8_t brightness = data[6];

    for (uint8_t i = start; i <= end; i++) {
        strip.setPixelColor(i, strip.Color(red, green, blue, white));
    }
    strip.setBrightness(brightness);
}

void displayLEDStrip() {
    strip.show();
}

void activateBuzzer(uint8_t *data, uint8_t length) {
    if (length < 1) return; // Ensure there is at least one byte for the duration
    uint8_t duration = data[0]; // Duration in milliseconds
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
}

void colorWipe(uint32_t c, uint8_t wait) {
    for (uint16_t i = 0; i < strip.numPixels(); i++) {
        strip.setPixelColor(i, c);
        strip.show();
        delay(wait);
    }
}
