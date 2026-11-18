#!/usr/bin/env python3
"""
Electronic Butterfly — Interactive 3D CAD & Kinematics Visualizer Server
======================================================================
Launches the WebGL 3D simulator & CAD inspector powered by Three.js.
Reads host, dev_port, and CORS settings from config/network.param.yaml or .env.

Features:
- Static CAD Model Inspection for all exported parts and assemblies (.STL & .STEP)
- Interactive Kinematic Simulation toggle (only runs when explicitly triggered)
- Model catalog API (/api/models) and static model file server (/models/<file>)

Usage:
    python3 scripts/visualize_model.py                  # Run server (default host:port from config)
    python3 scripts/visualize_model.py --browser        # Run and automatically open default browser
    python3 scripts/visualize_model.py --port 8088      # Run on custom port
"""

import argparse
import http.server
import json
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Auto-detect and switch to .venv interpreter if needed
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
VENV_PYTHON = WORKSPACE_ROOT / ".venv" / "bin" / "python3"
if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from config.config_loader import load_all_configs

def get_lan_ip() -> str:
    """Attempts to discover the primary local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler serving web visualizer, CAD models, and API endpoints."""
    def __init__(self, *args, **kwargs):
        directory = str(PROJECT_DIR / "web_visualizer")
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        models_dir = PROJECT_DIR / "cad" / "models"

        # 1. API: List of all generated CAD models
        if self.path == "/api/models":
            catalog = [
                {
                    "id": "butterfly_full_assembly",
                    "name": "🦋 Full Robotic Assembly",
                    "file": "butterfly_full_assembly.stl",
                    "step": "butterfly_full_assembly.step",
                    "type": "assembly",
                    "color": "#3b82f6",
                    "features": "Complete robot: Body + 2x MG90S Servos + 2x Horns + 2x Wings + Base Stand & Lid"
                },
                {
                    "id": "body",
                    "name": "🧬 Main Body Chassis (Thorax & Abdomen)",
                    "file": "body.stl",
                    "step": "body.step",
                    "type": "chassis",
                    "color": "#64748b",
                    "features": "Head with Antenna Sockets, Dual MG90S Bays, Outboard Hinges, ESP32-C3 Tray, USB-C Port, 470µF Cradle, 2-Pin JST Battery Terminal"
                },
                {
                    "id": "left_wing",
                    "name": "🪽 Left Wing (Direct-Drive Joint & Connector)",
                    "file": "left_wing.stl",
                    "step": "left_wing.step",
                    "type": "wing",
                    "color": "#10b981",
                    "features": "Servo Horn Recess with M2 Screwdriver Access Hole, Outer Support Hinge, 3-Pin JST-SH Socket on Neutral Axis, 4x LED Pockets"
                },
                {
                    "id": "right_wing",
                    "name": "🪽 Right Wing (Symmetric Mirrored Blade)",
                    "file": "right_wing.stl",
                    "step": "right_wing.step",
                    "type": "wing",
                    "color": "#10b981",
                    "features": "100% Bilateral CAD Mirror across Plane.XZ for perfect flight symmetry"
                },
                {
                    "id": "mg90s_servo",
                    "name": "⚙️ Real MG90S Micro Servo (Metal Gear)",
                    "file": "mg90s_servo.stl",
                    "step": "mg90s_servo.step",
                    "type": "actuator",
                    "color": "#1d4ed8",
                    "features": "Official Engineering CAD Model: 180° Metal Gear, 21T Splined Shaft, M2 Threaded Hole, 28mm Pitch Mounting Tabs"
                },
                {
                    "id": "mg90s_servo_horn",
                    "name": "🪓 Real MG90S Nylon Servo Horn",
                    "file": "mg90s_servo_horn.stl",
                    "step": "mg90s_servo_horn.step",
                    "type": "linkage",
                    "color": "#f8fafc",
                    "features": "Official Engineering CAD Model: Splined Hub with M2 Countersink, Tapered Single Arm with Fastening Holes"
                },
                {
                    "id": "base_stand",
                    "name": "🏛️ Base Stand & Battery Power Core",
                    "file": "base_stand.stl",
                    "step": "base_stand.step",
                    "type": "stand",
                    "color": "#475569",
                    "features": "14500 Battery Bay, TP4056 USB-C Charger Bay, 5V Boost Converter, Slide Switch, Ballast Cavity & Support Stem"
                },
                {
                    "id": "base_stand_lid",
                    "name": "🛡️ Base Stand Bottom Lid",
                    "file": "base_stand_lid.stl",
                    "step": "base_stand_lid.step",
                    "type": "stand",
                    "color": "#334155",
                    "features": "Protective Bottom Hatch with Battery Retention & M2 Fastener Holes"
                }
            ]

            # Populate live file sizes
            for item in catalog:
                f_stl = models_dir / item["file"]
                if f_stl.exists():
                    item["size_stl"] = f"{round(f_stl.stat().st_size / 1024, 1)} KB"
                f_step = models_dir / item["step"]
                if f_step.exists():
                    item["size_step"] = f"{round(f_step.stat().st_size / 1024, 1)} KB"

            data = json.dumps(catalog).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 2. File Server: CAD Model Assets (/models/...)
        if self.path.startswith("/models/"):
            filename = self.path[len("/models/"):]
            file_path = models_dir / filename
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if filename.endswith(".stl"):
                    self.send_header("Content-Type", "model/stl")
                elif filename.endswith(".step") or filename.endswith(".stp"):
                    self.send_header("Content-Type", "application/step")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(file_path.stat().st_size))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.copyfile(f, self.wfile)
                return
            else:
                self.send_error(404, f"CAD Model '{filename}' not found")
                return

        super().do_GET()

    def do_HEAD(self):
        models_dir = PROJECT_DIR / "cad" / "models"
        if self.path.startswith("/models/"):
            filename = self.path[len("/models/"):]
            file_path = models_dir / filename
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if filename.endswith(".stl"):
                    self.send_header("Content-Type", "model/stl")
                elif filename.endswith(".step") or filename.endswith(".stp"):
                    self.send_header("Content-Type", "application/step")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(file_path.stat().st_size))
                self.end_headers()
                return
            else:
                self.send_error(404, f"CAD Model '{filename}' not found")
                return
        super().do_HEAD()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        # Suppress standard noisy access logs; keep terminal clean
        pass

def start_server(host: str, port: int, open_browser: bool):
    lan_ip = get_lan_ip()
    local_url = f"http://localhost:{port}"
    lan_url = f"http://{lan_ip}:{port}"

    print("=" * 68)
    print("🦋 ELECTRONIC BUTTERFLY — 3D CAD INSPECTOR & KINEMATICS VISUALIZER")
    print("=" * 68)
    print("Features:")
    print(" • Static 3D CAD Model Inspector with part selector dropdown")
    print(" • Real MG90S Servo & Horn, Direct-Drive Joint, Circuit-Ready Chassis")
    print(" • Optional Flapping Simulation (activates only when user requests)")
    print(" • Wireframe toggle, PBR material shading, model dimensions & poly count")
    print("-" * 68)
    print(f"📡 Local Browser URL:    {local_url}")
    print(f"🌐 Network / Mobile URL: {lan_url}")
    print("=" * 68)
    print("Press Ctrl+C to terminate the visualizer server.\n")

    if open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(local_url)).start()

    server_address = (host, port)
    try:
        httpd = http.server.ThreadingHTTPServer(server_address, CustomHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Visualizer server stopped.")
    except OSError as e:
        print(f"\n❌ Failed to bind server to {host}:{port}: {e}")
        print("   Try specifying another port: python3 scripts/visualize_model.py --port 8081")

def main():
    cfg = load_all_configs()
    default_host = cfg.network.server.host
    default_port = cfg.network.server.dev_port or cfg.network.server.http_port

    parser = argparse.ArgumentParser(description="Electronic Butterfly 3D CAD Visualizer Server")
    parser.add_argument("--host", default=default_host, help=f"Host interface (default: {default_host})")
    parser.add_argument("--port", type=int, default=default_port, help=f"Server port (default: {default_port})")
    parser.add_argument("--browser", action="store_true", help="Automatically open browser on start")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser")
    args = parser.parse_args()

    open_in_browser = args.browser and not args.no_browser
    start_server(args.host, args.port, open_in_browser)

if __name__ == "__main__":
    main()
