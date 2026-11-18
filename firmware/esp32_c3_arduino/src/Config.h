// ============================================================================
// AUTO-GENERATED CONFIGURATION HEADER — DO NOT EDIT DIRECTLY!
// Source: config/*.param.yaml
// Generated via: python3 scripts/sync_config.py
// ============================================================================
#pragma once
#include <Arduino.h>

// --- Physical Pin Allocation (User Specification) ---
#define PIN_SERVO_LEFT          2   // GPIO 2: Left Wing MG90S PWM
#define PIN_SERVO_RIGHT         3  // GPIO 3: Right Wing MG90S PWM (Angle = 180 - L)
#define PIN_WS2812B_DATA        4 // GPIO 4: WS2812B / SMD LED Data via 330 ohm
#define PIN_BUTTON_BOOT         9  // GPIO 9: Onboard Boot button

// --- WS2812B Mini PCB Pixel Array ---
#define NUM_LEDS_PER_WING       4
#define TOTAL_LEDS              8
#define DEFAULT_LED_BRIGHTNESS  180

// --- Servo Kinematic Travel Limits ---
#define SERVO_MIN_ANGLE         15
#define SERVO_MAX_ANGLE         85
#define SERVO_REST_ANGLE        75
#define SERVO_HORIZONTAL_ANGLE  20

// --- Biomechanical Frequency Profiles (Hz) ---
#define FREQ_BREATHE            0.4f
#define FREQ_GENTLE_FLUTTER     1.2f
#define FREQ_ACTIVE_FLIGHT      2.2f
#define FREQ_STARTLED           3.5f

// --- Network & SoftAP Web Server ---
#define AP_SSID                 "CyberButterfly-ESP32"
#define AP_PASS                 "cyberbutterfly"
#define HTTP_PORT               80
#define MDNS_HOSTNAME           "butterfly"
