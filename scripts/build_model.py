#!/usr/bin/env python3
"""
Electronic Butterfly — Master Asset & Model Build Script
========================================================
1. Reads External Hardware CAD from cad/external/ (Read-Only, never modified or overwritten)
2. Generates Custom 3D-Printed Parts in cad/models/ (.STL ONLY: body.stl, left_wing.stl, right_wing.stl, butterfly_legs.stl)
3. Generates Full Robotic Assembly in cad/models/ (BOTH .STL and .STEP: butterfly_full_assembly.stl & .step)
4. Generates PCB Art Vector Artwork in hardware/pcb_art/ (wings_monarch_left.svg & wings_monarch_right.svg)
5. Synchronizes Unified Configurations across C++, MicroPython, and Web Simulator
"""

import argparse
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

def build_cad_models(verbose=False):
    """Executes build123d CAD generation adhering strictly to external vs generated rules."""
    print("\n📦 [1/3] Building 3D Mechanical CAD Models (build123d)...")
    from scripts.generate_butterfly_chassis import (
        EXTERNAL_CAD_DIR,
        GENERATED_CAD_DIR,
        load_external_mg90s_servo,
        load_external_mg90s_horn,
        build_body,
        build_left_wing,
        build_right_wing,
        build_butterfly_legs,
        build_full_assembly,
    )
    from build123d import export_stl, export_step

    GENERATED_CAD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Read-Only External Hardware Models (Never overwritten)
    servo_solid = load_external_mg90s_servo(EXTERNAL_CAD_DIR)
    horn_solid = load_external_mg90s_horn(EXTERNAL_CAD_DIR)
    print(f"   🔒 External CAD (Read-Only): {EXTERNAL_CAD_DIR}")

    # 2. Custom Generated Parts (.STL ONLY)
    body_solid = build_body()
    left_wing_solid = build_left_wing()
    right_wing_solid = build_right_wing(left_wing_solid)
    legs_solid = build_butterfly_legs()

    generated_parts = [
        ("body", body_solid),
        ("left_wing", left_wing_solid),
        ("right_wing", right_wing_solid),
        ("butterfly_legs", legs_solid),
    ]

    for name, solid in generated_parts:
        stl_path = GENERATED_CAD_DIR / f"{name}.stl"
        export_stl(solid, str(stl_path))
        stl_size = stl_path.stat().st_size / 1024
        print(f"   ✓ {name:<24} [Generated Part]     -> STL: {stl_size:>7.1f} KB (.STL Only)")

    # 3. Full Robotic Assembly (BOTH .STL and .STEP)
    full_assembly_solid, _ = build_full_assembly(
        body_solid, left_wing_solid, right_wing_solid, legs_solid, servo_solid, horn_solid
    )
    asm_stl = GENERATED_CAD_DIR / "butterfly_full_assembly.stl"
    asm_step = GENERATED_CAD_DIR / "butterfly_full_assembly.step"
    export_stl(full_assembly_solid, str(asm_stl))
    export_step(full_assembly_solid, str(asm_step))
    print(
        f"   ✓ {'butterfly_full_assembly':<24} [Full Assembly]      -> "
        f"STL: {asm_stl.stat().st_size / 1024:>7.1f} KB | STEP: {asm_step.stat().st_size / 1024:>7.1f} KB"
    )
    print(f"   📁 Generated Output Directory: {GENERATED_CAD_DIR}")

def build_pcb_art(verbose=False):
    """Executes procedural wing venation and PCB layer generation."""
    print("\n🎨 [2/3] Generating Procedural PCB Art Wings (SVG)...")
    from scripts.procedural_wing_venation import create_wing_pcb_svg

    pcb_dir = PROJECT_DIR / "hardware" / "pcb_art"
    pcb_dir.mkdir(parents=True, exist_ok=True)

    left_svg = pcb_dir / "wings_monarch_left.svg"
    right_svg = pcb_dir / "wings_monarch_right.svg"

    create_wing_pcb_svg(str(left_svg), is_right=False)
    create_wing_pcb_svg(str(right_svg), is_right=True)

    print(f"   ✓ wings_monarch_left.svg   -> {left_svg.stat().st_size / 1024:>6.1f} KB")
    print(f"   ✓ wings_monarch_right.svg  -> {right_svg.stat().st_size / 1024:>6.1f} KB")
    print(f"   📁 Output Directory: {pcb_dir}")

def sync_project_config():
    """Synchronizes parameter definitions across C++, Python & Web."""
    print("\n🔄 [3/3] Synchronizing Unified Configurations...")
    from scripts.sync_config import main as run_sync
    run_sync()

def clean_artifacts():
    """Removes generated build artifacts in cad/models/ and hardware/pcb_art/ (never touches cad/external/)."""
    print("🧹 Cleaning generated build artifacts (preserving cad/external/)...")
    models_dir = PROJECT_DIR / "cad" / "models"
    pcb_dir = PROJECT_DIR / "hardware" / "pcb_art"

    for p in models_dir.glob("*.*"):
        if p.is_file() and p.suffix in [".stl", ".step"]:
            p.unlink()
            print(f"   Deleted {p.name}")
    for p in pcb_dir.glob("*.svg"):
        p.unlink()
        print(f"   Deleted {p.name}")

def main():
    parser = argparse.ArgumentParser(description="Electronic Butterfly Asset & Model Builder")
    parser.add_argument("--cad-only", action="store_true", help="Generate only 3D CAD models")
    parser.add_argument("--pcb-only", action="store_true", help="Generate only PCB Art SVG vector layers")
    parser.add_argument("--sync-only", action="store_true", help="Synchronize configuration only")
    parser.add_argument("--clean", action="store_true", help="Clean generated artifacts before build")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    start_time = time.time()
    print("=" * 70)
    print("🦋 ELECTRONIC BUTTERFLY — ASSET BUILD SYSTEM")
    print("=" * 70)

    if args.clean:
        clean_artifacts()

    if args.sync_only:
        sync_project_config()
    elif args.cad_only:
        build_cad_models(args.verbose)
    elif args.pcb_only:
        build_pcb_art(args.verbose)
    else:
        build_cad_models(args.verbose)
        build_pcb_art(args.verbose)
        sync_project_config()

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✨ All build tasks completed successfully in {elapsed:.2f} seconds!")
    print("=" * 70)

if __name__ == "__main__":
    main()
