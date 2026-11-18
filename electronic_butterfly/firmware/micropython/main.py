"""
MicroPython Firmware for Electronic Butterfly (ESP32-C3)
Compliant with User Specifications:
- GPIO 2: Left Servo PWM
- GPIO 3: Right Servo PWM (Direct Drive: 180 - Left_Angle)
- GPIO 4: WS2812B Mini PCB Pixel Array via 330 ohm
- GPIO 9: Mode Button
"""

import time
import math
from machine import Pin, PWM
import neopixel

# Physical Pin Allocation
PIN_SERVO_LEFT = 2
PIN_SERVO_RIGHT = 3
PIN_NEOPIXEL = 4
PIN_BUTTON_BOOT = 9
TOTAL_LEDS = 8 # 4 LEDs per wing

# Setup MG90S Servos (50 Hz PWM)
servo_l = PWM(Pin(PIN_SERVO_LEFT), freq=50)
servo_r = PWM(Pin(PIN_SERVO_RIGHT), freq=50)

def set_servo_angle(pwm, angle_deg, mirrored=False):
    """Maps 0 - 180 degrees to standard 500us - 2500us duty cycle"""
    target = (180 - angle_deg) if mirrored else angle_deg
    target = max(15, min(85, target))
    pulse_ms = 0.5 + (target / 180.0) * 2.0
    duty_u16 = int((pulse_ms / 20.0) * 65535)
    pwm.duty_u16(duty_u16)

# Setup NeoPixels
np = neopixel.NeoPixel(Pin(PIN_NEOPIXEL), TOTAL_LEDS)
btn = Pin(PIN_BUTTON_BOOT, Pin.IN, Pin.PULL_UP)

print("🦋 Cybernetic Butterfly MicroPython Engine Started (Direct Drive MG90S)!")

def bioluminescent_pulse(t_ms):
    """Generates aquatic breathing wave on 8 WS2812B wing pixels"""
    for i in range(4):
        wave = int((math.sin((t_ms / 300.0) - (i * 0.8)) + 1.0) * 127)
        r = 0
        g = min(255, int(wave * 0.9))
        b = min(255, int(wave * 0.7))
        np[i] = (r, g, b)         # Left wing (0-3)
        np[7 - i] = (r, g, b)     # Mirrored right wing (7-4)
    np.write()

def main_loop():
    start_time = time.ticks_ms()
    freq = 1.2 # Flapping frequency in Hz
    center_angle = 45.0
    amplitude = 25.0

    while True:
        now = time.ticks_ms()
        elapsed_s = time.ticks_diff(now, start_time) / 1000.0
        
        # Harmonic Fourier Kinematics
        h1 = math.sin(2.0 * math.pi * freq * elapsed_s)
        h2 = 0.22 * math.sin(4.0 * math.pi * freq * elapsed_s + 0.35)
        stroke = h1 + h2
        angle = center_angle + (amplitude * stroke)
        
        # Apply to Direct Drive Servos (Right servo: 180 - angle)
        set_servo_angle(servo_l, angle, mirrored=False)
        set_servo_angle(servo_r, angle, mirrored=True)
        
        # Update glowing veins
        bioluminescent_pulse(now)
        time.sleep_ms(20)

if __name__ == "__main__":
    main_loop()
