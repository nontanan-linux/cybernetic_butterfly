# PCB Art Layer Stack & Fabrication Guide — Electronic Butterfly

This guide provides technical fabrication settings and ordering instructions for manufacturing the PCB Art butterfly wings with commercial PCB fabricators (e.g., JLCPCB, PCBWay, OSH Park).

---

## 1. PCB Specifications for Lightweight Flapping Wings

A typical 1.6mm standard PCB is too heavy for micro-servo flapping, causing excessive gear train strain and slow response. The following specifications ensure optimal strength-to-weight ratio:

| Fabrication Parameter | Recommended Value | Engineering Rationale |
| :--- | :--- | :--- |
| **Board Thickness** | **0.8 mm** (or 0.6 mm FPC / semi-rigid) | Keeps total wing mass $< 3.8\text{ g}$ per wing for high-agility flapping |
| **Layer Count** | **2 Layers** (Top: F.Cu, Bottom: B.Cu) | Standard single-core FR4 |
| **Copper Weight** | **1 oz** ($35\mu\text{m}$) | Low resistance for daisy-chained WS2812B supply rails |
| **Surface Finish** | **ENIG** (Electroless Nickel Immersion Gold) | Provides lustrous gold aesthetic on exposed copper wing veins |
| **Soldermask Color** | **Matte Black**, **Midnight Purple**, or **Emerald Green** | High contrast against ENIG gold veins and bright white silkscreen |
| **Silkscreen Color** | **Crisp White** | Delicate scales, margin crescents, and component designators |
| **Min Trace / Space** | $6\text{ mil} / 6\text{ mil}$ ($0.15\text{mm}$) | Allows intricate sub-vein detailing |
| **Edge Clearance** | $0.3\text{mm}$ from board outline | Clean CNC milling along organic wing perimeter |

---

## 2. Multi-Layer Visual Art Techniques

### A. Translucent Stained-Glass Window Effect
In natural Lepidoptera wings (such as the Glasswing butterfly *Greta oto*), sections of the wing membrane are transparent. We recreate this in FR4 PCB art:
1. **Remove Copper:** Ensure no copper fills on both **F.Cu (Top)** and **B.Cu (Bottom)** in the target window.
2. **Remove Soldermask:** Place soldermask apertures on both **F.Mask** and **B.Mask**.
3. **The Result:** The raw, unmasked FR4 fiberglass core ($0.8\text{mm}$) becomes semi-translucent. When the adjacent WS2812B LEDs fire, light diffuses through the fiberglass, creating an ambient glowing stained-glass aesthetic.

### B. Dual-Tone Vein Contrast
By utilizing the interplay between layers:
- **Tone 1 (Bright Gold):** Exposed Copper + ENIG finish (Soldermask removed).
- **Tone 2 (Deep Shimmering Emerald/Purple):** Copper under soldermask.
- **Tone 3 (Deep Matte Background):** No copper under soldermask.
- **Tone 4 (Crisp White Filigree):** Silkscreen over soldermask.

---

## 3. Mechanical Hinge Mounts & Wiring Connection

### Hinge Root Interface:
- Two **$\varnothing 1.6\text{mm}$ unplated mounting holes** are routed at the root tab of each wing.
- These mount directly into the 3D printed hinge clamps (`wing_hinge_left.stl` and `wing_hinge_right.stl`) using M1.6 machine screws or stainless steel pivot pins.

### Wiring Interconnect:
- 4 large gold solder pads are situated at the wing root:
  - **5V / VDD:** Power rail for 8x WS2812B LEDs
  - **GND:** Return line
  - **DIN:** Data In (connects to ESP32 GPIO8 via thorax harness)
  - **DOUT:** Data Out (daisy-chains across to right wing)
- Use **30 AWG ultra-flexible silicone stranded wire**. Standard rigid solid-core wire will fatigue and break during wing flapping cycles.
