/**
 * ============================================================================
 * ELECTRONIC BUTTERFLY — EMBEDDED CONTROL SYSTEM
 * Microcontroller: ESP32-C3 SuperMini (RISC-V 160MHz)
 * ============================================================================
 * Physical Pin Allocation (User Specification):
 * - GPIO 2: Left MG90S Micro Servo PWM
 * - GPIO 3: Right MG90S Micro Servo PWM (Direct Drive: Angle = 180 - Left)
 * - GPIO 4: WS2812B Mini PCB Pixel Array Data via 330 ohm resistor
 * - GPIO 9: Onboard BOOT Button (Cycle flight & lighting modes)
 *
 * Power Architecture & Protection:
 * - 2-wire umbilical up stem: 5V & GND from Base Stand (14500 Li-ion + TP4056 + 5V Boost)
 * - 1N5819 Schottky Diode: Prevents back-feeding 5V into PC during USB upload/simulation
 * - 470µF Capacitor: Absorbs servo inductive kick and transients
 * ============================================================================
 */

#include <Arduino.h>
#include "Config.h"
#include "WingKinematics.h"
#include "LEDEffects.h"
#include "WebDashboard.h"

// Subsystem singletons
WingKinematics wingKinematics;
LEDEffects ledEffects;
WebDashboard webDashboard(wingKinematics, ledEffects);

// State tracking
int lastButtonState = HIGH;

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n==========================================");
    Serial.println("🦋 CYBERNETIC BUTTERFLY INITIALIZING...  ");
    Serial.println("Platform: ESP32-C3 SuperMini (RISC-V 160MHz)");
    Serial.println("Servos: 2x MG90S Direct Drive (GPIO 2 & 3)");
    Serial.println("LEDs:   WS2812B Mini Pixels (GPIO 4 via 330Ω)");
    Serial.println("==========================================");

    // 1. Initialize Kinematics (Dual Direct-Drive MG90S Servos)
    Serial.print("Initializing Direct-Drive Wing Servos... ");
    wingKinematics.begin(PIN_SERVO_LEFT, PIN_SERVO_RIGHT);
    Serial.println("DONE.");

    // 2. Initialize Wing LEDs (WS2812B Mini PCB Pixels)
    Serial.print("Initializing WS2812B Wing Pixels... ");
    ledEffects.begin();
    ledEffects.setPattern(PATTERN_BIOLUMINESCENCE);
    Serial.println("DONE.");

    // 3. Initialize BOOT Button
    pinMode(PIN_BUTTON_BOOT, INPUT_PULLUP);

    // 4. Initialize WiFi SoftAP & Embedded Dashboard
    Serial.print("Launching Cybernetic Web Dashboard... ");
    webDashboard.begin();
    Serial.println("ONLINE.");

    Serial.println("🦋 Butterfly is alive, perched and breathing!\n");
}

void loop() {
    unsigned long now = millis();

    // 1. Process Embedded Web Dashboard Client Requests
    webDashboard.handleClient();

    // 2. Physical BOOT Button Toggle (Cycle Modes without phone)
    int btnState = digitalRead(PIN_BUTTON_BOOT);
    if (btnState == LOW && lastButtonState == HIGH) {
        delay(30); // Debounce
        int nextPattern = ((int)ledEffects.getPattern() + 1) % 4;
        ledEffects.setPattern((LEDPattern)nextPattern);

        int nextKinematic = ((int)wingKinematics.getState() + 1) % 6;
        wingKinematics.setState((KinematicState)nextKinematic);
        Serial.printf("🔘 Mode button pressed. Kinematic: %d, LED: %d\n", nextKinematic, nextPattern);
    }
    lastButtonState = btnState;

    // 3. Update Kinematics & Synchronized LED Illumination
    wingKinematics.update(now);
    float strokeNormalized = wingKinematics.getNormalizedStroke();
    ledEffects.update(now, strokeNormalized);
}
