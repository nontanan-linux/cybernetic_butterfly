#!/usr/bin/env python3
"""
Electronic Butterfly — Model Build Script (3D CAD & PCB Art)
===========================================================
Generates and exports all physical and vector assets:
1. 3D Mechanical Solids (Thorax body, wing hinges, display perch stand) in STL & STEP AP242
2. PCB Art Vector Artwork (Left & Right monarch wing contours, veins, FR4 windows, LED footprints)
3. Synchronizes configuration across C++, MicroPython, and Web Simulator

Usage:
    python3 scripts/build_model.py                # Build everything
    python3 scripts/build_model.py --cad-only     # Build only 3D CAD models
    python3 scripts/build_model.py --pcb-only     # Build only PCB Art SVGs
    python3 scripts/build_model.py --clean        # Clean and rebuild fresh
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Auto-detect and switch to .venv interpreter if needed
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
VENV_PYTHON = WORKSPACE_ROOT / ".venv" / "bin" / "python3"
if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

def build_cad_models(verbose=False):
    """Executes build123d CAD generation for all mechanical components."""
    print("\n📦 [1/3] Building 3D Mechanical CAD Models (build123d)...")
    from scripts.generate_butterfly_chassis import (
        build_body,
        build_left_wing,
        build_right_wing,
        build_base_stand,
        build_base_stand_lid,
        build_mg90s_servo,
        build_mg90s_servo_horn,
        build_full_assembly
    )
    from build123d import export_stl, export_step

    models_dir = PROJECT_DIR / "cad" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    servo_solid = build_mg90s_servo()
    horn_solid = build_mg90s_servo_horn()
    body_solid = build_body()
    left_wing_solid = build_left_wing()
    right_wing_solid = build_right_wing(left_wing_solid)
    stand_solid = build_base_stand()
    lid_solid = build_base_stand_lid()
    full_assembly_solid, _ = build_full_assembly(
        body_solid, left_wing_solid, right_wing_solid, stand_solid, lid_solid, servo_solid, horn_solid
    )

    parts = [
        ("body", body_solid),
        ("left_wing", left_wing_solid),
        ("right_wing", right_wing_solid),
        ("base_stand", stand_solid),
        ("base_stand_lid", lid_solid),
        ("mg90s_servo", servo_solid),
        ("mg90s_servo_horn", horn_solid),
        ("butterfly_full_assembly", full_assembly_solid),
    ]

    for name, solid in parts:
        stl_path = models_dir / f"{name}.stl"
        step_path = models_dir / f"{name}.step"
        
        export_stl(solid, str(stl_path))
        export_step(solid, str(step_path))
        
        stl_size = stl_path.stat().st_size / 1024
        step_size = step_path.stat().st_size / 1024
        print(f"   ✓ {name:<22} -> STL: {stl_size:>6.1f} KB | STEP: {step_size:>6.1f} KB")

    print(f"   📁 Output Directory: {models_dir}")

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
    """Removes previous build artifacts before fresh build."""
    print("🧹 Cleaning previous build artifacts...")
    models_dir = PROJECT_DIR / "cad" / "models"
    pcb_dir = PROJECT_DIR / "hardware" / "pcb_art"

    for p in models_dir.glob("*.*"):
        if p.suffix in [".stl", ".step"]:
            p.unlink()
            print(f"   Deleted {p.name}")
    for p in pcb_dir.glob("*.svg"):
        p.unlink()
        print(f"   Deleted {p.name}")

def main():
    parser = argparse.ArgumentParser(description="Electronic Butterfly Asset & Model Builder")
    parser.add_argument("--cad-only", action="store_true", help="Generate only 3D CAD models (STL/STEP)")
    parser.add_argument("--pcb-only", action="store_true", help="Generate only PCB Art SVG vector layers")
    parser.add_argument("--sync-only", action="store_true", help="Synchronize configuration only")
    parser.add_argument("--clean", action="store_true", help="Clean artifacts before build")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    start_time = time.time()
    print("=" * 65)
    print("🦋 ELECTRONIC BUTTERFLY — ASSET BUILD SYSTEM")
    print("=" * 65)

    if args.clean:
        clean_artifacts()

    if args.sync_only:
        sync_project_config()
    elif args.cad_only:
        build_cad_models(args.verbose)
    elif args.pcb_only:
        build_pcb_art(args.verbose)
    else:
        # Full Build Pipeline
        build_cad_models(args.verbose)
        build_pcb_art(args.verbose)
        sync_project_config()

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"✨ All build tasks completed successfully in {elapsed:.2f} seconds!")
    print("=" * 65)

if __name__ == "__main__":
    main()
