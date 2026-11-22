# Cybernetic Butterfly (หุ่นยนต์ผีเสื้อไซเบอร์เนติกส์) 🦋⚡

โปรเจกต์หุ่นยนต์ผีเสื้อชีวกลศาสตร์และงานศิลปะอิเล็กทรอนิกส์ (PCB Art) ขับเคลื่อนด้วย **Python (`build123d`)** สำหรับสร้างโมเดล 3D CAD พาราเมตริกไร้การชน (`0.0000 mm³` B-Rep Boolean Collision), ระบบจำลองการกระพือปีก 3 มิติบนเว็บ (**Three.js WebGL**) และเฟิร์มแวร์สำหรับชิป **ESP32-C3 SuperMini**

---

## 1. คำสั่งใช้งานด่วน (Quickstart Commands)

```bash
# 1. สร้างโมเดล 3D CAD, ลายปีก PCB Art (SVG) และซิงค์คอนฟิกทั้งหมด
python scripts/build_model.py

# 2. เปิดโปรแกรม 3D CAD Inspector & ตัวจำลองการกระพือปีกบนเบราว์เซอร์ (http://localhost:8050)
python scripts/visualize_model.py --browser

# 3. จำลองชีวกลศาสตร์การกระพือปีก คำนวณพลังงาน และสร้างกราฟรูปคลื่น
python scripts/simulate_kinematics.py --mode all --power --plot
```

*(สามารถใช้คำสั่ง `make build`, `make cad`, `make pcb`, `make sync`, `make sim`, `make view` ได้เช่นกัน)*

---

## 2. การแยกโครงสร้างไฟล์ 3D CAD (`cad/external/` vs `cad/models/`)

ระบบแยกไฟล์ชิ้นส่วนมาตรฐานภายนอก (External Hardware) ออกจากไฟล์ชิ้นส่วนที่สร้างขึ้นเพื่อพิมพ์ 3 มิติ (Generated Parts) อย่างชัดเจน:

### 2.1 `cad/external/` — ชิ้นส่วนมาตรฐานภายนอก (Read-Only ห้ามแก้ไขหรือบันทึกทับ)
สคริปต์จะ **อ่านอย่างเดียว (Read-Only)** เพื่อนำมาประกอบและตรวจสอบการชน โดยไม่เขียนทับไฟล์ต้นฉบับ:
- [`cad/external/Servo-sg90.step`](cad/external/Servo-sg90.step) และ [`cad/external/mg90s_servo.stl`](cad/external/mg90s_servo.stl) — เซอร์โวมอเตอร์เฟืองโลหะ TowerPro MG90S ($180^\circ$)
- [`cad/external/SG90-1-arm-horn.step`](cad/external/SG90-1-arm-horn.step) และ [`cad/external/mg90s_servo_horn.stl`](cad/external/mg90s_servo_horn.stl) — แขนเซอร์โวไนลอนเดี่ยว (21T Spline)

### 2.2 `cad/models/` — ชิ้นส่วนที่สร้างขึ้นด้วย `build123d` (Generated Models)
- **ชิ้นส่วนย่อยสำหรับพิมพ์ 3 มิติ (ส่งออกเฉพาะไฟล์ `.stl` เท่านั้น):**
  1. **[`cad/models/body.stl`](cad/models/body.stl)** — ลำตัวผีเสื้อชิ้นเดียวสมบูรณ์ (`1 Solid`):
     - **ส่วนหัว (Head):** ตาประกอบคู่ใหญ่, งวงผีเสื้อขดใต้หัว (Coiled Proboscis) และ **หนวดผีเสื้อคู่หน้าปลายป่องทรงหยดน้ำ (Clubbed Butterfly Antennae)** กวาดโค้งไปด้านหน้า
     - **ส่วนอกและส่วนท้องที่ท้องด้านล่างราบสนิท (100% Flat Ventral Belly at `Z = -19.8 mm`):** ท้องด้านล่างของส่วนอกและส่วนท้องอยู่ในระนาบ `Z = -19.8 mm` เรียบเสมอกันทั้งหมด โดยมีเบ้าตื้นให้แป้นฐานขาผีเสื้อฝังจมราบสนิทเป็นระนาบเดียวกัน
     - **ส่วนท้องพร้อมช่องใส่ถ่าน 14500 (Abdomen with Battery & MCU Compartments):** ท้องเรียวยาวมีปล้อง (`56.5 mm`) ชั้นล่างเป็น **ช่องล็อกถ่านชาร์จ Li-ion 14500 แบบกดสวมจากใต้ท้อง (`Ø 15.0 × 51.5 mm` Snap-In Cradle)** พร้อมช่องสวิตช์เปิด-ปิดด้านข้าง ส่วนชั้นบนเป็นห้องวางบอร์ด **ESP32-C3 SuperMini**, โมดูลชาร์จ **TP4056 / 5V Boost**, คาปาซิเตอร์ **470µF**, ไดโอด **1N5819** และพอร์ต USB-C
  2. **[`cad/models/left_wing.stl`](cad/models/left_wing.stl)** — ปีกผีเสื้อหางติ่งขนาดใหญ่ด้านซ้าย (`1 Solid`):
     - รูปทรงผีเสื้อหางติ่ง (*Papilio* Swallowtail) ตามภาพต้นแบบ: ปีกคู่หน้ากวาดขึ้นสูง + รอยคอดเว้าลึก + ปีกคู่หลังขอบหยักเป็นคลื่นพร้อม **ติ่งหางผีเสื้อเรียวยาวปลายหยดน้ำ (Long Spatulate Swallowtail)**
     - ขยายขนาดใหญ่ขึ้นอีกเท่าตัว (กางปีกรวม **`464 mm`**, คอร์ดยาว **`298 mm`**) และ **ลดความหนาลง 40%** (โครงขอบปีกและเส้นเลือดหลักบางเพียง **`1.20 mm`**, แผ่นเยื่อในช่องเซลล์บาง **`0.52 mm`**)
  3. **[`cad/models/right_wing.stl`](cad/models/right_wing.stl)** — ปีกผีเสื้อด้านขวา (`1 Solid`, CAD Mirror สมมาตรกับปีกซ้าย 100%)
  4. **[`cad/models/butterfly_legs.stl`](cad/models/butterfly_legs.stl)** — ชุดขาผีเสื้อชีวกลศาสตร์ 6 ขา (`1 Solid`):
     - แป้นฐานยึดโคนขา (`Coplanar Flat Sternum Plate`) ฝังจมเข้าในเบ้าใต้ส่วนอกโดยมีผิวล่างสุดอยู่ที่ `Z = -19.8 mm` **ราบสนิทเสมอกับท้องผีเสื้อ 100%**
     - ขาผีเสื้อเรียวเล็ก 3 คู่ (ขาหน้า ขากลาง ขาหลัง) พับต้นขา (`Femur`) แนบชิดลำตัว ทอดแข้งขา (`Tibia`) ลงสู่ปล้องข้อเท้า (`Horizontal Tarsus`) และกรงเล็บคู่ปลายขา 2 แฉกในท่ายืนของผีเสื้อจริง
- **ไฟล์ประกอบรวมทั้งระบบ (ส่งออกทั้ง `.stl` และ `.step`):**
  5. **[`cad/models/butterfly_full_assembly.stl`](cad/models/butterfly_full_assembly.stl)** และ **[`cad/models/butterfly_full_assembly.step`](cad/models/butterfly_full_assembly.step)** — ชุดประกอบหุ่นยนต์ผีเสื้อสมบูรณ์ทั้ง 8 ชิ้นส่วน (ปริมาตรการชน Static & Dynamic = `0.0000 mm³`)

---

## 3. รายชื่อไฟล์ Python ที่ใช้งานในระบบ (Active Python Modules)

ไฟล์ Python ที่ไม่ใช้งานถูกลบออกทั้งหมด เหลือเฉพาะโมดูลหลักที่ทำงานร่วมกันดังนี้:

| ไฟล์ Python | หน้าที่ในระบบ |
| :--- | :--- |
| **[`scripts/build_model.py`](scripts/build_model.py)** | สคริปต์ Build หลัก: สั่งสร้างโมเดล 3D CAD, สร้างไฟล์ลายปีก SVG และซิงค์คอนฟิกทั้งหมดในคำสั่งเดียว |
| **[`scripts/generate_butterfly_chassis.py`](scripts/generate_butterfly_chassis.py)** | สคริปต์ `build123d` อ่านไฟล์ External CAD (`cad/external/`) และสร้างชิ้นส่วน `.stl` + ชุดประกอบรวม `.stl/.step` ลงใน `cad/models/` |
| **[`scripts/procedural_wing_venation.py`](scripts/procedural_wing_venation.py)** | สร้างไฟล์ลายวงจรศิลปะบนปีกผีเสื้อ 2 มิติ ([`wings_monarch_left.svg`](hardware/pcb_art/wings_monarch_left.svg) และ [`wings_monarch_right.svg`](hardware/pcb_art/wings_monarch_right.svg)) |
| **[`scripts/sync_config.py`](scripts/sync_config.py)** | ซิงค์ค่าจาก `config/*.param.yaml` ไปยัง C++ ([`Config.h`](firmware/esp32_c3_arduino/src/Config.h)), MicroPython ([`config.py`](firmware/micropython/config.py)) และ Web ([`config.json`](web_visualizer/config.json)) |
| **[`scripts/simulate_kinematics.py`](scripts/simulate_kinematics.py)** | จำลองสมการชีวกลศาสตร์การกระพือปีก 6 โหมด ตรวจสอบขอบเขตมุมปลอดภัย คำนวณกระแสไฟ และพล็อตกราฟ [`docs/kinematics_waveform.png`](docs/kinematics_waveform.png) |
| **[`scripts/visualize_model.py`](scripts/visualize_model.py)** | รัน HTTP Server (`http://localhost:8050`) ให้บริการ WebGL 3D CAD Inspector & Kinematics Simulator |
| **[`config/config_loader.py`](config/config_loader.py)** | โมดูลโหลดไฟล์ตั้งค่า YAML, ผสานค่าจาก `.env` และตรวจสอบความถูกต้องของพารามิเตอร์ |

---

## 4. ผังการต่อขาพินและวงจรอิเล็กทรอนิกส์ (Pinout & Electronics)

อุปกรณ์ทั้งหมดติดตั้งอยู่ภายในลำตัวผีเสื้อชิ้นเดียว (ถ่านชาร์จ **14500 Li-ion** อยู่ชั้นล่างของส่วนท้อง และบอร์ด **ESP32-C3 SuperMini** อยู่ชั้นบนของส่วนท้อง):

| ขาพิน ESP32-C3 | อุปกรณ์ปลายทาง | ประเภทสัญญาณ | รายละเอียดการทำงาน |
| :--- | :--- | :--- | :--- |
| **GPIO 2** | เซอร์โวปีกซ้าย (Left MG90S) | PWM 50 Hz (`500–2500 µs`) | ขับปีกซ้ายโดยตรง (`15°–85°`, มุมกลางแนวนอน `45°`) |
| **GPIO 3** | เซอร์โวปีกขวา (Right MG90S) | PWM 50 Hz (`500–2500 µs`) | ขับปีกขวากลับด้านอัตโนมัติ (`Angle = 180 - Left`) |
| **GPIO 4** | ไฟปีก WS2812B (8 ดวง) | Serial Data 800 kHz | ต่อผ่านตัวต้านทาน `330 Ω` แยกเข้าปีกซ้าย 4 ดวง และปีกขวา 4 ดวง |
| **GPIO 9** | ปุ่ม BOOT บนบอร์ด | Digital Input (Pull-up) | กดเพื่อสลับโหมดการบินและพาเลตต์สีไฟทั้ง 6 โหมด |
| **5V (VIN)** | รางไฟหลัก 5V DC | Power Rail (`4.8V–5.0V`) | รับไฟจากโมดูล 5V Step-Up Boost ผ่านไดโอด **1N5819** (กันไฟย้อนเข้า PC) และคร่อมคาปาซิเตอร์ **470µF** (ซับไฟกระชากเซอร์โว) |
| **GND** | กราวด์รวม (Star Ground) | Ground Return | เชื่อมกราวด์ของแบตเตอรี่ 14500, TP4056, 5V Boost, เซอร์โว และไฟ LED ร่วมกัน |

---

## 5. รายการอุปกรณ์ทั้งหมด (Bill of Materials — BOM)

| หมวดหมู่ | อุปกรณ์ | จำนวน | ตำแหน่งติดตั้งในหุ่นยนต์ผีเสื้อ |
| :--- | :--- | :---: | :--- |
| **บอร์ดควบคุม** | **ESP32-C3 SuperMini** ($22.5 \times 18\text{ mm}$) | 1 ตัว | ห้องเครื่องชั้นบนของส่วนท้อง (Upper Dorsal Abdomen Deck) |
| **กลไกขับปีก** | **Micro Servo MG90S ($180^\circ$ เฟืองโลหะ)** + Single-Arm Horn | 2 ชุด | เบ้าเซอร์โวซ้าย-ขวาในส่วนอก (Thorax) สวมแขน Horn เข้าโคนปีกโดยตรง |
| **แสงสว่างบนปีก** | **WS2812B Mini PCB LED** ($\varnothing 9–9.5\text{ mm}$) | 8 ดวง | ฝังในเบ้าบนปุ่มเส้นเลือดปีกซ้าย 4 ดวง และปีกขวา 4 ดวง |
| **ระบบพลังงาน** | **ถ่านชาร์จ Li-ion 14500 (3.7V 800mAh)** + ขั้วสปริง | 1 ก้อน | ช่องกระบอกชั้นล่างของส่วนท้อง (`Ø 15.0 × 51.5 mm` Snap-In Ventral Bay) |
| | **โมดูลชาร์จ TP4056 (USB-C)** + **โมดูล Step-Up Boost 5V** | อย่างละ 1 | ห้องเครื่องส่วนท้อง พร้อมสวิตช์เลื่อน **SPDT Slide Switch** ด้านข้างส่วนท้อง |
| **วงจรป้องกัน** | **คาปาซิเตอร์ 470µF (10V/16V)** + **ไดโอด 1N5819** + **R 330Ω (2 ตัว)** | 1 ชุด | ห้องเครื่องส่วนท้องและจุดแยกสายสัญญาณเข้าโคนปีก |
| | **ลวดทองแดงอาบน้ำยา $\varnothing 0.2\text{ mm}$** | 1 ม้วน | เดินสาย 3 เส้น (`5V`, `GND`, `DIN`) ขดเป็นสปริง 2–3 รอบข้ามจุดหมุนโคนปีก |
| **ชิ้นส่วนพิมพ์ 3 มิติ** | [`body.stl`](cad/models/body.stl), [`left_wing.stl`](cad/models/left_wing.stl), [`right_wing.stl`](cad/models/right_wing.stl), [`butterfly_legs.stl`](cad/models/butterfly_legs.stl) | 4 ชิ้น | ประกอบเข้าด้วยกันด้วยสกรู M2 และสลักประคองจุดหมุนหน้า $\varnothing 2\text{ mm}$ |

---

## 6. โหมดการกระพือปีกชีวกลศาสตร์และการใช้งาน 3D Visualizer

สมการฮาร์โมนิกลำดับที่ 2 ที่ใช้ร่วมกันทั้งในเฟิร์มแวร์ ([`WingKinematics.cpp`](firmware/esp32_c3_arduino/src/WingKinematics.cpp) / [`main.py`](firmware/micropython/main.py)) และตัวจำลอง:

$$\theta(t) = \theta_{\text{center}} + A_1 \sin(2\pi f t) + 0.22 A_1 \sin(4\pi f t + 0.35)$$

- **โหมดการทำงาน 6 รูปแบบ:** `Sleep` ($80^\circ$ พับปีกพัก), `Breathe` ($0.4\text{ Hz}, \pm 8^\circ$), `Flutter` ($1.2\text{ Hz}, \pm 25^\circ$), `Active Flight` ($2.2\text{ Hz}, \pm 30^\circ$), `Startled Burst` ($3.5\text{ Hz}, \pm 32^\circ$) และ `Glide` ($0.2\text{ Hz}, 20^\circ$)
- **การใช้งาน WebGL 3D Visualizer (`python scripts/visualize_model.py --browser`):**
  - เปิด `http://localhost:8050` เพื่อตรวจสอบโมเดลแยกรายชิ้น (แสดงแยกกลุ่ม **Generated Assembly**, **Generated 3D-Print Parts (`.STL Only`)** และ **External Commercial CAD (`Read-Only`)**)
  - กดปุ่ม **`▶ Start Flapping Simulation`** เพื่อทดสอบการกระพือปีกและเอฟเฟกต์ไฟ LED แบบเรียลไทม์
- **การควบคุมบอร์ดจริงผ่าน Wi-Fi SoftAP:** เชื่อมต่อ Wi-Fi ชื่อ **`CyberButterfly-ESP32`** (รหัสผ่าน: `cyberbutterfly`) แล้วเปิดเบราว์เซอร์ไปที่ **`http://192.168.4.1`**
