# Electronic Butterfly (Cybernetic Lepidoptera) 🦋⚡

> **A fusion of Organic Nature, PCB Art, Micro-Robotic Kinematics, and Embedded Cybernetics.**  
> *โปรเจกต์งานศิลปะอิเล็กทรอนิกส์ ขับเคลื่อนด้วย **ภาษา Python เป็นหลัก** ทั้งระบบอัตโนมัติ การจำลองกลศาสตร์ และเฟิร์มแวร์ โดยใช้โมดูล **build123d** ในการออกแบบโมเดล 3D CAD พาราเมตริกทั้งหมด*

---

## 🐍 Python-First Architecture & build123d CAD

โปรเจกต์นี้ยึดหลัก **Python-First**:
- **3D CAD Modeling:** พัฒนาด้วยโมดูล **[build123d](https://build123d.readthedocs.io/)** (Python Parametric CAD) รองรับการแสดงผลผ่าน **OCP CAD Viewer (`ocp_vscode`)** บน VS Code แบบเรียลไทม์ และส่งออกไฟล์มาตรฐาน **STL** และ **STEP AP242**
- **Kinematics & Power Simulation:** ขับเคลื่อนด้วย `numpy`, `scipy` และ `matplotlib` จำลองการกระพือปีกและกำลังไฟฟ้า
- **Unified Toolchain CLI:** รวมศูนย์ทุกคำสั่งผ่าน [`main.py`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/main.py) เพียงไฟล์เดียว
- **Embedded MicroPython Firmware:** มีซอร์สโค้ด MicroPython สแตนด์อโลนสำหรับชิป ESP32-C3 ควบคุมเซอร์โว Direct Drive และไฟ WS2812B ได้ทันที

---

## 📖 สารบัญ (Table of Contents)
1. [ภาพรวมของโปรเจกต์ (Project Overview)](#1-ภาพรวมของโปรเจกต์-project-overview)
2. [คำสั่งใช้งานด่วนผ่าน Python CLI (Quickstart)](#2-คำสั่งใช้งานด่วนผ่าน-python-cli-quickstart)
3. [สถาปัตยกรรมระบบ (System Architecture)](#3-สถาปัตยกรรมระบบ-system-architecture)
4. [โครงสร้างไดเรกทอรี (Directory Structure)](#4-โครงสร้างไดเรกทอรี-directory-structure)
5. [การออกแบบโมเดล 3D CAD ด้วย build123d](#5-การออกแบบโมเดล-3d-cad-ด้วย-build123d)
6. [วงจรอิเล็กทรอนิกส์และสถาปัตยกรรม Two-Zone](#6-วงจรอิเล็กทรอนิกส์และสถาปัตยกรรม-two-zone)
7. [การจำลองกลศาสตร์และการแสดงผล (Simulation & Visualizer)](#7-การจำลองกลศาสตร์และการแสดงผล-simulation--visualizer)
8. [รายการอุปกรณ์ทั้งหมด (Complete BOM Checklist)](#8-รายการอุปกรณ์ทั้งหมด-complete-bom-checklist)

---

## 1. ภาพรวมของโปรเจกต์ (Project Overview)

**Electronic Butterfly** คือประติมากรรมหุ่นยนต์แมลงกึ่งไซเบอร์เนติกส์ (Hybrid Cybernetic Sculpture) ที่ออกแบบมาเพื่อจัดแสดงบนโต๊ะทำงานหรือเป็นผลงานศิลปะทางเทคโนโลยี:
- **3D Printed Chassis (3 ชิ้นส่วนหลัก + ฐานตั้ง):**
  - **ส่วนอก (Thorax):** ช่องยึด Micro Servo MG90S 2 ตัว หันแกนหมุนออกด้านซ้ายและขวา (**Direct Drive**) พร้อม **จุดหมุนประคองปีก (Support Hinge)** ลดแรงงัดที่เฟือง Servo
  - **ส่วนท้อง (Abdomen):** โครงโปร่งหรือแคปซูลสำหรับติดตั้งแผ่น PCB และบอร์ด ESP32-C3 SuperMini ให้มองเห็นแสงไฟสถานะภายใน
  - **ปีกซ้าย & ปีกขวา (Left & Right Wings):** โคนปีกมีช่องเว้าฝังแขน Servo Horn สวมเข้าแกนหมุนโดยตรง ตัวปีกหนา $1.8\text{ mm}$ เซาะร่องด้านหลังลึก $0.8\text{ mm}$ สำหรับฝังลวดทองแดงอาบน้ำยา และเจาะเบ้าใส่หลอด WS2812B Mini PCB
  - **ฐานตั้ง (Base Stand):** ซ่อนรางถ่าน 14500 (1 ก้อน), โมดูลชาร์จ TP4056 (USB-C), โมดูล Step-Up Boost 5V, สวิตช์เลื่อนเปิด-ปิด และช่องถ่วงน้ำหนัก โดยส่งสายไฟขึ้นตัวผีเสื้อเพียง 2 เส้น (5V และ GND)
- **Power Protection:** ไดโอด **1N5819** ป้องกันไฟ 5V ชนกันเมื่อเสียบ USB เข้า PC และคาปาซิเตอร์ **470µF** ซับไฟกระชาก
- **Control Pins:** **GPIO 2** คุม Left Servo, **GPIO 3** คุม Right Servo (`180 - Left`), **GPIO 4** คุมหลอดไฟ WS2812B (ผ่านตัวต้านทาน 330Ω และขดลวดสปริง 2–3 รอบข้ามบานพับ)

---

## 2. สถาปัตยกรรมระบบ (System Architecture)

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      POWER INPUT (USB-C 5V / 1S LiPo)                  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
┌──────────────────────────────┐                       ┌───────────────────┐
│     5V BUFFERED RAIL         │                       │ 3.3V CLEAN LDO    │
│  [220µF Low-ESR Capacitor]   │                       │ ESP32-C3 RISC-V   │
└──────────────┬───────────────┘                       └─────────┬─────────┘
               │                                                 │
      ┌────────┴────────┐                               ┌────────┴────────┐
      ▼                 ▼                               ▼                 ▼
 [Left Servo]     [Right Servo]                   [Antenna Touch]    [LDR Light]
  (GPIO6 PWM)      (GPIO7 PWM)                     (GPIO3 / GPIO4)   (GPIO1 ADC)
      │                 │                               │                 │
      └────────┬────────┘                               └────────┬────────┘
               │                                                 │
               ▼                                                 ▼
    ┌──────────────────────┐                         ┌──────────────────────┐
    │  Kinematic Linkage   │◄────────────────────────┤  Kinematics Engine   │
    │  Dual Wing Flapping  │   Harmonic Sine Wave    │  (State Controller)  │
    └──────────┬───────────┘                         └──────────┬───────────┘
               │                                                 │
               ▼                                                 ▼
    ┌───────────────────────────────────────────────────────────────────────┐
    │       PCB ART WINGS (16x WS2812B LEDs on GPIO8 Serial Data)           │
    │        - Left Wing: D1 - D8   |   Right Wing: D9 - D16                │
    │        - Stained-glass translucent FR4 + Exposed ENIG gold traces     │
    └───────────────────────────────────────────────────────────────────────┘
```

---

## 3. โครงสร้างไดเรกทอรี (Directory Structure)

```text
ElectronicsArt/
└── electronic_butterfly/              # ไดเรกทอรีย่อยสำหรับโปรเจกต์ Electronic Butterfly
    ├── README.md                      # เอกสารคู่มือและรายละเอียดโครงการทั้งหมด
    ├── requirements.txt               # รายการ Python dependencies (build123d, scipy, svgwrite, pyyaml)
    ├── .env / .env.example            # การตั้งค่า Environment (Host, Port, Wi-Fi, Serial)
    ├── config/                        # สารบัญการตั้งค่าพารามิเตอร์แบบศูนย์รวม (Single Source of Truth)
    │   ├── network.param.yaml         # การตั้งค่า Host IP, Port, SoftAP, Station Wi-Fi, mDNS
    │   ├── hardware.param.yaml        # แมปปิ้งขาพิน ESP32-C3, สเปก PWM เซอร์โว และระดับแรงดัน
    │   ├── kinematics.param.yaml      # ขอบเขตองศาปีก, ความถี่ และสมการฮาร์โมนิกไซน์ชีวภาพ
    │   ├── effects.param.yaml         # พาเลตต์สีไฟ LED 16 ดวง และเกณฑ์เซนเซอร์สัมผัส/แสง
    │   ├── default_config.json        # ไฟล์ JSON รวมพารามิเตอร์ทั้งหมด
    │   ├── config_loader.py           # ตัวโหลดและตรวจสอบความถูกต้องของคอนฟิกด้วย Python
    │   └── README.md                  # คู่มือการจัดการคอนฟิก
    ├── hardware/                      # วงจรไฟฟ้า, พินเอาต์, BOM และลายวงจร PCB Art
│   ├── schematic/
│   │   ├── electronic_butterfly_schematic.svg  # ผังวงจรไฟฟ้าความละเอียดสูง (Vector Schematic)
│   │   ├── pinout_guide.md                     # ตารางกำหนดขาพินและการต่อสายไฟ
│   │   └── circuit_theory.md                   # ทฤษฎีวงจร, ระบบลดสัญญาณรบกวน และ Power Budget
│   ├── pcb_art/
│   │   ├── wings_monarch_left.svg              # เวกเตอร์อาร์ตเวิร์กปีกซ้าย (Outline, Mask, Copper, Silk)
│   │   ├── wings_monarch_right.svg             # เวกเตอร์อาร์ตเวิร์กปีกขวา
│   │   └── layer_stack_guide.md                # คู่มือสั่งผลิต PCB (0.8mm FR4, ENIG Gold, JLCPCB/PCBWay)
│   └── bom/
│       └── bill_of_materials.md                # รายการอุปกรณ์ ฮาร์ดแวร์ และแหล่งจัดซื้อ
├── cad/                               # โมเดล 3 มิติ และสคริปต์ขึ้นรูปพาราเมตริก
│   ├── scripts/
│   │   └── generate_butterfly_chassis.py       # สคริปต์ Python build123d สร้างโมเดล 3D ทั้งหมด
│   ├── models/
│   │   ├── thorax_body.stl / .step             # ลำตัว/โครงกลางสำหรับยึด ESP32-C3 และเซอร์โว
│   │   ├── wing_hinge_left.stl / .step         # แคลมป์บานพับปีกซ้าย
│   │   ├── wing_hinge_right.stl / .step        # แคลมป์บานพับปีกขวา
│   │   └── desktop_perch_stand.stl / .step     # ฐานตั้งโชว์ทรงกิ่งไม้/ดอกไม้
│   └── cad_assembly_guide.md                   # คู่มือการพิมพ์ 3 มิติและการประกอบเครื่องกล
├── firmware/                          # ซอร์สโค้ดเฟิร์มแวร์สำหรับบอร์ด ESP32-C3
│   ├── esp32_c3_arduino/                      # โปรเจกต์ PlatformIO / Arduino C++
│   │   ├── platformio.ini                      # การตั้งค่า PlatformIO
│   │   └── src/
│   │       ├── main.cpp                        # โค้ดหลักเชื่อมโยงทุกระบบ
│   │       ├── Config.h                        # ค่าคอนฟิกพินและขอบเขตมุม
│   │       ├── WingKinematics.h / .cpp         # เอนจินคำนวณการกระพือปีกแบบไซน์
│   │       ├── LEDEffects.h / .cpp             # เอฟเฟกต์ไฟ 16 WS2812B ตามสโตรกปีก
│   │       ├── TouchSensor.h / .cpp            # ระบบตรวจจับสัมผัสแบบเก็บประจุ
│   │       └── WebDashboard.h / .cpp           # หน้าเว็บคอนโทรลเลอร์ฝังตัวผ่าน SoftAP
│   ├── micropython/                           # เฟิร์มแวร์ทางเลือก MicroPython
│   │   ├── boot.py
│   │   └── main.py                             # สคริปต์ MicroPython แบบสแตนด์อโลน
│   └── calibration_guide.md                    # คู่มือการปรับแต่งมุมเซอร์โวและเซนเซอร์
├── scripts/                           # เครื่องมือสร้างอาร์ตเวิร์กและทดสอบ
│   ├── procedural_wing_venation.py             # เจเนอเรเตอร์ลายเส้นปีกผีเสื้ออัลกอริทึม
│   └── test_kinematics_sim.py                  # สคริปต์จำลองคลื่นฮาร์โมนิกบนเทอร์มินัล
└── web_visualizer/                    # ซอฟต์แวร์จำลอง 3D เสมือนจริงบน WebGL
    ├── index.html                              # หน้าเว็บแอปพลิเคชัน Three.js
    ├── app.js                                  # ลอจิกการเรนเดอร์ 3D, แอนิเมชันปีก และแสงไฟ
    └── styles.css                              # ดีไซน์สไตล์ Cyberpunk HUD
```

---

## 4. วงจรอิเล็กทรอนิกส์และพินเอาต์ (Electronics & Pinout)

ดูเอกสารฉบับเต็มได้ที่ [`hardware/schematic/pinout_guide.md`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/hardware/schematic/pinout_guide.md) และผังวงจรเวกเตอร์ที่ [`hardware/schematic/electronic_butterfly_schematic.svg`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/hardware/schematic/electronic_butterfly_schematic.svg)

| Pin บนบอร์ด ESP32-C3 | อุปกรณ์ที่เชื่อมต่อ | สัญญาณ | คำอธิบาย |
| :--- | :--- | :--- | :--- |
| **GPIO6** | เซอร์โวปีกซ้าย (M1) | PWM (50 Hz) | สัญญาณพัลส์ควบคุมมุมปีกซ้าย ($15^\circ - 85^\circ$) |
| **GPIO7** | เซอร์โวปีกขวา (M2) | PWM (50 Hz) | สัญญาณพัลส์ควบคุมมุมปีกขวา (สะท้อนองศา) |
| **GPIO8** | สายสัญญาณไฟ WS2812B | Serial Data | ต่อผ่านตัวต้านทาน $330\ \Omega$ ไปยัง LED 16 ดวง |
| **GPIO1** | โฟโตรีซิสเตอร์ (LDR) | Analog ADC1_CH1 | วัดความสว่างบรรยากาศ (Voltage divider กับ $10\text{ k}\Omega$) |
| **GPIO3** | หนวดซ้าย (Antenna L) | Capacitive Touch / ADC | ตรวจจับการเปลี่ยนแปลงประจุเมื่อนิ้วมือแตะหนวด |
| **GPIO4** | หนวดขวา (Antenna R) | Capacitive Touch / ADC | ตรวจจับสัมผัสหนวดขวา |
| **GPIO9** | สวิตช์ BOOT บนบอร์ด | Digital Input (Pullup) | กดเพื่อเปลี่ยนโหมดการทำงานเมื่อไม่ได้ต่อ Wi-Fi |
| **5V (VIN)** | รางไฟจ่ายเซอร์โว & LED | Power Bus ($5\text{V}$) | ต่อตัวเก็บประจุ $220\ \mu\text{F}$ กรองกระแสกระชากจากเซอร์โว |
| **3V3** | ไฟเลี้ยงระบบตรรกะ & LDR | Power Out ($3.3\text{V}$) | จ่ายไฟนิ่งให้ชิป ESP32-C3 และวงจรแบ่งแรงดัน |
| **GND** | กราวด์รวม (Star Ground) | Ground Return | เดินสายกราวด์แบบรวมศูนย์ ป้องกันการรบกวนสัญญาณ |

---

## 5. การออกแบบศิลปะบนแผ่นวงจรพิมพ์ (PCB Art Design)

ปีกทั้งสองข้างถูกสร้างขึ้นผ่านสคริปต์พาราเมตริก [`scripts/procedural_wing_venation.py`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/scripts/procedural_wing_venation.py):
- **Substrate Thickness:** ใช้ความหนา **$0.8\text{ mm}$** เพื่อให้น้ำหนักเบาเพียง $\approx 3.5\text{ g}$ ต่อข้าง ทำให้เซอร์โวกระพือได้อย่างคล่องตัวและไม่กินกระแสเกิน
- **Surface Finish:** ผิวชุบทองคำบริสุทธิ์เคมี **ENIG (Electroless Nickel Immersion Gold)** ทำให้ลายเส้นปีกเป็นสีทองเปล่งประกาย
- **Soldermask:** หน้ากากเคลือบสีดำด้าน (Matte Black), ม่วงเข้ม (Midnight Purple) หรือเขียวมรกต (Emerald Green)
- **Stained-Glass Window Cutout:** ช่องว่างในปีกที่ไม่มีทั้ง Copper และ Soldermask ทั้งสองด้าน ทำให้เนื้อ FR4 โปร่งแสง เมื่อเปิดไฟ LED แสงจะกระจายส่องสว่างนวลตา

---

## 6. โมเดลเครื่องกล 3D และโครงสร้าง (3D Mechanical CAD)

ไฟล์ CAD 3D ทั้งหมดสร้างด้วยภาษาไพทอนผ่านไลบรารี **build123d** โดยรันสคริปต์:
```bash
./.venv/bin/python3 electronic_butterfly/scripts/generate_butterfly_chassis.py
# หรือ
python3 main.py cad
```
จะได้ไฟล์ทั้งฟอร์แมต **STL** สำหรับเครื่องพิมพ์ 3 มิติ และ **STEP (AP242)** สำหรับโปรแกรม Solid CAD (FreeCAD, Fusion 360, SolidWorks):
1. **`thorax_body.stl`:** โครงลำตัวส่วนอก ออกแบบตามหลักอากาศพลศาสตร์ มีช่องใส่บอร์ด ESP32-C3 SuperMini พร้อมช่องต่อ USB-C ท้ายลำตัว, ช่องยึดเซอร์โวมอเตอร์ 2 ช่อง และรูเดือยบานพับปีก
2. **`wing_hinge_left.stl` & `wing_hinge_right.stl`:** แคลมป์ยึดโคนปีก PCB หนา $0.8\text{ mm}$ พร้อมแขนก้านสูบ (Moment arm) สำหรับต่อลวด Pushrod ขนาด $0.8\text{ mm}$ จากก้านเซอร์โว
3. **`desktop_perch_stand.stl`:** ฐานตั้งโชว์บนโต๊ะทรงกิ่งไม้/กลีบดอกไม้ พร้อมร่องซ่อนสาย USB-C

---

## 7. เฟิร์มแวร์และอัลกอริทึมการเคลื่อนไหว (Firmware & Kinematics)

### สมการฮาร์โมนิกไซน์ชีวภาพ (Biomimetic Harmonic Kinematics):
แทนที่จะใช้คำสั่ง `for` loop แบบทื่อๆ เฟิร์มแวร์คำนวณตำแหน่งองศาปีกแบบเวลาจริงไร้การหน่วงเวลา (Non-blocking):
$$\theta(t) = \theta_{\text{center}} + A_1 \sin(2\pi f t) + A_2 \sin(4\pi f t + \phi)$$
โดยที่:
- $f$: ความถี่ในการกระพือปีก ($0.4\text{ Hz}$ ถึง $3.5\text{ Hz}$)
- $A_1$: แอมพลิจูดหลัก ($6^\circ$ ในโหมดหายใจ จนถึง $32^\circ$ ในโหมดบินเร็ว)
- $A_2, \phi$: ฮาร์โมนิกลำดับที่ 2 ช่วยจำลองอัตราเร่งและจังหวะสะบัดปลายปีกของแมลงจริง

### โหมดพฤติกรรม (Behavioral States):
1. **Sleep Mode (หลับ):** ปีกหุบขึ้นตั้ง $80^\circ$ ไฟดับสนิท (เข้าโหมดเมื่อมืด)
2. **Breathing Mode (หายใจ):** ปีกขยับเบาๆ เป็นจังหวะ $0.4\text{ Hz}$ ไฟเรืองแสงช้าๆ
3. **Flutter Mode (บินร่อนชมสวน):** กระพือปีกนุ่มนวล $1.5\text{ Hz}$
4. **Dynamic Flight (บินทรงพลัง):** กระพือเต็มระยะ $2.4\text{ Hz}$
5. **Startled Burst (สะดุ้งตกใจ):** เกิดขึ้นทันทีเมื่อแตะหนวด กระพือเร็ว $3.5\text{ Hz}$ พร้อมระเบิดแสงคลื่นช็อกเวฟสีขาว-ฟ้า
6. **Glide Mode (ร่อนนิ่ง):** ปีกกางระนาบแนวนอน $20^\circ$

---

## 8. โปรแกรมจำลองเสมือนจริง 3 มิติ (WebGL 3D Visualizer)

โปรเจกต์มีตัวจำลอง 3 มิติเสมือนจริงที่ทำงานบนเว็บเบราว์เซอร์ด้วย Three.js อยู่ในโฟลเดอร์ [`web_visualizer/`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/web_visualizer/index.html):
- แสดงผลโมเดลผีเสื้อ 3 มิติพร้อมปีก PCB Art และหลอดไฟ 16 ดวง
- แอนิเมชันปีกขยับตามสมการคณิตศาสตร์เดียวกับตัวฮาร์ดแวร์จริง
- สามารถหมุนกล้อง ซูมเข้าออก เปลี่ยนโหมดการบิน สลับพาเลตต์สีไฟ และกดปุ่มจำลองการแตะหนวดได้
- **วิธีเปิดดู:** เปิดไฟล์ [`web_visualizer/index.html`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/web_visualizer/index.html) ใน Google Chrome / Firefox / Edge หรือรันเว็บเซิร์ฟเวอร์แบบพกพา:
```bash
python3 main.py view
```
แล้วเปิด `http://localhost:8050` บนเบราว์เซอร์

---

### ขั้นตอนที่ 1: การ Build โมเดล, จำลอง และแสดงผล (Build, Simulate & Visualize)

```bash
cd /home/tacv/workspace/ElectronicsArt/electronic_butterfly

# 1. Build Model: สร้างโมเดล 3D CAD (STL/STEP), PCB Art (SVG) และซิงค์คอนฟิก
python3 scripts/build_model.py

# 2. Simulate: จำลองการกระพือปีก ตรวจสอบความปลอดภัยเชิงกล และคำนวณการใช้พลังงาน
python3 scripts/simulate_kinematics.py --power --plot

# 3. Visualize: รัน WebGL 3D Interactive Simulator พร้อมเปิดเบราว์เซอร์อัตโนมัติ
python3 scripts/visualize_model.py --browser
```

*(หรือสามารถสั่งผ่าน `make build`, `make sim`, `make view` จาก Workspace Root ได้ทันที)*

### ขั้นตอนที่ 2: การคอมไพล์และแฟลชเฟิร์มแวร์ ESP32-C3
1. เปิดโฟลเดอร์ `electronic_butterfly/firmware/esp32_c3_arduino` ใน **VS Code** ที่ติดตั้งส่วนขยาย **PlatformIO IDE**
2. เสียบสาย USB-C เข้ากับบอร์ด ESP32-C3 SuperMini
3. กดปุ่ม **Upload & Monitor** ใน PlatformIO หรือใช้คำสั่ง:
```bash
pio run -d electronic_butterfly/firmware/esp32_c3_arduino -t upload
```
4. หรือหากใช้ **Arduino IDE**:
   - เลือกบอร์ด `ESP32C3 Dev Module`
   - ตั้งค่า `USB CDC On Boot: Enabled`
   - ติดตั้งไลบรารี `ESP32Servo` และ `FastLED`
   - เปิดไฟล์ `firmware/esp32_c3_arduino/src/main.cpp` แล้วกด Upload

### ขั้นตอนที่ 3: การควบคุมผ่านสมาร์ตโฟน (Web Dashboard)
1. เมื่อเปิดเครื่อง ESP32-C3 จะปล่อยสัญญาณ Wi-Fi ชื่อ: **`CyberButterfly-ESP32`** (รหัสผ่าน: `12345678`)
2. ใช้มือถือหรือโน้ตบุ๊กเชื่อมต่อ Wi-Fi ดังกล่าว
3. เปิดเบราว์เซอร์ไปที่ **`http://192.168.4.1`**
4. คุณสามารถปรับสปีดการกระพือ, เปลี่ยนสีไฟ และสั่งงานผีเสื้อได้แบบเรียลไทม์!

---

## 📄 License
This project is open-source and licensed under the [MIT License](file:///home/tacv/workspace/ElectronicsArt/LICENSE).
Crafted with passion for Art, Robotics, and Electronics. 🦋✨
