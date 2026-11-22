#!/usr/bin/env python3
"""
Electronic Butterfly — Kinematics & Electrical Power Simulator
=============================================================
Simulates biological harmonic wing flapping motion, validates physical angle
boundaries against mechanical stalls, computes angular velocity/acceleration,
and estimates real-time electrical power consumption.

Usage:
    python3 scripts/simulate_kinematics.py                      # Default flutter simulation
    python3 scripts/simulate_kinematics.py --mode startled      # Startled escape burst
    python3 scripts/simulate_kinematics.py --mode all           # Test all 6 behavioral modes
    python3 scripts/simulate_kinematics.py --live               # Live animated terminal display
    python3 scripts/simulate_kinematics.py --plot               # Generate PNG waveform graph
    python3 scripts/simulate_kinematics.py --power              # Detailed battery power breakdown
"""

import argparse
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Auto-detect and switch to .venv interpreter if needed
PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_DIR
VENV_PYTHON = WORKSPACE_ROOT / ".venv" / "bin" / "python3"
if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

sys.path.insert(0, str(PROJECT_DIR))

from config.config_loader import load_all_configs

def compute_wing_angle(
    t: float,
    freq: float,
    amplitude: float,
    center: float,
    harmonic_ratio: float = 0.22,
    harmonic_phase: float = 0.35
) -> Tuple[float, float, str]:
    """
    Evaluates biomimetic Fourier harmonic equation:
    theta(t) = center + A1 * sin(2*pi*f*t) + A2 * sin(4*pi*f*t + phi)
    """
    if freq <= 0.0 or amplitude <= 0.0:
        return center, 0.0, "Stationary"

    omega = 2.0 * math.pi * freq
    h1 = math.sin(omega * t)
    h2 = harmonic_ratio * math.sin(2.0 * omega * t + harmonic_phase)
    stroke = h1 + h2

    angle = center + (amplitude * stroke)

    # First derivative: angular velocity (rad/s converted to deg/s)
    h1_dot = omega * math.cos(omega * t)
    h2_dot = 2.0 * omega * harmonic_ratio * math.cos(2.0 * omega * t + harmonic_phase)
    ang_vel_deg_s = amplitude * (h1_dot + h2_dot)

    phase_label = "▲ Upstroke" if ang_vel_deg_s > 0 else "▼ Downstroke"
    return angle, ang_vel_deg_s, phase_label

def estimate_power_draw(
    angle: float,
    ang_vel_deg_s: float,
    num_leds: int = 8,
    led_brightness: int = 180
) -> Tuple[float, float]:
    """
    Estimates total system current (mA) and power (mW) at 5V:
    - ESP32-C3 Base: ~45 mA
    - 2x Servos: 15 mA idle holding + load proportional to |velocity| (up to 350 mA)
    - 8x WS2812B LEDs (4 per wing): ~1 mA quiescent + ~12 mA per LED at current brightness
    """
    mcu_ma = 45.0
    servo_holding_ma = 30.0 # 15 mA per servo
    servo_dynamic_ma = min(400.0, abs(ang_vel_deg_s) * 0.45)
    led_ma = num_leds * (1.0 + (led_brightness / 255.0) * 12.0)

    total_ma = mcu_ma + servo_holding_ma + servo_dynamic_ma + led_ma
    total_mw = total_ma * 5.0 # 5V rail
    return total_ma, total_mw

def render_ascii_bar(val: float, min_val: float, max_val: float, width: int = 24) -> str:
    """Renders a smooth ASCII progress bar for terminal visualization."""
    norm = max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))
    filled = int(norm * width)
    return "█" * filled + "░" * (width - filled)

def simulate_mode(
    mode_key: str,
    mode_cfg: Dict,
    kin_limits: Dict,
    duration: float = 2.5,
    fps: int = 25,
    live: bool = False,
    show_power: bool = False
):
    freq = mode_cfg.get("frequency_hz", 1.5)
    amp = mode_cfg.get("amplitude_deg", 25.0)
    center = mode_cfg.get("center_angle_deg", 45.0)
    name = mode_cfg.get("name", mode_key)

    min_limit = kin_limits.get("min_safe_angle_deg", 15.0)
    max_limit = kin_limits.get("max_safe_angle_deg", 85.0)

    print(f"\n▶ Testing Mode: [{name.upper()}] (f={freq} Hz, Amp=±{amp}°, Center={center}°)")
    print("-" * 75)
    header = f"{'Time (s)':^9} | {'Angle (°)':^10} | {'Velocity (°/s)':^15} | {'Waveform (15°-85°)':^22}"
    if show_power:
        header += f" | {'Power (mA / mW)':^17}"
    print(header)
    print("-" * 75)

    steps = int(duration * fps)
    dt = 1.0 / fps

    peak_vel = 0.0
    total_energy_mws = 0.0
    is_safe = True

    for i in range(steps + 1):
        t = i * dt
        angle, vel, phase = compute_wing_angle(t, freq, amp, center)
        peak_vel = max(peak_vel, abs(vel))

        # Check safety boundaries
        if angle < min_limit or angle > max_limit:
            is_safe = False

        bar = render_ascii_bar(angle, min_limit, max_limit, width=18)
        current_ma, power_mw = estimate_power_draw(angle, vel)
        total_energy_mws += power_mw * dt

        line = f"{t:^9.2f} | {angle:^10.1f} | {vel:^15.1f} | [{bar}] {phase[:1]}"
        if show_power:
            line += f" | {current_ma:>6.1f}mA / {power_mw:>5.0f}mW"

        if live:
            sys.stdout.write("\r" + line)
            sys.stdout.flush()
            time.sleep(dt)
        else:
            print(line)

    if live:
        print() # Newline after live animation

    avg_power_mw = total_energy_mws / duration if duration > 0 else 0
    avg_current_ma = avg_power_mw / 5.0
    battery_hrs = (500.0 / avg_current_ma) if avg_current_ma > 0 else 0

    print("-" * 75)
    status_str = "✅ PASS (Within mechanical limits)" if is_safe else "❌ FAIL (Exceeds mechanical limits)"
    print(f"Status: {status_str} | Peak Velocity: {peak_vel:.1f} °/s | Avg Current: {avg_current_ma:.1f} mA | Est. Runtime: {battery_hrs:.1f} hrs")

def generate_plot(output_file: Path, cfg):
    """Generates a high-resolution waveform visualization plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        kin_modes = cfg.kinematics.modes
        limits = cfg.kinematics.limits

        t = np.linspace(0, 3.0, 600)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, dpi=150)
        plt.subplots_adjust(hspace=0.25)

        fig.patch.set_facecolor("#0b0f19")
        for ax in (ax1, ax2):
            ax.set_facecolor("#111827")
            ax.grid(True, color="#1f293b", linestyle="--", alpha=0.7)
            ax.tick_params(colors="#94a3b8")
            for spine in ax.spines.values():
                spine.set_color("#334155")

        # Plot 1: Wing Angles
        colors = {
            "flutter": "#38bdf8",
            "active_flight": "#10b981",
            "startled_burst": "#f43f5e",
            "breathing": "#a855f7"
        }

        for m_key in ["breathing", "flutter", "active_flight", "startled_burst"]:
            m_cfg = getattr(kin_modes, m_key)
            angles = [compute_wing_angle(ti, m_cfg.frequency_hz, m_cfg.amplitude_deg, m_cfg.center_angle_deg)[0] for ti in t]
            ax1.plot(t, angles, label=f"{m_cfg.name} ({m_cfg.frequency_hz} Hz)", color=colors[m_key], linewidth=2.0)

        ax1.axhline(limits.max_safe_angle_deg, color="#ef4444", linestyle=":", label="Mechanical Max Limit (85°)")
        ax1.axhline(limits.min_safe_angle_deg, color="#f59e0b", linestyle=":", label="Mechanical Min Limit (15°)")
        ax1.set_ylabel("Wing Angle (Degrees)", color="#f1f5f9", fontsize=10)
        ax1.set_title("Electronic Butterfly — Biomimetic Wing Kinematics Trajectories", color="#f1f5f9", fontsize=12, fontweight="bold")
        ax1.legend(loc="upper right", facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0", fontsize=8)

        # Plot 2: Electrical Current
        flutter_cfg = kin_modes.flutter
        currents = []
        for ti in t:
            angle, vel, _ = compute_wing_angle(ti, flutter_cfg.frequency_hz, flutter_cfg.amplitude_deg, flutter_cfg.center_angle_deg)
            ma, _ = estimate_power_draw(angle, vel)
            currents.append(ma)

        ax2.plot(t, currents, color="#38bdf8", linewidth=1.8, label="Total 5V Current Draw (Flutter Mode)")
        ax2.fill_between(t, currents, color="#38bdf8", alpha=0.15)
        ax2.set_xlabel("Time (Seconds)", color="#f1f5f9", fontsize=10)
        ax2.set_ylabel("Current Draw (mA)", color="#f1f5f9", fontsize=10)
        ax2.legend(loc="upper right", facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0", fontsize=8)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(output_file), facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()
        print(f"📊 Waveform graph saved to: {output_file}")
    except ImportError:
        print("⚠️ Matplotlib not installed; skipping graphic plot generation.")

def main():
    cfg = load_all_configs()
    kin_modes = cfg.kinematics.modes
    limits = cfg.kinematics.limits

    parser = argparse.ArgumentParser(description="Electronic Butterfly Kinematics & Power Simulator")
    parser.add_argument("--mode", default="flutter", choices=["sleep", "breathe", "flutter", "flight", "startled", "glide", "all"],
                        help="Behavioral mode to simulate (default: flutter)")
    parser.add_argument("--duration", type=float, default=2.5, help="Simulation duration in seconds (default: 2.5s)")
    parser.add_argument("--fps", type=int, default=20, help="Sampling rate in frames/sec (default: 20)")
    parser.add_argument("--live", action="store_true", help="Animated real-time terminal progress")
    parser.add_argument("--power", action="store_true", help="Display current and power estimates")
    parser.add_argument("--plot", action="store_true", help="Export high-resolution PNG waveform plot")
    args = parser.parse_args()

    print("=" * 75)
    print("🦋 ELECTRONIC BUTTERFLY — KINEMATICS & POWER SIMULATOR")
    print("=" * 75)

    mode_map = {
        "sleep": kin_modes.sleep,
        "breathe": kin_modes.breathing,
        "flutter": kin_modes.flutter,
        "flight": kin_modes.active_flight,
        "startled": kin_modes.startled_burst,
        "glide": kin_modes.glide
    }

    if args.mode == "all":
        for k, m_cfg in mode_map.items():
            simulate_mode(k, m_cfg, limits, duration=args.duration, fps=args.fps, live=args.live, show_power=args.power)
    else:
        target_cfg = mode_map[args.mode]
        simulate_mode(args.mode, target_cfg, limits, duration=args.duration, fps=args.fps, live=args.live, show_power=args.power)

    if args.plot:
        plot_path = PROJECT_DIR / "docs" / "kinematics_waveform.png"
        generate_plot(plot_path, cfg)

    print("\n" + "=" * 75)
    print("✨ Simulation finished.")
    print("=" * 75)

if __name__ == "__main__":
    main()
