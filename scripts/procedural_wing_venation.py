#!/usr/bin/env python3
"""
Procedural Butterfly Wing Venation Generator
Generates organic PCB Art SVG layers for the Cybernetic Butterfly wings:
- Edge.Cuts (Board Outline matching 3D CAD Wing Contour & Root Clevis)
- F.Cu / B.Cu (Copper Veins & Signal Traces)
- F.Mask (Soldermask Windows for Translucent FR4 Light Diffusion)
- F.SilkS (Artistic White Silkscreen Filigree)
- Component Footprints (4x WS2812B Mini LEDs per wing, Direct-Drive Horn Clevis, 3-Pin Harness Pads)
"""

import math
import os
import numpy as np
import svgwrite

def generate_wing_contour(scale=1.0, is_right=False):
    """
    Parametric butterfly forewing and hindwing contour using blended Fourier harmonics.
    Returns list of (x, y) coordinates.
    """
    t = np.linspace(0, 2 * np.pi, 240)
    r = (
        80.0
        + 42.0 * np.sin(t)
        - 28.0 * np.sin(2 * t)
        + 18.0 * np.cos(3 * t)
        - 12.0 * np.sin(4 * t)
    )

    x = r * np.cos(t) * 1.3
    y = r * np.sin(t) * 1.6

    x_warped = x + 35.0
    y_warped = y - 40.0

    pts = []
    for xi, yi in zip(x_warped, y_warped):
        if xi < 15.0:
            xi = 15.0
            yi = np.clip(yi, -25.0, 25.0)
        pts.append((float(xi * scale), float(yi * scale)))

    pts.append(pts[0])

    if is_right:
        pts = [(-x, y) for x, y in pts]
    return pts

def create_wing_pcb_svg(output_path, is_right=False):
    """
    Creates full multi-layer PCB art SVG for a butterfly wing aligned with the 3D CAD specification:
    - 4x WS2812B Mini PCB LEDs per wing (8 LEDs total across left & right wings)
    - Direct-Drive MG90S Servo Horn Clevis & Coaxial Forward Support Hinge
    - 3-Wire Spring-Coiled Enamel Interconnect (5V, GND, DIN) on Neutral Rotation Axis
    """
    width = 450
    height = 550
    dwg = svgwrite.Drawing(output_path, size=(f"{width}px", f"{height}px"), viewBox=f"0 0 {width} {height}")

    # Modern dark preview background
    dwg.add(dwg.rect((0, 0), (width, height), fill="#0d1117"))

    # Coordinate center offset (Wing Pivot Root)
    cx = 80 if not is_right else width - 80
    cy = 280
    sgn = 1.0 if not is_right else -1.0

    # Colors mimicking PCB fab preview
    COLOR_MASK = "#0d402b"      # Matte Emerald Green Soldermask
    COLOR_COPPER = "#d97706"    # Warm Copper / ENIG Gold
    COLOR_SILK = "#f8fafc"      # Crisp White Silkscreen
    COLOR_LED = "#10b981"       # WS2812B glowing emitter
    COLOR_PAD = "#f59e0b"       # Gold immersion pad

    # 1. Edge.Cuts (Board Outline matching lateral wing blade & clevis root)
    root_x, root_y = cx, cy
    wing_points = [
        (root_x, root_y - 25),
        (root_x + sgn * 35, root_y - 28),
        (root_x + sgn * 120, root_y - 120),
        (root_x + sgn * 220, root_y - 200),  # Forewing Apex
        (root_x + sgn * 260, root_y - 190),  # Apex tip
        (root_x + sgn * 240, root_y - 100),  # Outer Margin
        (root_x + sgn * 210, root_y - 20),
        (root_x + sgn * 180, root_y + 40),   # Hindwing Junction
        (root_x + sgn * 190, root_y + 110),
        (root_x + sgn * 160, root_y + 170),
        (root_x + sgn * 110, root_y + 200),  # Anal lobe
        (root_x + sgn * 55, root_y + 130),   # Inner margin (clears thorax/abdomen)
        (root_x + sgn * 38, root_y + 45),
        (root_x + sgn * 35, root_y + 22),
        (root_x, root_y + 22),
    ]

    poly_path = "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in wing_points) + " Z"
    dwg.add(dwg.path(d=poly_path, fill=COLOR_MASK, stroke="#059669", stroke_width=2))

    # 2. Translucent Soldermask Windows (FR4 Light Cells)
    cell_centers = [
        (root_x + sgn * 90, root_y - 80, 22, 14, 25),
        (root_x + sgn * 160, root_y - 130, 28, 16, 35),
        (root_x + sgn * 200, root_y - 160, 24, 14, 40),
        (root_x + sgn * 170, root_y - 70, 26, 15, 15),
        (root_x + sgn * 140, root_y - 20, 24, 16, 0),
        (root_x + sgn * 140, root_y + 60, 22, 18, -20),
        (root_x + sgn * 120, root_y + 120, 24, 18, -40),
        (root_x + sgn * 75, root_y + 70, 20, 15, -15),
    ]

    for (ccx, ccy, rx, ry, rot) in cell_centers:
        dwg.add(dwg.ellipse(
            center=(ccx, ccy),
            r=(rx, ry),
            fill="#1e3a2b",
            stroke="#10b981",
            stroke_width=1,
            stroke_dasharray="2,2",
            transform=f"rotate({rot * sgn}, {ccx}, {ccy})"
        ))

    # 3. Main Radial Veins (Copper Traces - F.Cu & ENIG)
    vein_endpoints = [
        (root_x + sgn * 250, root_y - 190),
        (root_x + sgn * 240, root_y - 100),
        (root_x + sgn * 210, root_y - 20),
        (root_x + sgn * 180, root_y + 40),
        (root_x + sgn * 190, root_y + 110),
        (root_x + sgn * 160, root_y + 170),
        (root_x + sgn * 110, root_y + 200),
    ]

    for ep in vein_endpoints:
        ctrl_x = (root_x + ep[0]) / 2 + sgn * 15
        ctrl_y = (root_y + ep[1]) / 2 - 10
        dwg.add(dwg.path(
            d=f"M {root_x + sgn*15},{root_y} Q {ctrl_x:.1f},{ctrl_y:.1f} {ep[0]:.1f},{ep[1]:.1f}",
            fill="none",
            stroke=COLOR_COPPER,
            stroke_width=3,
            stroke_linecap="round"
        ))

        b1_x = (ctrl_x + ep[0]) / 2 + sgn * 10
        b1_y = (ctrl_y + ep[1]) / 2 + 15
        dwg.add(dwg.line(
            start=(ctrl_x, ctrl_y),
            end=(b1_x, b1_y),
            stroke=COLOR_COPPER,
            stroke_width=1.5,
            stroke_linecap="round"
        ))

    # 4. 4x WS2812B Mini PCB LED Positions matching 3D CAD Wing Pockets:
    # CAD coordinates: (32, 36), (36, 68), (10, 60), (-15, 45)
    led_positions = [
        (root_x + sgn * 95,  root_y - 75,  "LED1 (Fore-Inner)"),
        (root_x + sgn * 190, root_y - 140, "LED2 (Fore-Apex)"),
        (root_x + sgn * 155, root_y - 20,  "LED3 (Mid-Cell)"),
        (root_x + sgn * 115, root_y + 95,  "LED4 (Hindwing)"),
    ]

    # 0.8mm Wire Routing Channels connecting 3-Pin Root to the 4 WS2812B LEDs
    wire_routes = [
        ((root_x + sgn * 25, root_y - 4), (led_positions[0][0], led_positions[0][1])),
        ((led_positions[0][0], led_positions[0][1]), (led_positions[1][0], led_positions[1][1])),
        ((led_positions[0][0], led_positions[0][1]), (led_positions[2][0], led_positions[2][1])),
        ((root_x + sgn * 25, root_y - 4), (led_positions[3][0], led_positions[3][1])),
    ]
    for p1, p2 in wire_routes:
        mid_x = (p1[0] + p2[0]) / 2
        dwg.add(dwg.path(
            d=f"M {p1[0]},{p1[1]} Q {mid_x},{p1[1]} {p2[0]},{p2[1]}",
            fill="none",
            stroke="#34d399",
            stroke_width=1.8,
            stroke_dasharray="4,2"
        ))

    for lx, ly, label in led_positions:
        # WS2812B Mini Round PCB Pocket (Dia 9.5mm)
        dwg.add(dwg.circle(center=(lx, ly), r=11, fill="#1f2937", stroke="#4ade80", stroke_width=1.5))
        # Solder Pads
        dwg.add(dwg.rect((lx - 7, ly - 5), (3.5, 3.5), fill=COLOR_PAD))
        dwg.add(dwg.rect((lx + 3.5, ly - 5), (3.5, 3.5), fill=COLOR_PAD))
        dwg.add(dwg.rect((lx - 7, ly + 1.5), (3.5, 3.5), fill=COLOR_PAD))
        dwg.add(dwg.rect((lx + 3.5, ly + 1.5), (3.5, 3.5), fill=COLOR_PAD))
        # Central Emitter Core (Glowing)
        dwg.add(dwg.circle(center=(lx, ly), r=4.5, fill=COLOR_LED))
        dwg.add(dwg.text(label, insert=(lx + sgn * 15, ly + 4), fill=COLOR_SILK, font_size=8, font_family="monospace"))

    # 5. Silkscreen Filigree & Margin Scales (F.SilkS)
    margin_spots = [
        (root_x + sgn * 248, root_y - 170),
        (root_x + sgn * 242, root_y - 135),
        (root_x + sgn * 232, root_y - 95),
        (root_x + sgn * 215, root_y - 50),
        (root_x + sgn * 195, root_y - 10),
        (root_x + sgn * 182, root_y + 30),
        (root_x + sgn * 185, root_y + 80),
        (root_x + sgn * 170, root_y + 130),
        (root_x + sgn * 135, root_y + 175),
        (root_x + sgn * 95, root_y + 190)
    ]
    for mx, my in margin_spots:
        dwg.add(dwg.circle(center=(mx, my), r=3, fill=COLOR_SILK))
        dwg.add(dwg.circle(center=(mx - sgn * 5, my), r=1.5, fill=COLOR_SILK))

    # 6. Direct-Drive MG90S Servo Horn Clevis & Coaxial Support Hinge Outline
    clevis_x = root_x if not is_right else root_x - 42
    dwg.add(dwg.rect((clevis_x, root_y - 20), (42, 14), fill="#0d1117", stroke="#38bdf8", stroke_width=1.5, rx=4))
    dwg.add(dwg.circle(center=(root_x + sgn * 6, root_y - 13), r=4.0, fill="#0d1117", stroke="#f8fafc", stroke_width=1.5))
    dwg.add(dwg.text("MG90S Horn Clevis + Coaxial Hinge", insert=(root_x + sgn * 8, root_y - 24), fill="#38bdf8", font_size=7.5, font_family="monospace"))

    # 3-Pin Spring-Coiled Enamel Wire Harness Pads: 5V, GND, DIN (via 330 ohm)
    pads = [("5V", -2), ("GND", 6), ("DIN", 14)]
    for pad_name, offset_y in pads:
        py = root_y + offset_y
        px = root_x + sgn * 14
        dwg.add(dwg.rect((px - 3, py - 2.5), (6, 5), fill=COLOR_PAD, stroke="#b45309", stroke_width=0.5))
        dwg.add(dwg.text(pad_name, insert=(px + sgn * 8, py + 2), fill=COLOR_SILK, font_size=7.5, font_family="monospace"))

    # Watermark / Attribution
    wing_label = "LEFT WING (F.Cu / ENIG)" if not is_right else "RIGHT WING (F.Cu / ENIG)"
    dwg.add(dwg.text(f"CYBER-BUTTERFLY :: {wing_label}", insert=(20, 30), fill="#64ffda", font_size=13, font_weight="bold", font_family="sans-serif"))
    dwg.add(dwg.text("1.8mm Wing Blade | Direct-Drive MG90S Clevis | 4x WS2812B Mini PCB LEDs", insert=(20, 48), fill="#94a3b8", font_size=10, font_family="sans-serif"))

    dwg.save()
    print(f"Generated PCB Art SVG: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(out_dir, "..", "hardware", "pcb_art")
    os.makedirs(target_dir, exist_ok=True)

    left_path = os.path.join(target_dir, "wings_monarch_left.svg")
    right_path = os.path.join(target_dir, "wings_monarch_right.svg")

    create_wing_pcb_svg(left_path, is_right=False)
    create_wing_pcb_svg(right_path, is_right=True)
