#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for Electronic Butterfly Chassis (build123d)
========================================================================
Architecture & File Separation:
- External Hardware CAD (Read-Only in cad/external/ — NEVER modified or overwritten):
  * cad/external/Servo-sg90.step (and mg90s_servo.stl for WebGL viewer)
  * cad/external/SG90-1-arm-horn.step (and mg90s_servo_horn.stl for WebGL viewer)
- Generated Custom 3D-Printed Parts (Exported as .STL ONLY in cad/models/):
  1. body.stl:
     - Head with sweeping Clubbed Butterfly Antennae, Compound Eyes & Coiled Proboscis
     - Streamlined Thorax & Elongated Abdomen with a 100% FLAT & FLUSH Ventral Belly Plane (Z = -19.8 mm)
     - Integrated snap-in 14500 Li-ion Battery Compartment (51.5 x Ø15.0 mm) & ESP32-C3 Upper Deck
  2. left_wing.stl:
     - 2x Larger Swallowtail Butterfly Wing matching reference silhouette (Wingspan = 464 mm, Chord = 298 mm)
     - 40% Thinner profile (1.20 mm raised veins & border framing 0.52 mm translucent petal cells)
     - Distinct Forewing with deep horizontal cleft, scalloped Hindwing, and long spatulate Swallowtail tip
  3. right_wing.stl:
     - 100% CAD Mirror of left_wing.stl across Plane.XZ
  4. butterfly_legs.stl:
     - Coplanar flat sternal mounting plate recessed flush at Z = -19.8 mm + 6 tucked Lepidoptera legs
- Generated Full Assembly (Exported as BOTH .STL and .STEP in cad/models/):
  5. butterfly_full_assembly.stl & butterfly_full_assembly.step
"""

import math
import os
import sys
from pathlib import Path
from build123d import *

PROJECT_DIR = Path(__file__).resolve().parent.parent
EXTERNAL_CAD_DIR = PROJECT_DIR / "cad" / "external"
GENERATED_CAD_DIR = PROJECT_DIR / "cad" / "models"

def load_external_mg90s_servo(external_dir: Path = EXTERNAL_CAD_DIR):
    """
    Reads (without modifying or overwriting) the external MG90S Micro Servo STEP model
    and normalizes its coordinate frame in memory so the origin (0, 0, 0) is at the base
    of the brass output spline shaft pointing along +Z.
    """
    raw_file = external_dir / "Servo-sg90.step"
    if not raw_file.exists():
        raise FileNotFoundError(f"External servo STEP file not found: {raw_file}")

    raw_servo = import_step(str(raw_file))
    loc_spline = Location(Vector(0, 16.6, 26.7))
    return raw_servo.moved(loc_spline.inverse())

def load_external_mg90s_horn(external_dir: Path = EXTERNAL_CAD_DIR):
    """
    Reads (without modifying or overwriting) the external MG90S Single-Arm Horn STEP model
    and normalizes its coordinate frame in memory so the origin (0, 0, 0) is at the exact
    center of the 8mm spline hub, with the internal spline socket engaging Z = [0.3, 3.3].
    """
    raw_file = external_dir / "SG90-1-arm-horn.step"
    if not raw_file.exists():
        raise FileNotFoundError(f"External horn STEP file not found: {raw_file}")

    raw_horn = import_step(str(raw_file))
    return (
        raw_horn
        .moved(Location(Vector(26.9697123, 36.3361995, 30.6721712)).inverse())
        .moved(Location((0, 0, 0), (180, 0, 0)))
        .moved(Location((0, 0, 0.3)))
    )

def _add_tapered_segment(p1, p2, r1, r2, add_start_sphere=True, add_end_sphere=True):
    """
    Constructs a smooth organic tapered segment (Cone + spherical joint condyles)
    from 3D point p1 (radius r1) to p2 (radius r2) inside an active BuildPart context.
    """
    v1 = Vector(*p1)
    v2 = Vector(*p2)
    dv = v2 - v1
    length = dv.length
    plane = Plane(origin=v1, z_dir=dv)
    with Locations(plane):
        Cone(
            bottom_radius=r1,
            top_radius=r2,
            height=length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.ADD,
        )
    if add_start_sphere:
        with Locations(Location(p1)):
            Sphere(radius=r1, mode=Mode.ADD)
    if add_end_sphere:
        with Locations(Location(p2)):
            Sphere(radius=r2, mode=Mode.ADD)

def build_body():
    """
    Body (ลำตัวผีเสื้อชิ้นเดียวสมบูรณ์ ท้องด้านล่างที่ติดกับขาราบสนิท 100% ที่ระนาบ Z = -19.8 mm):
    1. ส่วนหัวและหนวดผีเสื้อ (Head, Sweeping Clubbed Antennae, Compound Eyes & Coiled Proboscis):
       - หัวโค้งมน ตาประกอบคู่ใหญ่ งวงขดใต้หัว และหนวดผีเสื้อคู่หน้าปลายป่องโค้งยาว
    2. ส่วนอกและส่วนท้องที่ท้องด้านล่างราบสนิทเป็นระนาบเดียวกัน (100% Flat Ventral Belly at Z = -19.8 mm):
       - ใต้ท้องส่วนอกและส่วนท้องอยู่ในระนาบ Z = -19.8 mm เรียบเสมอกันทั้งหมด ไม่มีปุ่มหรือกล่องยื่นลงมา
       - มีเบ้าตื้นใต้ส่วนอก (Z = [-19.8, -17.2]) ให้แป้นฐานขาผีเสื้อ (butterfly_legs.stl) ฝังจมราบสนิท
         เสมอกับผิวท้อง Z = -19.8 mm พอดี
    3. ช่องใส่ถ่านชาร์จ 14500 Li-ion (Ø15.0 x 51.5 mm) ชั้นล่างของส่วนท้อง และห้องวางบอร์ด ESP32-C3 ชั้นบน
    """
    with BuildPart() as body:
        # --- 1. Thorax Main Shell with Flat Ventral Belly at Z = -19.8 mm (Z=[-19.8, +9.6]) ---
        with Locations(Location((-6.45, 0, -5.1))):
            Box(28.1, 32.4, 29.4)
        # Sculpted Rounded Dorsal Mesothoracic Dome
        with Locations(Location((-6.0, 0, 7.2))):
            Cylinder(radius=10.2, height=24.0, rotation=(0, 90, 0), mode=Mode.ADD)
        # Upper Servo Mounting-Ear Bosses (Top only up to Z=+13.8; Bottom stays 100% flat at Z=-19.8!)
        for y_ear in [10.0, -10.0]:
            with Locations(Location((-1.5, y_ear, -3.0))):
                Box(7.8, 12.4, 33.6, mode=Mode.ADD)

        # --- 2. Prothorax Central Neck & Forward Support Hinge Brackets ---
        with Locations(Location((13.7, 0, 1.0))):
            Box(13.4, 7.8, 15.0, mode=Mode.ADD)

        with Locations(Location((18.4, 0, 2.0))):
            Box(4.0, 18.0, 9.0, mode=Mode.ADD)

        for y_side in [9.0, -9.0]:
            with Locations(Location((18.4, y_side, 2.0))):
                Cylinder(radius=4.5, height=4.0, rotation=(0, 90, 0), mode=Mode.ADD)
                Cylinder(radius=1.55, height=6.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # --- 3. Head, Compound Eyes, Coiled Proboscis & Clubbed Butterfly Antennae ---
        with Locations(Location((23.5, 0, 2.5))):
            Sphere(radius=5.8, mode=Mode.ADD)
            with Locations(Location((1.5, 4.4, 1.0)), Location((1.5, -4.4, 1.0))):
                Sphere(radius=2.7, mode=Mode.ADD)
            with Locations(Location((3.2, 0, -4.2))):
                Cylinder(radius=2.5, height=1.6, rotation=(90, 0, 0), mode=Mode.ADD)
                Cylinder(radius=1.1, height=2.2, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Sweeping Clubbed Butterfly Antennae (หนวดผีเสื้อคู่หน้าโค้งยาวปลายป่องตามภาพตัวอย่าง)
        for sgn in [1.0, -1.0]:
            ant_p0 = (24.5, sgn * 2.2, 6.2)
            ant_p1 = (35.0, sgn * 6.0, 13.0)
            ant_p2 = (48.0, sgn * 12.5, 19.5)
            ant_p3 = (60.0, sgn * 20.0, 24.0)
            ant_p4 = (65.0, sgn * 24.5, 25.0)
            ant_p5 = (66.5, sgn * 27.5, 24.2)

            _add_tapered_segment(ant_p0, ant_p1, 0.95, 0.75, add_start_sphere=True, add_end_sphere=True)
            _add_tapered_segment(ant_p1, ant_p2, 0.75, 0.65, add_start_sphere=False, add_end_sphere=True)
            _add_tapered_segment(ant_p2, ant_p3, 0.65, 0.70, add_start_sphere=False, add_end_sphere=True)
            _add_tapered_segment(ant_p3, ant_p4, 0.70, 1.40, add_start_sphere=False, add_end_sphere=True)
            _add_tapered_segment(ant_p4, ant_p5, 1.40, 0.50, add_start_sphere=False, add_end_sphere=True)

        # --- 4. Elongated Abdomen Coplanar with Flat Belly Z = -19.8 mm (X=[-76.0, -19.5]) ---
        # Flat-bottomed Abdomen Hull (Z = [-19.8, +5.8], Y = [-10.6, +10.6], X = [-68.0, -19.5])
        with Locations(Location((-43.75, 0, -7.0))):
            Box(48.5, 21.2, 25.6, mode=Mode.ADD)
        # Sculpted Posterior Abdominal Tail Cone (X=[-76.0, -68.0])
        with Locations(Location((-72.0, 0, -6.5))):
            Cone(
                bottom_radius=9.0,
                top_radius=2.8,
                height=8.0,
                rotation=(0, -90, 0),
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.ADD,
            )
        with Locations(Location((-75.8, 0, -6.5))):
            Sphere(radius=2.8, mode=Mode.ADD)

        # --- 5. Flush Rectangular Pocket in Flat Belly for Coplanar Leg Sternum Plate ---
        # Pocket spans X=[-17.5, +5.5], Y=[-3.8, +3.8], Z=[-19.8, -16.8]
        with Locations(Location((-6.0, 0, -18.3))):
            Box(23.0, 7.6, 3.0, mode=Mode.SUBTRACT)
        with Locations(Location((-8.0, 0, -15.5))):
            Cylinder(radius=2.55, height=4.0, mode=Mode.SUBTRACT)

        # --- 6. Real MG90S Servo Pockets (Left at Y=+9.0, Right at Y=-9.0) ---
        for y_servo in [9.0, -9.0]:
            with Locations(Location((-5.55, y_servo, -3.35))):
                Box(27.1, 12.6, 23.3, mode=Mode.SUBTRACT)
            with Locations(Location((-1.55, y_servo, -3.10))):
                Box(3.3, 12.6, 33.2, mode=Mode.SUBTRACT)
            with Locations(Location((0.0, y_servo, 10.13)), Location((0.0, y_servo, -16.83))):
                Cylinder(radius=0.85, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # Central internal wire conduit from thorax servos to abdomen electronics & battery bay
        with Locations(Location((-16.0, 0, -3.5))):
            Box(12.0, 10.0, 14.0, mode=Mode.SUBTRACT)

        # --- 7. Dedicated 14500 Li-ion Battery Compartment in Lower Abdomen (Ø15.0 x 51.5 mm) ---
        with Locations(Location((-44.5, 0, -10.5))):
            Cylinder(radius=7.5, height=51.5, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Snap-in ventral battery insertion slot opening through flat belly Z = -19.8 mm
        with Locations(Location((-44.5, 0, -16.0))):
            Box(48.5, 13.6, 8.0, mode=Mode.SUBTRACT)
        # Side SPDT Slide Switch Mount Slot on Abdomen
        with Locations(Location((-24.0, -9.5, -5.0))):
            Box(8.0, 4.0, 4.5, mode=Mode.SUBTRACT)

        # --- 8. Upper Dorsal ESP32-C3 SuperMini, TP4056, 470µF Capacitor & 1N5819 Diode Deck ---
        with Locations(Location((-42.0, 0, 0.8))):
            Box(39.0, 17.6, 7.6, mode=Mode.SUBTRACT)
        with Locations(Location((-64.0, 0, 0.8))):
            Box(9.0, 9.4, 4.4, mode=Mode.SUBTRACT)
        for x_rib in [-26.0, -33.0, -40.0, -47.0, -54.0]:
            with Locations(Location((x_rib, 0, 4.8))):
                Box(3.2, 12.0, 3.0, mode=Mode.SUBTRACT)
            with Locations(Location((x_rib, 9.8, 0.8)), Location((x_rib, -9.8, 0.8))):
                Box(3.2, 3.5, 4.5, mode=Mode.SUBTRACT)

    return body.part

def build_left_wing():
    """
    Left Wing (ปีกผีเสื้อหางติ่งตามภาพตัวอย่าง ขยายขนาดใหญ่ขึ้นอีกเท่าตัว และบางลง 40%):
    - ขนาดใหญ่ขึ้น 2 เท่า:
      * กางปีกต่อข้าง Y = 9.0 ถึง 232.0 mm (ความกว้างปีกรวมซ้าย-ขวา Wingspan = 464.0 mm ~ 2x ของเดิม 236 mm)
      * ความยาวคอร์ดปีก X = -160.0 mm (ปลายติ่งหางยาว) ถึง +138.0 mm (ยอดปีกคู่หน้า) รวม 298.0 mm (>2x ของเดิม)
    - ความหนาใบปีกและเส้นเลือดบางลง 40%:
      * ความหนาโครงขอบปีกและเส้นเลือดหลัก ลดจาก 2.00 mm ลง 40% เหลือ 1.20 mm (Z = [1.40, 2.60] สมมาตรบนระนาบแกนหมุน Z = 2.0)
      * แผ่นเยื่อปีกในช่องเซลล์บางเพียง 0.52 mm (Z = [1.74, 2.26])
    - รูปทรงตรงตามภาพตัวอย่าง:
      * ปีกคู่หน้า (Forewing) กวาดเฉียงขึ้นเป็นสามเหลี่ยมมุมมนขนาดใหญ่ ขอบล่างตัดเว้าลึกแยกจากปีกหลังชัดเจน
      * ปีกคู่หลัง (Hindwing) ขอบนอกหยักเป็นคลื่น พร้อมติ่งหางผีเสื้อเรียวยาว (Long Spatulate Swallowtail) ที่ปลายมีดุมจุดกลม
    """
    with BuildPart() as wing:
        # 1. Full 2x-Scale Reference Swallowtail Butterfly Wing Blade (1.20 mm thick -> Z = [1.40, 2.60])
        with BuildSketch(Plane.XY.offset(1.40)) as sk_outer:
            with BuildLine() as ln_outer:
                # Root stalk attachment
                Line((8.5, 13.0), (15.0, 13.0))
                Line((15.0, 13.0), (15.0, 22.0))
                # Forewing Leading Edge (Costa) sweeping up at diagonal to High Forewing Apex
                Spline((15.0, 22.0), (48.0, 48.0), (88.0, 95.0), (124.0, 158.0), (138.0, 208.0), (128.0, 228.0))
                # Forewing Outer Margin (Termen) dropping from high apex to rounded lower tornus corner
                Spline((128.0, 228.0), (98.0, 232.0), (62.0, 224.0), (32.0, 212.0), (18.0, 198.0))
                # Forewing Bottom Edge cutting nearly horizontally inward into the Deep Inter-Wing Cleft
                Spline((18.0, 198.0), (8.0, 165.0), (4.0, 118.0), (2.0, 68.0))
                # Hindwing Upper Lobe flaring out beneath the Forewing
                Spline((2.0, 68.0), (-4.0, 115.0), (-12.0, 152.0), (-28.0, 164.0))
                # Hindwing Scalloped Outer Margin (Wave Lobe 1 & 2 & 3)
                Spline((-28.0, 164.0), (-46.0, 168.0), (-62.0, 156.0))
                Spline((-62.0, 156.0), (-76.0, 158.0), (-90.0, 144.0))
                Spline((-90.0, 144.0), (-102.0, 142.0), (-112.0, 128.0))
                # Long Spatulate Swallowtail Projection (ติ่งหางยาวพุ่งเฉียงลงด้านหลัง ปลายป่องมนเหมือนในภาพ)
                Spline((-112.0, 128.0), (-132.0, 120.0), (-152.0, 115.0), (-160.0, 108.0))
                Spline((-160.0, 108.0), (-154.0, 99.0), (-134.0, 104.0), (-114.0, 110.0))
                # Hindwing Inner Posterior Scallops & Anal Lobe
                Spline((-114.0, 110.0), (-118.0, 92.0), (-110.0, 74.0))
                Spline((-110.0, 74.0), (-96.0, 52.0), (-76.0, 34.0))
                # Hindwing Anal Margin curving smoothly alongside Abdomen back to Root
                Spline((-76.0, 34.0), (-48.0, 23.5), (-16.0, 22.0), (8.5, 22.0))
                Line((8.5, 22.0), (8.5, 13.0))
            make_face()
        extrude(amount=1.20)

        # 2. Recessed Translucent Wing Membrane Basins (40% thinner -> 0.52 mm inner membrane Z=[1.74, 2.26])
        # Leaves wide outer dark border band matching the reference illustration
        for z_offset, cut_depth in [(2.26, 0.38), (1.36, 0.38)]:
            # Forewing Inner Petal Basin
            with BuildSketch(Plane.XY.offset(z_offset)) as sk_fw_cell:
                with BuildLine() as ln_fw:
                    Spline((18.0, 28.0), (46.0, 52.0), (80.0, 94.0), (104.0, 145.0), (108.0, 182.0), (98.0, 198.0))
                    Spline((98.0, 198.0), (74.0, 202.0), (48.0, 196.0), (26.0, 184.0))
                    Spline((26.0, 184.0), (14.0, 160.0), (10.0, 118.0), (8.0, 72.0))
                    Spline((8.0, 72.0), (10.0, 48.0), (14.0, 34.0), (18.0, 28.0))
                make_face()
            extrude(amount=cut_depth, mode=Mode.SUBTRACT)

            # Hindwing Inner Petal Basin
            with BuildSketch(Plane.XY.offset(z_offset)) as sk_hw_cell:
                with BuildLine() as ln_hw:
                    Spline((-2.0, 62.0), (-8.0, 102.0), (-15.0, 132.0), (-28.0, 142.0))
                    Spline((-28.0, 142.0), (-44.0, 144.0), (-60.0, 134.0), (-74.0, 126.0))
                    Spline((-74.0, 126.0), (-86.0, 112.0), (-92.0, 92.0), (-90.0, 72.0))
                    Spline((-90.0, 72.0), (-78.0, 50.0), (-58.0, 34.0), (-32.0, 28.0))
                    Spline((-32.0, 28.0), (-12.0, 28.0), (-2.0, 42.0), (-2.0, 62.0))
                make_face()
            extrude(amount=cut_depth, mode=Mode.SUBTRACT)

        # 3. Raised 3D Fan-Like Petal Veins & Swallowtail Midrib (1.20 mm thick, Z = [1.40, 2.60])
        vein_segments = [
            # Forewing Basal Pink Triangle Cell Divider & Radial Fan Petal Veins (matching reference image)
            ((15.0, 24.0), (68.0, 78.0), 2.4),
            ((68.0, 78.0), (36.0, 110.0), 2.2),
            ((15.0, 24.0), (36.0, 110.0), 2.4),
            ((68.0, 78.0), (105.0, 185.0), 2.2),   # Radial Petal Vein 1
            ((54.0, 92.0), (86.0, 198.0), 2.2),    # Radial Petal Vein 2
            ((44.0, 102.0), (64.0, 198.0), 2.2),   # Radial Petal Vein 3
            ((36.0, 110.0), (42.0, 192.0), 2.2),   # Radial Petal Vein 4
            ((36.0, 110.0), (20.0, 180.0), 2.0),   # Radial Petal Vein 5
            ((15.0, 24.0), (2.0, 68.0), 2.6),      # Inter-Wing Cleft Structural Spar
            # Hindwing Fan-Like Radial Petal Veins & Long Swallowtail Midrib
            ((10.0, 24.0), (-24.0, 62.0), 2.4),
            ((-24.0, 62.0), (-24.0, 142.0), 2.0),  # Hindwing Petal Vein 1
            ((-24.0, 62.0), (-48.0, 142.0), 2.0),  # Hindwing Petal Vein 2
            ((-24.0, 62.0), (-70.0, 130.0), 2.2),  # Hindwing Petal Vein 3
            ((-70.0, 130.0), (-113.0, 119.0), 2.2),
            ((-113.0, 119.0), (-155.0, 107.0), 1.8), # Long Swallowtail Central Midrib
            ((-24.0, 62.0), (-86.0, 102.0), 2.0),  # Hindwing Petal Vein 4
            ((-24.0, 62.0), (-88.0, 74.0), 2.0),   # Hindwing Petal Vein 5
            ((10.0, 24.0), (-72.0, 44.0), 2.0),    # Hindwing Anal Vein
        ]
        for (x1, y1), (x2, y2), w_vein in vein_segments:
            mid_x = (x1 + x2) / 2.0
            mid_y = (y1 + y2) / 2.0
            dx = x2 - x1
            dy = y2 - y1
            length = (dx * dx + dy * dy) ** 0.5 + w_vein * 0.5
            deg = math.degrees(math.atan2(dy, dx))
            with Locations(Location((mid_x, mid_y, 2.0), (0, 0, deg))):
                Box(length, w_vein, 1.20, mode=Mode.ADD)

        # Decorative Swallowtail Eye-Spot Medallion at tip of tail (-154, 106) matching yellow dot in image
        with Locations(Location((-153.0, 106.5, 2.0))):
            Cylinder(radius=4.2, height=1.20, mode=Mode.ADD)

        # 4. 4x WS2812B Mini LED Node Bosses & Sockets scaled across the 2x Larger Wing
        led_coords = [(54.0, 92.0), (86.0, 175.0), (36.0, 135.0), (-52.0, 105.0)]
        for x_led, y_led in led_coords:
            with Locations(Location((x_led, y_led, 2.0))):
                Cylinder(radius=5.8, height=1.20, mode=Mode.ADD)
            with Locations(Location((x_led, y_led, 2.35))):
                Cylinder(radius=4.75, height=0.60, mode=Mode.SUBTRACT)

        # 5. Wire routing channels on bottom of structural veins (Z = 1.40..1.75)
        wire_routes = [
            ((15.0, 24.0), (54.0, 92.0)),
            ((54.0, 92.0), (86.0, 175.0)),
            ((54.0, 92.0), (36.0, 135.0)),
            ((10.0, 24.0), (-24.0, 62.0)),
            ((-24.0, 62.0), (-52.0, 105.0)),
        ]
        for (x1, y1), (x2, y2) in wire_routes:
            mid_x = (x1 + x2) / 2.0
            mid_y = (y1 + y2) / 2.0
            dx = x2 - x1
            dy = y2 - y1
            length = (dx * dx + dy * dy) ** 0.5
            deg = math.degrees(math.atan2(dy, dx))
            with Locations(Location((mid_x, mid_y, 1.55), (0, 0, deg))):
                Box(length, 0.9, 0.40, mode=Mode.SUBTRACT)

        # 6. Wing Root Clevis & Coaxial Forward Support Hinge Knuckle around pivot (8.0, 9.0, 2.0)
        with Locations(Location((8.0, 9.0, 2.0))):
            with Locations(Location((4.15, 0, 0))):
                Cylinder(radius=4.5, height=7.8, rotation=(0, 90, 0), mode=Mode.ADD)
            with Locations(Location((3.75, 9.75, 0))):
                Box(7.0, 19.5, 9.0, mode=Mode.ADD)
            with Locations(Location((2.65, 0, 0))):
                Cylinder(radius=4.25, height=5.8, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations(Location((4.30, 7.30, 0))):
                Box(2.50, 23.20, 8.50, mode=Mode.SUBTRACT)
                with Locations(Location((0, 1.0, 0)), Location((0, 7.0, 0))):
                    Cylinder(radius=0.85, height=11.0, mode=Mode.SUBTRACT)
            with Locations(Location((4.0, 0, 0))):
                Cylinder(radius=1.50, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations(Location((6.50, 6.0, 0))):
                Box(1.50, 4.5, 3.8, mode=Mode.SUBTRACT)

    return wing.part

def build_right_wing(left_wing_solid):
    """
    Right Wing (ปีกขวา):
    สร้างจากการ Mirror ชิ้นส่วน Left Wing ข้าม Plane.XZ เพื่อให้สมมาตรกัน 100%
    """
    return mirror(left_wing_solid, about=Plane.XZ)

def build_butterfly_legs():
    """
    Biomimetic Butterfly Legs (ชุดขาผีเสื้อจริง 6 ขา แป้นฐานฝังราบสนิท 100% กับผิวท้อง Z = -19.8 mm):
    - แป้นยึดโคนขา (Coplanar Flat Sternum Plate, Z = [-19.8, -17.2]) ฝังจมอยู่ในเบ้าใต้ส่วนอก
      โดยผิวล่างสุดของแป้นอยู่ที่ Z = -19.8 mm ราบสนิทเป็นระนาบเดียวกับท้องผีเสื้อ (ไม่มีปุ่มหรือสันนูนยื่นออกมา)
    - ขาผีเสื้อเรียวเล็กทั้ง 6 ขางอกออกจากระดับผิวท้องราบ Z = -19.8 mm พับต้นขาแนบลำตัวลงสู่ระดับพื้น Z = -38.0 mm
    """
    with BuildPart() as legs_part:
        # 1. Coplanar Flat Sternum Plate recessed flush inside body's ventral pocket (Bottom face at Z = -19.8 mm!)
        with Locations(Location((-6.0, 0.0, -18.5))):
            Box(22.0, 5.8, 2.6, mode=Mode.ADD)
        # Dorsal Mating Peg engaging body's ventral socket at X=-8.0, Y=0 (Z=[-17.2, -13.9])
        with Locations(Location((-8.0, 0.0, -15.55))):
            Cylinder(radius=2.25, height=3.3, mode=Mode.ADD)

        # 3 Pairs of Tucked, Natural-Posture Butterfly Legs emerging from the flat Z = -19.8 mm belly
        leg_kinematics = [
            # Pair 1: Prothoracic Forelegs (ขาคู่หน้า)
            (
                (3.8, 2.0, -20.4),      # Coxa origin fused to bottom of flat sternum plate (Z=-19.8)
                (5.2, 6.5, -21.8),      # Trochanter joint below flat belly
                (13.0, 9.5, -21.2),     # Femur folded forward parallel below flat belly plane
                (19.5, 13.0, -35.8),    # Slender Tibia descending forward to Ankle
                (25.5, 14.5, -37.4),    # Horizontal Tarsus extending forward
                (28.0, 15.4, -38.0),    # Outer Tarsal Claw tip (Z = -38.0)
                (27.8, 13.6, -38.0),    # Inner Tarsal Claw tip (Z = -38.0)
            ),
            # Pair 2: Mesothoracic Midlegs (ขาคู่กลาง)
            (
                (-7.2, 2.0, -20.4),     # Coxa origin fused to bottom of flat mid sternum plate
                (-8.2, 7.8, -21.8),     # Trochanter joint below flat belly
                (-9.0, 12.8, -21.2),    # Femur tucked parallel below flat belly plane
                (-11.5, 17.5, -35.8),   # Slender Tibia descending to Ankle
                (-9.5, 20.0, -37.4),    # Horizontal Tarsus
                (-8.0, 21.2, -38.0),    # Anterior Tarsal Claw tip (Z = -38.0)
                (-10.8, 21.0, -38.0),   # Posterior Tarsal Claw tip (Z = -38.0)
            ),
            # Pair 3: Metathoracic Hindlegs (ขาคู่หลัง)
            (
                (-15.0, 2.0, -20.4),    # Coxa origin fused to bottom of flat rear sternum plate
                (-17.5, 7.2, -21.8),    # Trochanter joint below flat belly
                (-23.0, 12.3, -21.2),   # Femur tucked alongside anterior abdomen
                (-31.0, 15.5, -35.8),   # Slender Tibia descending backward to Ankle
                (-37.0, 17.0, -37.4),   # Horizontal Tarsus extending backward
                (-39.6, 18.0, -38.0),   # Outer Tarsal Claw tip (Z = -38.0)
                (-39.4, 16.0, -38.0),   # Inner Tarsal Claw tip (Z = -38.0)
            ),
        ]

        for sgn in [1.0, -1.0]:
            for (p_coxa, p_troch, p_knee, p_ankle, p_tarsus, p_claw1, p_claw2) in leg_kinematics:
                c_pt = (p_coxa[0], sgn * p_coxa[1], p_coxa[2])
                tr_pt = (p_troch[0], sgn * p_troch[1], p_troch[2])
                k_pt = (p_knee[0], sgn * p_knee[1], p_knee[2])
                a_pt = (p_ankle[0], sgn * p_ankle[1], p_ankle[2])
                ta_pt = (p_tarsus[0], sgn * p_tarsus[1], p_tarsus[2])
                cl1_pt = (p_claw1[0], sgn * p_claw1[1], p_claw1[2])
                cl2_pt = (p_claw2[0], sgn * p_claw2[1], p_claw2[2])

                _add_tapered_segment(c_pt, tr_pt, 1.00, 1.05, add_start_sphere=True, add_end_sphere=True)
                _add_tapered_segment(tr_pt, k_pt, 1.05, 1.00, add_start_sphere=False, add_end_sphere=True)
                _add_tapered_segment(k_pt, a_pt, 0.98, 0.72, add_start_sphere=False, add_end_sphere=True)

                spur_base = (
                    k_pt[0] * 0.30 + a_pt[0] * 0.70,
                    k_pt[1] * 0.30 + a_pt[1] * 0.70,
                    k_pt[2] * 0.30 + a_pt[2] * 0.70,
                )
                spur_tip = (
                    spur_base[0] - 1.0,
                    spur_base[1] - sgn * 1.2,
                    spur_base[2] - 2.4,
                )
                _add_tapered_segment(spur_base, spur_tip, 0.45, 0.20, add_start_sphere=False, add_end_sphere=False)

                _add_tapered_segment(a_pt, ta_pt, 0.70, 0.56, add_start_sphere=False, add_end_sphere=True)
                _add_tapered_segment(ta_pt, cl1_pt, 0.52, 0.25, add_start_sphere=False, add_end_sphere=True)
                _add_tapered_segment(ta_pt, cl2_pt, 0.52, 0.25, add_start_sphere=False, add_end_sphere=True)

    return legs_part.part

build_base_stand = build_butterfly_legs

def build_full_assembly(body, left_wing, right_wing, legs, servo_norm, horn_norm):
    """
    ประกอบชิ้นส่วนที่สร้างขึ้นทั้ง 4 ชิ้น (Body, Left Wing, Right Wing, Butterfly Legs)
    เข้ากับชิ้นส่วน External 4 ชิ้น (2x MG90S Servos, 2x MG90S Servo Horns) เป็นหุ่นยนต์ผีเสื้อสมบูรณ์
    """
    s_aligned = servo_norm.moved(Location((0, 0, 0), (0, 90, 90)))
    servo_left = s_aligned.moved(Location((8.0, 9.0, 2.0)))
    servo_right = s_aligned.moved(Location((8.0, -9.0, 2.0)))

    horn_left = horn_norm.moved(Location((0, 0, 0), (0, 90, 90)))\
                         .moved(Location((8.0, 9.0, 2.0)))

    horn_right = horn_norm.moved(Location((0, 0, 0), (0, 90, -90)))\
                          .moved(Location((8.0, -9.0, 2.0)))

    full_compound = Compound([
        body,
        servo_left,
        servo_right,
        horn_left,
        horn_right,
        left_wing,
        right_wing,
        legs
    ])

    return full_compound, {
        "body": body,
        "servo_left": servo_left,
        "servo_right": servo_right,
        "horn_left": horn_left,
        "horn_right": horn_right,
        "wing_left": left_wing,
        "wing_right": right_wing,
        "butterfly_legs": legs
    }

def main():
    GENERATED_CAD_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("🦋 ELECTRONIC BUTTERFLY — 3D CHASSIS CAD GENERATOR (build123d)")
    print(" • Wing Profile: Reference Swallowtail Butterfly (464mm Span, 1.2mm Thin)")
    print(" • Belly & Legs: 100% Flat Coplanar Ventral Belly Plane (Z = -19.8 mm)")
    print("=" * 72)

    servo_norm = load_external_mg90s_servo(EXTERNAL_CAD_DIR)
    horn_norm = load_external_mg90s_horn(EXTERNAL_CAD_DIR)

    body = build_body()
    assert len(body.solids()) == 1, f"Body must be 1 unified solid, got {len(body.solids())}"
    export_stl(body, str(GENERATED_CAD_DIR / "body.stl"))

    left_wing = build_left_wing()
    assert len(left_wing.solids()) == 1, f"Left wing must be 1 unified solid, got {len(left_wing.solids())}"
    right_wing = build_right_wing(left_wing)
    assert len(right_wing.solids()) == 1, f"Right wing must be 1 unified solid, got {len(right_wing.solids())}"
    export_stl(left_wing, str(GENERATED_CAD_DIR / "left_wing.stl"))
    export_stl(right_wing, str(GENERATED_CAD_DIR / "right_wing.stl"))

    legs = build_butterfly_legs()
    assert len(legs.solids()) == 1, f"Butterfly legs must be 1 unified solid, got {len(legs.solids())}"
    export_stl(legs, str(GENERATED_CAD_DIR / "butterfly_legs.stl"))

    full_assembly, _ = build_full_assembly(body, left_wing, right_wing, legs, servo_norm, horn_norm)
    export_stl(full_assembly, str(GENERATED_CAD_DIR / "butterfly_full_assembly.stl"))
    export_step(full_assembly, str(GENERATED_CAD_DIR / "butterfly_full_assembly.step"))
    print("🎉 All custom .STL parts and full assembly (.STL + .STEP) generated!")

if __name__ == "__main__":
    main()
