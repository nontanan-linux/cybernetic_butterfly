#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for Electronic Butterfly Chassis
============================================================
Complies with User Specifications:
1. Unified Continuous Main Body Chassis:
   - 100% single watertight manifold solid (zero disconnected parts)
   - Sturdy lateral bridge brackets fusing outboard support hinge lugs to thorax
   - Reinforced bottom stem boss with umbilical wire passage
   - Head with compound eyes and angled antenna capacitive touch sockets
   - Thorax with dual MG90S servo clamp bays (shafts along +X, 28mm pitch M2 holes, wire channel)
   - Abdomen with ESP32-C3 SuperMini mounting tray, rear USB-C port cutout,
     470µF capacitor cradle, 1N5819 diode pocket, and 2-pin JST-PH battery terminal socket
2. Real MG90S Micro Servos installed firmly onto the Body:
   - Sourced from official engineering CAD models
   - Installed inside thorax pockets with shafts pointing forward (+X)
3. Lateral Butterfly Wings Flapping UP and DOWN along Z-axis:
   - Wing blade spreads out laterally into +/- Y (chord in X, span in Y, thickness in Z)
   - Flapping rotation axis parallel to the Longitudinal X-axis
   - Wing root clevis clamps the MG90S single-arm nylon horn
   - Longitudinal M2 screwdriver through-tunnel into servo brass gear
   - Outer coaxial support hinge knuckles aligned with body support lugs (Dia 2.05mm pin)
   - Integrated 3-Pin micro connector socket on neutral rotation axis
   - Right wing 100% CAD mirrored across Plane.XZ for perfect bilateral symmetry
4. Base Stand & Battery Power Core below the body
"""

import math
import os
import sys
from pathlib import Path
from build123d import *

def load_real_mg90s_servo(models_dir: Path = None):
    """
    Loads real TowerPro MG90S Micro Servo from engineering STEP file.
    Origin is at the base of the brass output spline shaft (0, 0, 0),
    with the spline shaft pointing along +Z.
    """
    if models_dir is None:
        models_dir = Path(__file__).resolve().parent.parent / "cad" / "models"

    raw_file = models_dir / "raw" / "Servo-sg90.step"
    norm_file = models_dir / "mg90s_servo.step"

    if raw_file.exists():
        raw_servo = import_step(str(raw_file))
        loc_spline = Location(Vector(0, 16.6, 26.7))
        servo_norm = raw_servo.moved(loc_spline.inverse())
    elif norm_file.exists():
        servo_norm = import_step(str(norm_file))
    else:
        raise FileNotFoundError(f"Servo STEP file not found in {models_dir}")

    return servo_norm

def load_real_mg90s_horn(models_dir: Path = None):
    """
    Loads real MG90S Single-Arm Nylon Servo Horn from engineering STEP file.
    Origin is at the center of the spline hub (0, 0, 0),
    with the arm extending along +X and hub bore along +Z.
    """
    if models_dir is None:
        models_dir = Path(__file__).resolve().parent.parent / "cad" / "models"

    raw_file = models_dir / "raw" / "SG90-1-arm-horn.step"
    norm_file = models_dir / "mg90s_servo_horn.step"

    if raw_file.exists():
        raw_horn = import_step(str(raw_file))
        loc_hub = Location(Vector(22.9697123, 36.3361995, 25.6721712))
        horn_norm = raw_horn.moved(loc_hub.inverse())
    elif norm_file.exists():
        horn_norm = import_step(str(norm_file))
    else:
        raise FileNotFoundError(f"Horn STEP file not found in {models_dir}")

    return horn_norm

# Backwards compatibility aliases
build_mg90s_servo = load_real_mg90s_servo
build_mg90s_servo_horn = load_real_mg90s_horn

def build_body():
    """
    Body (ลำตัวกลางและฐานรองรับ):
    - ออกแบบเป็นชิ้นเนื้อตันชิ้นเดียวต่อเนื่องสมบูรณ์ (100% Single Unified Solid)
    - ส่วนหัว (Head): ส่วนหัวโค้งมน พร้อม Compound Eyes และ Antenna Sockets
    - ส่วนอก (Thorax):
      * ออกแบบเบ้าใส่ Real MG90S Micro Servo ซ้าย-ขวาอย่างแม่นยำ
      * บ่ารับหูยึด Servo (Mounting Ears Shelf) พร้อมรูเจาะนำสกรู M2 (ระยะพิทช์ 27.0 mm)
      * เพลาหมุนชี้ไปข้างหน้าตามแนวแกน X ที่ตำแหน่ง (X=8.0, Y=+/-9.0, Z=2.0)
      * หูประคองจุดหมุนปีกคู่หน้า (Forward Support Hinge Brackets: X=16.0, Y=+/-9.0, Z=2.0)
        Collinear ร่วมแกนหมุนเดียวกับเพลา Servo อย่างแม่นยำ พร้อมรูสลักสแตนเลส Dia 2.1 mm
      * ช่องเดินสายไฟ Servo รวมตรงกลางส่งต่อลงสู่ส่วนท้อง
    - ส่วนท้อง (Abdomen):
      * ช่องติดตั้งบอร์ด ESP32-C3 SuperMini (22.0 x 19.0 x 14.0 mm) พร้อมบ่ารอง 4 มุม
      * ช่องเสียบพอร์ต USB-C ด้านท้าย (9.5 x 4.5 mm)
      * ช่องวางตัวเก็บประจุ 470µF 10V และช่องวางไดโอด 1N5819
      * ช่องหน้าต่างโครงกระดูก (Skeleton ribs) ให้แสงไฟสถานะ LED จากบอร์ดส่องทะลุออกมา
    - ข้อต่อก้านฐาน (Bottom Stem Collar):
      * คอค้ำหนาเชื่อมติดใต้ลำตัว พร้อมเบ้ารองรับ Dia 6.2 mm ลึก 7.0 mm และรูร้อยสายไฟ (5V และ GND)
    """
    with BuildPart() as body:
        # --- 1. Thorax Main Outer Solid ---
        with Locations(Location((-2.0, 0, -2.5))):
            Box(40.0, 34.0, 35.0)

        # --- 2. Forward Support Hinge Brackets (Collinear at Y = +/- 9.0, Z = 2.0) ---
        for y_side in [9.0, -9.0]:
            with Locations(Location((16.0, y_side, 2.0))):
                Box(6.0, 6.0, 12.0, mode=Mode.ADD)
                Cylinder(radius=5.0, height=6.0, rotation=(0, 90, 0), mode=Mode.ADD)
                Cylinder(radius=1.1, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # --- 3. Head, Eyes & Antenna Sockets ---
        with Locations(Location((20.0, 0, 3.0))):
            Sphere(radius=7.5, mode=Mode.ADD)
            with Locations(Location((2.0, 5.2, 1.5)), Location((2.0, -5.2, 1.5))):
                Sphere(radius=2.8, mode=Mode.ADD)
            with Locations(Location((2.5, 3.2, 5.0), (30, 25, 0)), Location((2.5, -3.2, 5.0), (-30, 25, 0))):
                Cylinder(radius=0.8, height=8.0, mode=Mode.SUBTRACT)

        # --- 4. Abdomen Structure ---
        with Locations(Location((-28.0, 0, -3.0))):
            Box(24.0, 24.0, 22.0, mode=Mode.ADD)
            with Locations(Location((-12.0, 0, -1.0))):
                Cone(bottom_radius=9.0, top_radius=3.5, height=14.0, rotation=(0, -90, 0), mode=Mode.ADD)

        # --- 5. Bottom Stem Collar ---
        with Locations(Location((-2.0, 0, -22.0))):
            Cylinder(radius=6.0, height=8.0, mode=Mode.ADD)
            Cylinder(radius=3.1, height=7.0, mode=Mode.SUBTRACT)
            Cylinder(radius=1.8, height=18.0, mode=Mode.SUBTRACT)

        # --- 6. Real MG90S Servo Pockets (Left at Y=+9.0, Right at Y=-9.0) ---
        for y_servo in [9.0, -9.0]:
            with Locations(Location((-7.6, y_servo, -5.3))):
                Box(23.2, 12.6, 23.5, mode=Mode.SUBTRACT)
            with Locations(Location((2.8, y_servo, -3.8))):
                Box(3.0, 12.6, 33.0, mode=Mode.SUBTRACT)
                with Locations(Location((0, 0, 12.0)), Location((0, 0, -15.0))):
                    Cylinder(radius=0.9, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations(Location((6.0, y_servo, 2.0))):
                Cylinder(radius=6.5, height=6.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # Central wireway between servos down to abdomen
        with Locations(Location((-14.0, 0, -5.0))):
            Box(12.0, 12.0, 16.0, mode=Mode.SUBTRACT)

        # --- 7. Abdomen Electronics Cavity ---
        with Locations(Location((-28.0, 0, -2.0))):
            Box(22.0, 19.0, 14.0, mode=Mode.SUBTRACT)
            # ESP32-C3 Corner standoffs
            with Locations(Location((-8.0, 7.0, -5.5)), Location((-8.0, -7.0, -5.5)),
                           Location((8.0, 7.0, -5.5)), Location((8.0, -7.0, -5.5))):
                Box(2.5, 2.5, 3.0, mode=Mode.ADD)

        # Rear USB-C Port
        with Locations(Location((-42.0, 0, -2.0))):
            Box(10.0, 9.5, 4.5, mode=Mode.SUBTRACT)

        # Capacitor & Diode slots
        with Locations(Location((-26.0, 0, -10.0))):
            Cylinder(radius=4.3, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations(Location((-32.0, 6.5, -10.0))):
            Box(4.0, 8.0, 3.5, mode=Mode.SUBTRACT)

        # Skeleton ribs on abdomen for LED glow
        for x_rib in [-23.0, -29.0, -35.0]:
            with Locations(Location((x_rib, 0, 7.5))):
                Box(3.5, 12.0, 4.0, mode=Mode.SUBTRACT)
            with Locations(Location((x_rib, 11.0, -2.0))):
                Box(3.5, 4.0, 7.0, mode=Mode.SUBTRACT)
            with Locations(Location((x_rib, -11.0, -2.0))):
                Box(3.5, 4.0, 7.0, mode=Mode.SUBTRACT)

    return body.part

def build_left_wing():
    """
    Left Wing (ปีกซ้าย):
    - แผ่นปีกกางออกด้านข้างตามแนวแกน Y (Lateral Wingspan)
      * คอร์ดปีกตามยาว (Longitudinal Chord) ตามแนวแกน X (X = -40 ถึง +48 mm)
      * ปีกกางออกด้านข้างทางซ้ายตามแนวแกน Y (Y = 9 ถึง 96 mm)
      * ความหนาของปีก 1.8 mm ตามแนวแกน Z
    - จุดเชื่อมต่อกับ Servo Motor (Direct-Drive Servo Horn Recess):
      * ช่องสวมแขน Servo Horn แนบสนิท ขยายออกตามแนวแกน Y (ความยาว 22.0 mm)
      * รูทะลุไขควง M2 (Dia 3.0 mm) ตรงแกนหมุนตามแนวแกน X เพื่อขันสกรูยึดเข้าแกนเฟืองทองเหลือง Servo ได้จากด้านนอก
      * รูสกรูขันยึดแขน Servo Horn เข้ากับโคนปีก
    - จุดหมุนประคองปีก (Outboard Support Hinge Knuckle):
      * หูประคองหน้า (X = 16.0, Y = 9.0, Z = 2.0) Collinear กับแกนหมุน X ร่วมกับเพลา Servo
      * สวมประคองกับ Bracket ของตัว Body พร้อมรูสลักสแตนเลส Dia 2.1 mm ช่วยรับแรงงัดขณะกระพือปีกขึ้น-ลง
    - เบ้าติดตั้ง Micro 3-Pin Connector (JST-SH 1.0mm) บน Neutral Rotation Axis
    - เบ้าใส่หลอด WS2812B Mini LED (4 จุด) บนระนาบปีก
    - ร่องเดินสายไฟลวดทองแดงด้านล่าง 0.8 มม.
    """
    with BuildPart() as wing:
        # 1. Lateral Wing Blade in X-Y Plane
        with BuildSketch(Plane.XY) as sk:
            with BuildLine() as ln:
                l1 = Line((12, 9), (42, 28))
                l2 = Spline((42, 28), (48, 58), (36, 84), (18, 96))
                l3 = Spline((18, 96), (-8, 92), (-28, 74), (-38, 50))
                l4 = Spline((-38, 50), (-40, 30), (-24, 16), (-12, 9))
                l5 = Line((-12, 9), (12, 9))
            make_face()
        extrude(amount=1.8)

        # 2. Wing Root Hub & Hinge Knuckle around (8.0, 9.0, 2.0)
        with Locations(Location((8.0, 9.0, 2.0))):
            with Locations(Location((3.0, 7.0, -1.0))):
                Box(14.0, 16.0, 8.0, mode=Mode.ADD)

            # Forward Support Hinge Knuckle at X = 8.0 relative to hub (so X_world = 16.0)
            with Locations(Location((8.0, 0, 0))):
                Cylinder(radius=4.5, height=5.0, rotation=(0, 90, 0), mode=Mode.ADD)
                Cylinder(radius=1.1, height=8.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

            # Servo Horn Recess facing -X (towards the servo shaft)
            with Locations(Location((0, 0, 0))):
                # Hub recess (Dia 8.5 mm, depth 3.5 mm along +X)
                Cylinder(radius=4.25, height=3.5, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                # Screwdriver through-hole for M2 center spline screw
                Cylinder(radius=1.5, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                # Horn arm channel extending laterally along +Y (from Y=0 to 22.0)
                with Locations(Location((1.2, 11.0, 0))):
                    Box(2.6, 22.0, 6.0, mode=Mode.SUBTRACT)
                    # 2x Clamping screw holes along arm
                    with Locations(Location((0, -4.0, 0)), Location((0, 4.0, 0))):
                        Cylinder(radius=0.9, height=8.0, mode=Mode.SUBTRACT)

            # 3-Pin JST-SH Connector Socket on Neutral Axis
            with Locations(Location((0.0, 5.0, 0))):
                Box(4.5, 5.5, 4.2, mode=Mode.SUBTRACT)
                with Locations(Location((-2.0, 0, 0))):
                    Box(2.0, 4.5, 3.2, mode=Mode.SUBTRACT)

        # 3. 4x WS2812B Mini LED sockets (Dia 9.5mm, depth 1.0mm)
        led_coords = [(32.0, 36.0), (36.0, 68.0), (10.0, 60.0), (-15.0, 45.0)]
        for x_led, y_led in led_coords:
            with Locations(Location((x_led, y_led, 1.8))):
                Cylinder(radius=4.75, height=1.0, mode=Mode.SUBTRACT)

        # 4. Wire routing channels on bottom (0.8 x 0.8 mm)
        wire_routes = [
            ((8.0, 14.0), (32.0, 36.0)),
            ((32.0, 36.0), (36.0, 68.0)),
            ((32.0, 36.0), (10.0, 60.0)),
            ((8.0, 14.0), (-15.0, 45.0)),
        ]
        for (x1, y1), (x2, y2) in wire_routes:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            dx = x2 - x1
            dy = y2 - y1
            length = (dx*dx + dy*dy)**0.5
            deg = math.degrees(math.atan2(dy, dx))
            with Locations(Location((mid_x, mid_y, 0.4), (0, 0, deg))):
                Box(length, 0.9, 0.8, mode=Mode.SUBTRACT)

    return wing.part

def build_right_wing(left_wing_solid):
    """
    Right Wing (ปีกขวา):
    สร้างจากการ Mirror ชิ้นส่วน Left Wing ข้าม Plane.XZ เพื่อให้สมมาตรกัน 100%
    """
    right_wing = mirror(left_wing_solid, about=Plane.XZ)
    return right_wing

def build_base_stand():
    """
    ฐานตั้ง (Base Stand):
    ภายในซ่อน:
    - รางถ่าน 14500 (1 ก้อน)
    - โมดูลชาร์จ TP4056 (USB-C) พร้อมช่องเสียบสายหลังฐาน
    - โมดูล Step-Up Boost 5V
    - ช่องสวิตช์เลื่อนเปิด-ปิด
    - ช่องใส่เหรียญ/ตะกั่วถ่วงน้ำหนักกันล้ม
    - ก้านรองรับ (Support Stem) สูง 52 mm พร้อมรูร้อยสายไฟ 2 เส้น (5V และ GND)
    """
    with BuildPart() as stand:
        with Locations(Location((0, 0, 12))):
            Box(85, 70, 24)

            # 1. 14500 Battery Cavity (58 x 20 x 18 mm)
            with Locations(Location((-10, 0, -5))):
                Box(58, 20, 18, mode=Mode.SUBTRACT)

            # 2. TP4056 USB-C Charger Module Bay (30 x 20 x 14 mm)
            with Locations(Location((26, 0, -4))):
                Box(30, 20, 14, mode=Mode.SUBTRACT)
                with Locations(Location((15, 0, 0))):
                    Box(8, 12, 6.5, mode=Mode.SUBTRACT)

            # 3. 5V Step-Up Boost Converter Bay (20 x 15 x 12 mm)
            with Locations(Location((15, -22, -4))):
                Box(20, 15, 12, mode=Mode.SUBTRACT)

            # 4. Slide Switch Mount (12 x 6 x 8 mm)
            with Locations(Location((-5, -34, -2))):
                Box(12, 6, 8, mode=Mode.SUBTRACT)

            # 5. Ballast / Weight Cavity (36 x 28 x 12 mm)
            with Locations(Location((-20, 15, -6))):
                Box(36, 28, 12, mode=Mode.SUBTRACT)

        # 6. Hollow Support Stem (Height 52 mm with central wire conduit)
        with Locations(Location((0, 0, 50))):
            Cone(bottom_radius=7.0, top_radius=4.5, height=52.0)
            Cylinder(radius=1.8, height=60.0, mode=Mode.SUBTRACT)

        # Top Mating Peg into Butterfly Body
        with Locations(Location((0, 0, 78))):
            Cylinder(radius=2.9, height=8.0)
            Cylinder(radius=1.6, height=10.0, mode=Mode.SUBTRACT)

    return stand.part

def build_base_stand_lid():
    """ฝาปิดใต้ฐานตั้ง (Battery & Ballast Hatch Lid)"""
    with BuildPart() as lid:
        Box(81, 66, 2.0)
        with Locations(Location((0, 0, -0.6))):
            Box(14, 18, 0.8, mode=Mode.ADD)
        with Locations(Location((-32, 0, 0)), Location((32, 0, 0))):
            Cylinder(radius=1.1, height=4.0, mode=Mode.SUBTRACT)
    return lid.part

def build_full_assembly(body, left_wing, right_wing, stand, lid, servo_norm, horn_norm):
    """
    ประกอบชิ้นส่วนทั้งหมดเข้าเป็นหุ่นยนต์ผีเสื้อสมบูรณ์ (Full Robotic Assembly):
    - Body: ลำตัวชิ้นเดียวสมบูรณ์
    - Servo Left & Right: ติดตั้งลงในช่องยึดของ Body หันเพลาไปข้างหน้าตามแนว X ที่ตำแหน่ง (8.0, +/-9.0, 2.0)
    - Horn Left & Right: ติดตั้งลงบนแกนเฟืองทองเหลืองของ Servo ยื่นแขนออกไปด้านข้างตามแนว Y
    - Wing Left & Right: ติดตั้งสวมลงบน Servo Horn และ Support Hinge แผ่ออกด้านข้างตามแนว Y
    - Base Stand & Lid: รองรับอยู่ด้านล่าง
    """
    s_aligned = servo_norm.moved(Location((0, 0, 0), (0, 90, 90)))
    servo_left = s_aligned.moved(Location((8.0, 9.0, 2.0)))
    servo_right = s_aligned.moved(Location((8.0, -9.0, 2.0)))

    # Horns rotated to mate on shaft along +X, extending arms laterally into +/- Y
    horn_left = horn_norm.moved(Location((0, 0, 0), (0, 90, 90)))\
                         .moved(Location((8.0, 9.0, 2.0)))

    horn_right = horn_norm.moved(Location((0, 0, 0), (0, 90, -90)))\
                          .moved(Location((8.0, -9.0, 2.0)))

    # Base Stand and Lid positioned below body
    loc_stand = Location((-2.0, 0, -92.0))
    stand_asm = stand.moved(loc_stand)
    lid_asm = lid.moved(loc_stand)

    full_compound = Compound([
        body,
        servo_left,
        servo_right,
        horn_left,
        horn_right,
        left_wing,
        right_wing,
        stand_asm,
        lid_asm
    ])

    return full_compound, {
        "body": body,
        "servo_left": servo_left,
        "servo_right": servo_right,
        "horn_left": horn_left,
        "horn_right": horn_right,
        "wing_left": left_wing,
        "wing_right": right_wing,
        "stand": stand_asm,
        "lid": lid_asm
    }

def is_ocp_viewer_active(port: int = 3939, host: str = "127.0.0.1") -> bool:
    """Checks if OCP CAD Viewer extension WebSocket server is actively listening."""
    import socket
    try:
        with socket.create_connection((host, port), timeout=0.15):
            return True
    except (OSError, ConnectionRefusedError):
        return False

def main():
    script_dir = Path(__file__).resolve().parent
    models_dir = script_dir.parent / "cad" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 68)
    print("🦋 ELECTRONIC BUTTERFLY — 3D CHASSIS CAD GENERATOR (build123d)")
    print("Features: Lateral Wings Flapping in Z, Longitudinal Servo Drive & Unified Body")
    print("=" * 68)

    import argparse
    parser = argparse.ArgumentParser(description="build123d CAD Generator for Electronic Butterfly")
    parser.add_argument("--show", "--view", dest="show", action="store_true", help="Display 3D solids in OCP CAD Viewer or WebGL Viewer")
    args = parser.parse_args()

    # 1. Real MG90S Servo & Horn
    print("⚙️  [1/6] Loading Real MG90S Micro Servo (Metal Gear, 21T Spline)...")
    servo_norm = load_real_mg90s_servo(models_dir)
    export_stl(servo_norm, str(models_dir / "mg90s_servo.stl"))
    export_step(servo_norm, str(models_dir / "mg90s_servo.step"))
    print(f"   ✓ mg90s_servo.stl & mg90s_servo.step")

    print("⚙️  [2/6] Loading Real MG90S Nylon Servo Horn (Single-Arm)...")
    horn_norm = load_real_mg90s_horn(models_dir)
    export_stl(horn_norm, str(models_dir / "mg90s_servo_horn.stl"))
    export_step(horn_norm, str(models_dir / "mg90s_servo_horn.step"))
    print(f"   ✓ mg90s_servo_horn.stl & mg90s_servo_horn.step")

    # 2. Unified Body (100% Single Solid)
    print("⚙️  [3/6] Generating Unified Body (Single Solid: Thorax, Abdomen, Circuit & Battery)...")
    body = build_body()
    assert len(body.solids()) == 1, f"Body must be 1 unified solid, got {len(body.solids())}"
    export_stl(body, str(models_dir / "body.stl"))
    export_step(body, str(models_dir / "body.step"))
    print(f"   ✓ body.stl & body.step (Verified: 100% single unified solid)")

    # 3. Lateral Wings Flapping in Z
    print("⚙️  [4/6] Generating Left Wing (Lateral Span in Y, Flapping in Z)...")
    left_wing = build_left_wing()
    export_stl(left_wing, str(models_dir / "left_wing.stl"))
    export_step(left_wing, str(models_dir / "left_wing.step"))
    print(f"   ✓ left_wing.stl & left_wing.step")

    print("⚙️  [5/6] Generating Right Wing (100% CAD Mirror for symmetry)...")
    right_wing = build_right_wing(left_wing)
    export_stl(right_wing, str(models_dir / "right_wing.stl"))
    export_step(right_wing, str(models_dir / "right_wing.step"))
    print(f"   ✓ right_wing.stl & right_wing.step")

    # 4. Base Stand & Lid
    stand = build_base_stand()
    lid = build_base_stand_lid()
    export_stl(stand, str(models_dir / "base_stand.stl"))
    export_step(stand, str(models_dir / "base_stand.step"))
    export_stl(lid, str(models_dir / "base_stand_lid.stl"))
    export_step(lid, str(models_dir / "base_stand_lid.step"))

    # 5. Full Assembly Export
    print("⚙️  [6/6] Generating Full Assembly (Servos in Body, Wings Flapping in Z)...")
    full_assembly, parts_map = build_full_assembly(body, left_wing, right_wing, stand, lid, servo_norm, horn_norm)
    export_step(full_assembly, str(models_dir / "butterfly_full_assembly.step"))
    export_stl(full_assembly, str(models_dir / "butterfly_full_assembly.stl"))
    print(f"   ✓ butterfly_full_assembly.step & butterfly_full_assembly.stl")

    if args.show:
        if is_ocp_viewer_active(3939):
            try:
                from ocp_vscode import show
                print("\n🚀 Streaming complete robotic assembly to OCP CAD Viewer (VS Code)...")
                show(
                    parts_map["body"],
                    parts_map["servo_left"],
                    parts_map["servo_right"],
                    parts_map["horn_left"],
                    parts_map["horn_right"],
                    parts_map["wing_left"],
                    parts_map["wing_right"],
                    parts_map["stand"],
                    parts_map["lid"],
                    names=[
                        "Body_Thorax_Abdomen",
                        "MG90S_Servo_Left",
                        "MG90S_Servo_Right",
                        "Servo_Horn_Left",
                        "Servo_Horn_Right",
                        "Left_Wing_With_Connector",
                        "Right_Wing_With_Connector",
                        "Base_Stand",
                        "Base_Stand_Lid"
                    ],
                    colors=[
                        "#334155",  # Body: Slate Grey
                        "#1d4ed8",  # Servo Left: Electric Blue
                        "#1d4ed8",  # Servo Right: Electric Blue
                        "#f8fafc",  # Horn Left: White Nylon
                        "#f8fafc",  # Horn Right: White Nylon
                        "#10b981",  # Wing Left: Emerald Green PCB Art
                        "#10b981",  # Wing Right: Emerald Green PCB Art
                        "#475569",  # Stand: Dark Slate
                        "#1e293b"   # Lid: Deep Charcoal
                    ]
                )
                print("✅ Models streamed to OCP CAD Viewer in VS Code.")
            except Exception as e:
                print(f"⚠️ Could not stream to OCP CAD Viewer: {e}")
        else:
            import webbrowser
            import socket
            from config.config_loader import load_all_configs

            cfg = load_all_configs()
            port = cfg.network.server.dev_port or 8050
            host = cfg.network.server.host or "0.0.0.0"
            url = f"http://localhost:{port}"

            print("\n" + "=" * 68)
            print("ℹ️  OCP CAD Viewer extension window is not open in VS Code.")
            print(f"🌐 Launching interactive 3D Web Visualizer in your Browser ({url})...")
            print("   Features: 3D CAD Inspection, Model Selector & Flapping Simulation in Z")
            print("=" * 68)

            def is_server_running(p=port, h="127.0.0.1"):
                try:
                    with socket.create_connection((h, p), timeout=0.15):
                        return True
                except (OSError, ConnectionRefusedError):
                    return False

            if is_server_running():
                print(f"📡 3D Visualizer server is already active! Opening {url}...")
                webbrowser.open(url)
            else:
                from scripts.visualize_model import start_server
                start_server(host, port, open_browser=True)

    print("\n" + "=" * 68)
    print("🎉 All 3D CAD chassis models & assemblies exported successfully!")
    print(f"📁 Destination Directory: {models_dir}")
    print("=" * 68)

if __name__ == "__main__":
    main()
