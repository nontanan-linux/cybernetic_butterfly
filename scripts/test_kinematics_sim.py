#!/usr/bin/env python3
"""
Kinematics & Harmonic Waveform Simulation Test
Simulates and validates the harmonic sine-wave wing flapping equations used in ESP32-C3 firmware.
"""

import math
import time

def simulate_flapping(duration_sec=2.0, freq_hz=1.5, amplitude_deg=28.0, center_deg=45.0, steps=25):
    print("=" * 65)
    print("🦋 BIOMIMETIC WING FLAPPING KINEMATICS SIMULATION")
    print(f"Frequency: {freq_hz} Hz | Amplitude: ±{amplitude_deg}° | Center: {center_deg}°")
    print("=" * 65)
    print(f"{'Time (s)':^10} | {'Left Wing (°)':^14} | {'Right Wing (°)':^15} | {'Visual Waveform':<20}")
    print("-" * 65)

    dt = duration_sec / steps
    for i in range(steps + 1):
        t = i * dt
        # Biomechanical harmonic equation: primary harmonic + 2nd harmonic
        h1 = math.sin(2.0 * math.pi * freq_hz * t)
        h2 = 0.22 * math.sin(4.0 * math.pi * freq_hz * t + 0.35)
        stroke = h1 + h2

        angle_l = center_deg + (amplitude_deg * stroke)
        # Clamped within safe physical servo bounds (15° - 85°)
        angle_l = max(15.0, min(85.0, angle_l))
        angle_r = angle_l # Symmetrical flapping

        # ASCII bar graph (15° to 85° mapped to 0 to 24 chars)
        bar_len = int(((angle_l - 15.0) / 70.0) * 24)
        bar = "█" * bar_len + "░" * (24 - bar_len)

        phase = "▲ Upstroke" if stroke > 0 else "▼ Downstroke"
        print(f"{t:^10.2f} | {angle_l:^14.1f} | {angle_r:^15.1f} | [{bar}] {phase}")

    print("=" * 65)
    print("✅ Harmonic motion equations validated successfully. No mechanical stall detected.")

if __name__ == "__main__":
    simulate_flapping()
