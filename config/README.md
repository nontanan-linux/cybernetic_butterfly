# Configuration Management — Electronic Butterfly ⚙️

This directory contains the centralized, single-source-of-truth configuration architecture for the Electronic Butterfly project. All network settings (host IP, ports, Wi-Fi credentials), hardware pinouts, kinematics boundaries, and lighting parameters are defined here in standard YAML and synchronized across C++, Python, and Web platforms.

---

## 📁 Configuration File Map

| File | Purpose | Key Parameters |
| :--- | :--- | :--- |
| **[`network.param.yaml`](file:///home/tacv/workspace/ElectronicsArt/config/network.param.yaml)** | Network & Communications | Host IP, HTTP Port (`80`), Dev Port (`8080`), SoftAP SSID/Password, Station Wi-Fi, mDNS hostname (`butterfly.local`), WebSocket telemetry rate |
| **[`hardware.param.yaml`](file:///home/tacv/workspace/ElectronicsArt/config/hardware.param.yaml)** | Physical Electronics & Pins | ESP32-C3 GPIO allocations (Servo Left/Right, WS2812B Data, LDR ADC, Touch Pins), Servo PWM timing ($50\text{ Hz}$, $500 - 2500\mu\text{s}$), battery ratings |
| **[`kinematics.param.yaml`](file:///home/tacv/workspace/ElectronicsArt/config/kinematics.param.yaml)** | Flapping Kinematics | Travel limits ($15^\circ - 85^\circ$), rest angle ($75^\circ$), harmonic Fourier ratios ($A_2/A_1 = 0.22$), behavioral mode profiles (Sleep, Breathe, Flutter, Flight, Startled, Glide) |
| **[`effects.param.yaml`](file:///home/tacv/workspace/ElectronicsArt/config/effects.param.yaml)** | LED Shaders & Sensors | 16x WS2812B NeoPixel settings, RGB palettes (Bioluminescence, Morpho Blue, Monarch Fire, Cyber Aurora), LDR day/night ADC thresholds, touch trigger delta |
| **[`default_config.json`](file:///home/tacv/workspace/ElectronicsArt/config/default_config.json)** | Compiled Unified JSON | Auto-generated JSON used by web simulators and runtime microservices |
| **[`config_loader.py`](file:///home/tacv/workspace/ElectronicsArt/config/config_loader.py)** | Python Config Engine | Loads YAMLs, merges dot-accessible dictionaries (`cfg.network.server.http_port`), validates physical safety bounds, applies `.env` overrides |

---

## 🔄 Automated Synchronization Workflow

Whenever you modify any `.param.yaml` or `.env` file, run the synchronizer script:

```bash
cd /home/tacv/workspace/ElectronicsArt
python3 scripts/sync_config.py
# หรือ
make sync
```

This single command automatically updates:
1. **`firmware/esp32_c3_arduino/src/Config.h`** — Embedded C++ preprocessor constants
2. **`firmware/micropython/config.py`** — MicroPython configuration constants
3. **`web_visualizer/config.json`** — WebGL Three.js interactive visualizer configuration
4. **`config/default_config.json`** — Consolidated JSON file

---

## 🌐 Network & Host Configuration

### 1. SoftAP (ESP32 Standalone Access Point)
- **SSID:** `CyberButterfly-ESP32`
- **Default Password:** `cyberbutterfly`
- **Gateway IP:** `192.168.4.1`
- **Web Dashboard URL:** `http://192.168.4.1` or `http://butterfly.local`

### 2. Local Development & Simulator
- **Host:** `0.0.0.0`
- **Port:** `8050`
- Launch with:
  ```bash
  python3 scripts/visualize_model.py
  # หรือ
  make view
  ```

---

## 🔐 Environment Variables (`.env`)

You can override settings at runtime without modifying YAML files by editing `.env`:

```bash
# Network & Server
BUTTERFLY_HOST=0.0.0.0
BUTTERFLY_PORT=80
BUTTERFLY_DEV_PORT=8050

# Wi-Fi SoftAP
BUTTERFLY_SSID=MyCustomButterfly
BUTTERFLY_PASS=securepass123

# Serial Upload Port
UPLOAD_PORT=/dev/ttyACM0
MONITOR_SPEED=115200
```

---

## 🐍 Python Usage Example

```python
from config.config_loader import load_all_configs

cfg = load_all_configs()

# Dot-accessible parameters
print("SoftAP SSID:", cfg.network.access_point.ssid)
print("HTTP Port:", cfg.network.server.http_port)
print("Left Servo Pin: GPIO", cfg.hardware.pins.servo_left)
print("Flap Min Angle:", cfg.kinematics.limits.min_safe_angle_deg)
```
