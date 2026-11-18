# Circuit Theory & Power Architecture — Electronic Butterfly

This document explains the electrical engineering rationale, transient noise mitigation, signal integrity, and power budgeting for the Cybernetic Butterfly.

---

## 1. Power Topology & Transient Isolation

Driving inductive mechanical actuators (micro servos) alongside sensitive high-speed digital electronics (ESP32-C3 RISC-V core and WS2812B high-speed serial LEDs) on a compact robotic insect presents electrical challenges:
1. **Motor Inrush & Inductive Kick:** Micro servos generate instantaneous current spikes of 300mA–600mA during rapid direction changes and PWM rotor acceleration.
2. **Brush Noise:** DC brushed coreless motors in mini servos emit high-frequency commutation noise across supply rails.
3. **Brownout Vulnerability:** The ESP32-C3 core operates at 3.3V and will trigger a hardware brownout reset if $V_{DD}$ sags below 2.8V for even a few microseconds.

### Power Architecture Solution:
```text
  [ USB-C 5V In / LiPo 3.7V + Boost ] 
                │
                ├───[ 220µF Low-ESR Cap ]───> [ 5V Servo Rail (M1 & M2) ]
                │
                ├───[ 100nF Ceramic ]───────> [ WS2812B Wing LEDs Rail ]
                │
                └───[ Onboard ME6211 LDO ]──> [ 3.3V Clean Rail ]
                                                      │
                                                      ├──> ESP32-C3 Core
                                                      ├──> Light Sensor (LDR)
                                                      └──> Antenna Touch Sensing
```

- **Separated Supply Paths:** The 3.3V internal LDO provides significant Power Supply Rejection Ratio (PSRR > 60dB @ 1kHz), isolating the CPU core from 5V servo voltage dips.
- **Bulk Energy Storage ($C_1 = 220\mu\text{F}$):** Absorbs servo startup transients locally, preventing voltage drops at the battery or boost converter output.
- **Star Grounding:** Motor ground returns do NOT pass through the analog / sensor reference ground traces before reaching the common battery ground plane.

---

## 2. Signal Conditioning & Interface Circuits

### A. WS2812B 800kHz Serial Data Protection
The WS2812B communication protocol relies on high-speed NRZ pulses ($T_0H = 400\text{ns}$, $T_1H = 850\text{ns}$, cycle period $1.25\mu\text{s}$).
- **Series Damping Resistor ($R_2 = 330\Omega$):** Positioned immediately at GPIO8 output pin. It suppresses high-frequency transmission line reflections caused by impedance mismatch between the PCB trace and the flexible wing harness wire.
- **Logic Level Compatibility:** Although WS2812B specifies $V_{IH(\min)} = 0.7 \times V_{DD}$ (which would be 3.5V at 5V supply), modern WS2812B-2020 and SK6812 ICs reliably trigger on 3.3V CMOS logic (threshold $\approx 2.0\text{V}$). Supplying LEDs at ~4.5V–4.8V (diode-dropped or 1S LiPo direct ~3.7V–4.2V) guarantees 100% logic compliance.

### B. Ambient Light Sensor (GL5528 LDR)
The ambient light detector uses a passive voltage divider with the internal ADC of the ESP32-C3:
$$V_{out} = V_{3V3} \times \frac{R_{pull-down}}{R_{LDR} + R_{pull-down}} = 3.3\text{V} \times \frac{10\text{k}\Omega}{R_{LDR} + 10\text{k}\Omega}$$
- Daylight ($R_{LDR} \approx 2\text{k}\Omega$): $V_{out} \approx 3.3 \times \frac{10}{12} = 2.75\text{V}$ (ADC reading $\approx 3410 / 4095$).
- Indoor Light ($R_{LDR} \approx 15\text{k}\Omega$): $V_{out} \approx 3.3 \times \frac{10}{25} = 1.32\text{V}$ (ADC reading $\approx 1638$).
- Dark / Night ($R_{LDR} > 150\text{k}\Omega$): $V_{out} < 0.20\text{V}$ (ADC reading $< 250$).

---

## 3. Power Budget & Battery Longevity

Calculated for a standard **3.7V 500mAh LiPo Battery (1.85 Wh)**:

| Mode | Active Components | Avg Current (mA) | Estimated Runtime |
| :--- | :--- | :---: | :---: |
| **Deep Sleep (Darkness)** | ESP32 RTC timer / ULP + LDR check | ~0.08 mA | > 200 days |
| **Resting / Perched** | ESP32 CPU (80MHz), LEDs breathing @ 10% brightness, Servos holding torque | ~45 mA | ~11.1 hours |
| **Gentle Biological Flutter**| Dual servos cycling @ 0.8 Hz sine wave, LEDs ambient pulse | ~140 mA | ~3.5 hours |
| **Active Flight & Fast Flutter**| Dual servos cycling @ 2.5 Hz, 16x RGB LEDs dynamic rainbow wave | ~290 mA | ~1.7 hours |
| **Continuous USB Display** | Powered from external 5V 1A USB-C wall adapter / power bank | — | Infinite |
