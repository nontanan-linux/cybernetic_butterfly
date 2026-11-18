#!/usr/bin/env python3
"""
Procedural Butterfly Wing Venation Generator
Generates organic PCB Art SVG layers for the Cybernetic Butterfly wings:
- Edge.Cuts (Board Outline)
- F.Cu / B.Cu (Copper Veins & Signal Traces)
- F.Mask (Soldermask Windows for Translucent FR4 Light Diffusion)
- F.SilkS (Artistic White Silkscreen Filigree)
- Component Footprints (8x WS2812B LEDs, Hinge Mounts, Solder Pads)
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
    # Parametric equations modeling Lepidoptera wing aerodynamics
    # Base radius modulation
    r = (
        80.0
        + 42.0 * np.sin(t)
        - 28.0 * np.sin(2 * t)
        + 18.0 * np.cos(3 * t)
        - 12.0 * np.sin(4 * t)
    )
    
    # Primary transformation
    x = r * np.cos(t) * 1.3
    y = r * np.sin(t) * 1.6
    
    # Shape warping to form anatomical forewing tip (apex) and anal lobe
    # Shift origin to wing root hinge
    x_warped = x + 35.0
    y_warped = y - 40.0
    
    # Wing root cutoff / hinge bracket clamping tab
    pts = []
    for xi, yi in zip(x_warped, y_warped):
        if xi < 15.0:
            # Clamping tab region near hinge
            xi = 15.0
            yi = np.clip(yi, -25.0, 25.0)
        pts.append((float(xi * scale), float(yi * scale)))
    
    # Ensure closed loop
    pts.append(pts[0])
    
    if is_right:
        pts = [(-x, y) for x, y in pts]
    return pts

def create_wing_pcb_svg(output_path, is_right=False):
    """
    Creates full multi-layer PCB art SVG for a butterfly wing.
    """
    width = 450
    height = 550
    dwg = svgwrite.Drawing(output_path, size=(f"{width}px", f"{height}px"), viewBox=f"0 0 {width} {height}")
    
    # Modern dark preview background
    dwg.add(dwg.rect((0, 0), (width, height), fill="#0d1117"))
    
    # Coordinate center offset
    cx = 80 if not is_right else width - 80
    cy = 280
    sgn = 1.0 if not is_right else -1.0
    
    # Colors mimicking PCB fab preview
    COLOR_FR4 = "#182026"       # Dark FR4 core
    COLOR_MASK = "#0d402b"      # Matte Forest Green / Emerald Soldermask (or Purple/Black)
    COLOR_COPPER = "#d97706"    # Warm Copper / ENIG Gold
    COLOR_SILK = "#f8fafc"      # Crisp White Silkscreen
    COLOR_LED = "#10b981"       # NeoPixel glowing emitter
    COLOR_PAD = "#f59e0b"       # Gold immersion pad
    
    # 1. Edge.Cuts (Board Outline)
    # Wing outer contour points
    t_vals = np.linspace(0, 1, 120)
    # Forewing apex and outer curve
    wing_points = []
    
    # Hinge Root (Tab for 3D printed mechanical clamp)
    root_x, root_y = cx, cy
    wing_points.append((root_x, root_y - 25))
    wing_points.append((root_x + sgn * 30, root_y - 30))
    # Forewing Leading Edge (Costa)
    wing_points.append((root_x + sgn * 120, root_y - 120))
    wing_points.append((root_x + sgn * 220, root_y - 200)) # Apex
    wing_points.append((root_x + sgn * 260, root_y - 190)) # Apex tip
    # Outer Margin (Termen) with gentle scalloping
    wing_points.append((root_x + sgn * 240, root_y - 100))
    wing_points.append((root_x + sgn * 210, root_y - 20))
    # Tornus / Hindwing Junction
    wing_points.append((root_x + sgn * 180, root_y + 40))
    # Hindwing Outer Margin
    wing_points.append((root_x + sgn * 190, root_y + 110))
    wing_points.append((root_x + sgn * 160, root_y + 170))
    wing_points.append((root_x + sgn * 110, root_y + 200)) # Anal angle
    # Inner Margin (Dorsum) leading back to root
    wing_points.append((root_x + sgn * 50, root_y + 130))
    wing_points.append((root_x + sgn * 25, root_y + 50))
    wing_points.append((root_x, root_y + 25))
    
    # PCB Substrate Body
    poly_path = "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in wing_points) + " Z"
    dwg.add(dwg.path(d=poly_path, fill=COLOR_MASK, stroke="#059669", stroke_width=2))
    
    # 2. Translucent Soldermask Windows (FR4 Light Cells)
    # Internal cells that have no copper and no soldermask, allowing backlight diffusion
    cell_centers = [
        (root_x + sgn * 90, root_y - 80, 22, 14, 25),
        (root_x + sgn * 160, root_y - 130, 28, 16, 35),
        (root_x + sgn * 200, root_y - 160, 24, 14, 40),
        (root_x + sgn * 170, root_y - 70, 26, 15, 15),
        (root_x + sgn * 140, root_y - 20, 24, 16, 0),
        (root_x + sgn * 140, root_y + 60, 22, 18, -20),
        (root_x + sgn * 120, root_y + 120, 24, 18, -40),
        (root_x + sgn * 70, root_y + 70, 20, 15, -15),
    ]
    
    for (ccx, ccy, rx, ry, rot) in cell_centers:
        # Subtle glowing translucent FR4 cell
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
    # Primary veins radiating from wing base (Root) to margins
    vein_endpoints = [
        (root_x + sgn * 250, root_y - 190), # Subcostal / Radial to apex
        (root_x + sgn * 240, root_y - 100), # Radial Sector R3-R5
        (root_x + sgn * 210, root_y - 20),  # Medial M1-M3
        (root_x + sgn * 180, root_y + 40),  # Cubital CuA1
        (root_x + sgn * 190, root_y + 110), # Hindwing Radial
        (root_x + sgn * 160, root_y + 170), # Hindwing Medial
        (root_x + sgn * 110, root_y + 200), # Anal vein 2A
    ]
    
    for ep in vein_endpoints:
        # Branching curved primary vein
        ctrl_x = (root_x + ep[0]) / 2 + sgn * 15
        ctrl_y = (root_y + ep[1]) / 2 - 10
        dwg.add(dwg.path(
            d=f"M {root_x + sgn*10},{root_y} Q {ctrl_x:.1f},{ctrl_y:.1f} {ep[0]:.1f},{ep[1]:.1f}",
            fill="none",
            stroke=COLOR_COPPER,
            stroke_width=3,
            stroke_linecap="round"
        ))
        
        # Secondary finer venation branches
        b1_x = (ctrl_x + ep[0]) / 2 + sgn * 10
        b1_y = (ctrl_y + ep[1]) / 2 + 15
        dwg.add(dwg.line(
            start=(ctrl_x, ctrl_y),
            end=(b1_x, b1_y),
            stroke=COLOR_COPPER,
            stroke_width=1.5,
            stroke_linecap="round"
        ))
    
    # 4. WS2812B-2020 SMD LED Positions (8 per wing)
    led_positions = [
        (root_x + sgn * 60, root_y - 45, "LED1"),
        (root_x + sgn * 125, root_y - 95, "LED2"),
        (root_x + sgn * 185, root_y - 145, "LED3"),
        (root_x + sgn * 220, root_y - 180, "LED4 (Apex)"),
        (root_x + sgn * 190, root_y - 50, "LED5"),
        (root_x + sgn * 165, root_y + 20, "LED6"),
        (root_x + sgn * 145, root_y + 90, "LED7"),
        (root_x + sgn * 100, root_y + 150, "LED8 (Tornus)")
    ]
    
    # Daisy-chain signal trace connecting LEDs
    trace_pts = [(root_x + sgn * 12, root_y - 12)] + [(pos[0], pos[1]) for pos in led_positions]
    for i in range(len(trace_pts) - 1):
        p1, p2 = trace_pts[i], trace_pts[i+1]
        mid_x = (p1[0] + p2[0]) / 2
        dwg.add(dwg.path(
            d=f"M {p1[0]},{p1[1]} Q {mid_x},{p1[1]} {p2[0]},{p2[1]}",
            fill="none",
            stroke="#34d399",
            stroke_width=1.5,
            stroke_dasharray="4,2"
        ))
    
    for lx, ly, label in led_positions:
        # SMD 2020 LED Package Body
        dwg.add(dwg.rect((lx - 7, ly - 7), (14, 14), fill="#1f2937", stroke="#4ade80", stroke_width=1.2, rx=2))
        # 4 Solder Pads
        dwg.add(dwg.rect((lx - 6, ly - 6), (3, 3), fill=COLOR_PAD))
        dwg.add(dwg.rect((lx + 3, ly - 6), (3, 3), fill=COLOR_PAD))
        dwg.add(dwg.rect((lx - 6, ly + 3), (3, 3), fill=COLOR_PAD))
        dwg.add(dwg.rect((lx + 3, ly + 3), (3, 3), fill=COLOR_PAD))
        # Central Emitter Core (Glowing)
        dwg.add(dwg.circle(center=(lx, ly), r=3.5, fill=COLOR_LED))
        # Label in silkscreen
        dwg.add(dwg.text(label, insert=(lx + sgn * 10, ly + 4), fill=COLOR_SILK, font_size=8, font_family="monospace"))
    
    # 5. Silkscreen Filigree & Margin Scales (F.SilkS)
    # Wing margin decorative crescents (mimicking monarch white spots)
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
    
    # 6. Mechanical Hinge Root Tab & Solder Terminals
    # Mounting Holes for 1.6mm / M1.6 hinge axle
    dwg.add(dwg.circle(center=(root_x + sgn * 12, root_y - 18), r=3.5, fill="#0d1117", stroke="#cbd5e1", stroke_width=1.5))
    dwg.add(dwg.circle(center=(root_x + sgn * 12, root_y + 18), r=3.5, fill="#0d1117", stroke="#cbd5e1", stroke_width=1.5))
    dwg.add(dwg.text("M1.6 Hinge", insert=(root_x + sgn * 22, root_y - 15), fill="#94a3b8", font_size=7, font_family="monospace"))

    # Solder Pads for 4-pin Flexible Wire Harness: VDD(5V), GND, DIN, DOUT
    pads = [("5V", -8), ("GND", -2), ("DIN", 4), ("DOUT", 10)]
    for pad_name, offset_y in pads:
        py = root_y + offset_y
        px = root_x + sgn * 12
        dwg.add(dwg.rect((px - 3, py - 2), (6, 4), fill=COLOR_PAD, stroke="#b45309", stroke_width=0.5))
        dwg.add(dwg.text(pad_name, insert=(px + sgn * 8, py + 2), fill=COLOR_SILK, font_size=7, font_family="monospace"))

    # Watermark / Attribution
    wing_label = "LEFT WING (F.Cu / ENIG)" if not is_right else "RIGHT WING (F.Cu / ENIG)"
    dwg.add(dwg.text(f"CYBER-BUTTERFLY :: {wing_label}", insert=(20, 30), fill="#64ffda", font_size=13, font_weight="bold", font_family="sans-serif"))
    dwg.add(dwg.text("FR4 0.8mm | Matte Soldermask | ENIG Gold | 8x WS2812B-2020", insert=(20, 48), fill="#94a3b8", font_size=10, font_family="sans-serif"))

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
