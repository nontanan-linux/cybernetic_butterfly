#!/usr/bin/env python3
"""
Configuration Synchronizer for Electronic Butterfly
Reads centralized YAML configurations from config/ and automatically generates:
1. firmware/esp32_c3_arduino/src/Config.h (C++ Header)
2. firmware/micropython/config.py (MicroPython module)
3. web_visualizer/config.json (Web simulator config)
4. config/default_config.json (Consolidated JSON)
"""

import sys
from pathlib import Path
import json

PROJECT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_DIR))

from config.config_loader import load_all_configs, export_json

def generate_cpp_header(cfg, target_path: Path):
    """Generates C++ Config.h for ESP32-C3 Arduino/PlatformIO."""
    hw_pins = cfg.hardware.pins
    kin_limits = cfg.kinematics.limits
    kin_modes = cfg.kinematics.modes
    net = cfg.network

    content = f"""// ============================================================================
// AUTO-GENERATED CONFIGURATION HEADER — DO NOT EDIT DIRECTLY!
// Source: config/*.param.yaml
// Generated via: python3 scripts/sync_config.py
// ============================================================================
#pragma once
#include <Arduino.h>

// --- Physical Pin Allocation (User Specification) ---
#define PIN_SERVO_LEFT          {hw_pins.servo_left}   // GPIO 2: Left Wing MG90S PWM
#define PIN_SERVO_RIGHT         {hw_pins.servo_right}  // GPIO 3: Right Wing MG90S PWM (Angle = 180 - L)
#define PIN_WS2812B_DATA        {hw_pins.ws2812b_data} // GPIO 4: WS2812B / SMD LED Data via 330 ohm
#define PIN_BUTTON_BOOT         {hw_pins.button_boot}  // GPIO 9: Onboard Boot button

// --- WS2812B Mini PCB Pixel Array ---
#define NUM_LEDS_PER_WING       {cfg.effects.leds.leds_per_wing}
#define TOTAL_LEDS              {cfg.effects.leds.total_count}
#define DEFAULT_LED_BRIGHTNESS  {cfg.effects.leds.default_brightness}

// --- Servo Kinematic Travel Limits ---
#define SERVO_MIN_ANGLE         {int(kin_limits.min_safe_angle_deg)}
#define SERVO_MAX_ANGLE         {int(kin_limits.max_safe_angle_deg)}
#define SERVO_REST_ANGLE        {int(kin_limits.rest_angle_deg)}
#define SERVO_HORIZONTAL_ANGLE  {int(kin_limits.horizontal_angle_deg)}

// --- Biomechanical Frequency Profiles (Hz) ---
#define FREQ_BREATHE            {kin_modes.breathing.frequency_hz}f
#define FREQ_GENTLE_FLUTTER     {kin_modes.flutter.frequency_hz}f
#define FREQ_ACTIVE_FLIGHT      {kin_modes.active_flight.frequency_hz}f
#define FREQ_STARTLED           {kin_modes.startled_burst.frequency_hz}f

// --- Network & SoftAP Web Server ---
#define AP_SSID                 "{net.access_point.ssid}"
#define AP_PASS                 "{net.access_point.password}"
#define HTTP_PORT               {net.server.http_port}
#define MDNS_HOSTNAME           "{net.mdns.hostname}"
"""
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated C++ Header: {target_path}")

def generate_micropython_config(cfg, target_path: Path):
    """Generates config.py for MicroPython."""
    content = f"""# Auto-generated MicroPython configuration
# Source: config/*.param.yaml
# Generated via: python3 scripts/sync_config.py

PIN_SERVO_LEFT = {cfg.hardware.pins.servo_left}    # GPIO 2
PIN_SERVO_RIGHT = {cfg.hardware.pins.servo_right}  # GPIO 3
PIN_NEOPIXEL = {cfg.hardware.pins.ws2812b_data}    # GPIO 4
PIN_BUTTON_BOOT = {cfg.hardware.pins.button_boot}  # GPIO 9

TOTAL_LEDS = {cfg.effects.leds.total_count}
LEDS_PER_WING = {cfg.effects.leds.leds_per_wing}

SERVO_MIN_ANGLE = {cfg.kinematics.limits.min_safe_angle_deg}
SERVO_MAX_ANGLE = {cfg.kinematics.limits.max_safe_angle_deg}
SERVO_REST_ANGLE = {cfg.kinematics.limits.rest_angle_deg}

AP_SSID = "{cfg.network.access_point.ssid}"
AP_PASS = "{cfg.network.access_point.password}"
HTTP_PORT = {cfg.network.server.http_port}
"""
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated MicroPython Config: {target_path}")

def main():
    print("=" * 60)
    print("🦋 SYNCHRONIZING ELECTRONIC BUTTERFLY CONFIGURATIONS")
    print("=" * 60)

    cfg = load_all_configs()

    # 1. Export Consolidated JSON
    json_path = export_json(PROJECT_DIR / "config" / "default_config.json")
    print(f"✅ Generated Consolidated JSON: {json_path}")

    # 2. Copy JSON for Web Visualizer
    web_json_path = PROJECT_DIR / "web_visualizer" / "config.json"
    with open(web_json_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print(f"✅ Generated Web Simulator Config: {web_json_path}")

    # 3. Generate C++ Header
    cpp_header_path = PROJECT_DIR / "firmware" / "esp32_c3_arduino" / "src" / "Config.h"
    generate_cpp_header(cfg, cpp_header_path)

    # 4. Generate MicroPython Config
    mpy_config_path = PROJECT_DIR / "firmware" / "micropython" / "config.py"
    generate_micropython_config(cfg, mpy_config_path)

    print("=" * 60)
    print("🎉 All configurations synchronized across C++, Python & Web Visualizer!")
    print("=" * 60)

if __name__ == "__main__":
    main()
