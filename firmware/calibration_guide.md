# Calibration & Tuning Guide — Electronic Butterfly

Follow these calibration procedures before final mechanical assembly to ensure smooth biological motion and protect servo gear trains from mechanical stalls.

---

## 1. Servo Electrical & Mechanical Trimming

Micro servos (such as SG90 or 3.7g sub-micro servos) have manufacturing tolerances in their internal potentiometer feedback.

### Calibration Procedure:
1. **Flashing Calibration Firmware:**
   Set the firmware to neutral calibration mode (both servos driven to $90^\circ$ continuous).
2. **Horn Orientation:**
   Press the plastic servo horn onto the splined output shaft so that it is oriented as close to perpendicular ($90^\circ$) to the servo body as possible.
3. **Software Angle Trimming:**
   In `firmware/esp32_c3_arduino/src/Config.h`:
   ```cpp
   #define SERVO_MIN_ANGLE   15  // Lower mechanical limit (Wings flat)
   #define SERVO_MAX_ANGLE   85  // Upper mechanical limit (Wings folded)
   #define SERVO_REST_ANGLE  75  // Default perched posture
   ```
   - If the pushrod hits the chassis during the downstroke, increase `SERVO_MIN_ANGLE` (e.g. from $15^\circ$ to $20^\circ$).
   - If the wings bind together at the top of the upstroke, decrease `SERVO_MAX_ANGLE` (e.g. from $85^\circ$ to $80^\circ$).

> **Warning:** A stalled servo draws $> 500\text{mA}$ continuously and can strip plastic nylon gears or overheat. If you hear a high-pitched buzzing without movement, immediately adjust angle bounds.

---

## 2. Capacitive Touch Sensitivity Tuning

The capacitive delta detection measures charge dissipation across the brass antenna probes:
In `firmware/esp32_c3_arduino/src/Config.h`:
```cpp
#define TOUCH_TRIGGER_DELTA  80  // Trigger threshold
```

- **If too sensitive (false triggers from ambient noise/servos):**
  Increase `TOUCH_TRIGGER_DELTA` to `120` or `150`.
- **If not sensitive enough (requires firm grasp rather than light brush):**
  Decrease `TOUCH_TRIGGER_DELTA` to `50` or `60`.
- Ensure the antenna wire is isolated from the chassis ground and servo wires.

---

## 3. Ambient Light Sensor (LDR) Calibration

In `firmware/esp32_c3_arduino/src/Config.h`:
```cpp
#define LDR_NIGHT_THRESHOLD  300  // ADC below this -> Sleep state
#define LDR_DAY_THRESHOLD    700  // ADC above this -> Wake state
```

1. Open Arduino Serial Monitor at $115200\text{ baud}$.
2. Read the raw ADC value printed during daylight and when covering the head with your hand.
3. Set `LDR_NIGHT_THRESHOLD` slightly above your dark reading (e.g. $250 - 350$).
4. The hysteresis band between $300$ and $700$ prevents flickering between sleep and wake modes at twilight.
