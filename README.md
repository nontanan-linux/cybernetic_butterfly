# ElectronicsArt 🎨⚡

> **A collection of creative electronics, interactive PCB art, and kinetic robotic sculptures.**  
> *คลังรวมผลงานศิลปะอิเล็กทรอนิกส์, ลายวงจรพิมพ์เชิงศิลปะ (PCB Art) และประติมากรรมหุ่นยนต์ชีวภาพ (Kinetic Robotics)*

---

## 📁 Projects Index (รายการโปรเจกต์)

| Project Directory | Description (คำอธิบาย) | Platform | Key Technologies |
| :--- | :--- | :--- | :--- |
| **[`electronic_butterfly/`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/README.md)** | **Cybernetic Butterfly (ผีเสื้อไซเบอร์เนติกส์)**<br>ประติมากรรมผีเสื้อปีกกระพือชีวภาพ ลายวงจร PCB Art เรืองแสง แตะหนวดตอบสนองด้วยสัมผัสความจุไฟฟ้า พร้อมเว็บคอนโทรลเลอร์ไร้สาย | ESP32-C3 SuperMini | • Dual Servo Sine Kinematics<br>• 16x WS2812B Wing Vein LEDs<br>• Capacitive Touch Antennae<br>• build123d 3D CAD (STL/STEP)<br>• WebGL 3D Simulator (Three.js) |

---

## 🚀 Workspace Setup (การติดตั้งสภาพแวดล้อมรวม)

สภาพแวดล้อม Python ถูกติดตั้งไว้ในระดับรากของ Workspace (`.venv`) ซึ่งสามารถใช้งานร่วมกันได้ทุกโปรเจกต์:

```bash
cd /home/tacv/workspace/ElectronicsArt

# 1. เรียกใช้งาน Virtual Environment
source .venv/bin/activate

# 2. ติดตั้ง Dependencies (หากต้องการเพิ่มเติม)
pip install -r electronic_butterfly/requirements.txt
```

---

## 🛠️ Automated Commands (Build, Simulate & Visualize)

คุณสามารถสั่งการทำงานผ่าน **Makefile** จากโฟลเดอร์หลักได้ทันที:

```bash
cd /home/tacv/workspace/ElectronicsArt

make help        # ดูรายการคำสั่งทั้งหมด
make build       # 1. Build: สร้างโมเดล 3D CAD (STL/STEP), PCB Art (SVG) และซิงค์คอนฟิก
make sim         # 2. Simulate: จำลองการเคลื่อนไหว คำนวณพลังงาน และพล็อตภาพกราฟ
make view        # 3. Visualize: เปิด WebGL 3D Simulator เซิร์ฟเวอร์
```

หรือสั่งผ่าน Python Script โดยตรงภายในไดเรกทอรี `electronic_butterfly/`:
```bash
cd /home/tacv/workspace/ElectronicsArt/electronic_butterfly

# 1. Build Model: สร้าง CAD, PCB Art และซิงค์คอนฟิกข้ามระบบ
python3 scripts/build_model.py

# 2. Simulation: จำลองกลศาสตร์และการใช้พลังงาน
python3 scripts/simulate_kinematics.py --mode flutter --power --plot

# 3. Visualization: รันเซิร์ฟเวอร์จำลอง 3 มิติบนเว็บ
python3 scripts/visualize_model.py --browser
```

ดูรายละเอียดและคู่มือฉบับเต็มได้ที่ **[`electronic_butterfly/README.md`](file:///home/tacv/workspace/ElectronicsArt/electronic_butterfly/README.md)**
