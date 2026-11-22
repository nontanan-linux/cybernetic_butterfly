#!/usr/bin/env python3
"""
Electronic Butterfly — Interactive 3D CAD & Kinematics Visualizer Server
======================================================================
Launches the WebGL 3D simulator & CAD inspector powered by Three.js.
Clearly separates:
- Generated CAD models in cad/models/ (.STL parts + Full Assembly .STL/.STEP)
- External Read-Only CAD models in cad/external/ (MG90S Servo & Horn)
"""

import argparse
import http.server
import json
import socket
import sys
import threading
import webbrowser
from pathlib import Path

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
    """HTTP handler serving web visualizer, generated/external CAD models, and API endpoints."""
    def __init__(self, *args, **kwargs):
        directory = str(PROJECT_DIR / "web_visualizer")
        super().__init__(*args, directory=directory, **kwargs)

    def _resolve_model_file(self, filename: str) -> Path:
        models_dir = PROJECT_DIR / "cad" / "models"
        external_dir = PROJECT_DIR / "cad" / "external"
        p_gen = models_dir / filename
        if p_gen.exists() and p_gen.is_file():
            return p_gen
        p_ext = external_dir / filename
        if p_ext.exists() and p_ext.is_file():
            return p_ext
        return p_gen

    def do_GET(self):
        models_dir = PROJECT_DIR / "cad" / "models"
        external_dir = PROJECT_DIR / "cad" / "external"

        # 1. API: Catalog of Generated vs External CAD Models
        if self.path == "/api/models":
            catalog = [
                {
                    "id": "butterfly_full_assembly",
                    "name": "🦋 Full Robotic Assembly (.STL + .STEP)",
                    "file": "butterfly_full_assembly.stl",
                    "step": "butterfly_full_assembly.step",
                    "source": "generated_assembly",
                    "type": "GENERATED ASSEMBLY (.STL & .STEP)",
                    "color": "#3b82f6",
                    "features": "Complete assembly: Body (with Clubbed Antennae & 14500 Battery Abdomen) + 2x Wings + 6x Tucked Legs + 2x External MG90S Servos & Horns"
                },
                {
                    "id": "body",
                    "name": "🧬 Main Body (Antennae, Thorax & 14500 Battery Abdomen)",
                    "file": "body.stl",
                    "step": None,
                    "source": "generated_part",
                    "type": "GENERATED PART (.STL ONLY)",
                    "color": "#64748b",
                    "features": "Head with Sweeping Clubbed Antennae & Coiled Proboscis, Streamlined Thorax, Elongated Abdomen with Snap-In 14500 Li-ion Battery Bay & ESP32-C3 Upper Deck"
                },
                {
                    "id": "left_wing",
                    "name": "🪽 Left Butterfly Wing (3D Venation & Horn Clevis)",
                    "file": "left_wing.stl",
                    "step": None,
                    "source": "generated_part",
                    "type": "GENERATED PART (.STL ONLY)",
                    "color": "#10b981",
                    "features": "Two-Lobed Forewing + Cleft Notch + Swallowtail Hindwing, 3D Raised Venation Skeleton, Direct-Drive Horn Clevis, 4x WS2812B LED Pockets"
                },
                {
                    "id": "right_wing",
                    "name": "🪽 Right Butterfly Wing (Symmetric Mirror)",
                    "file": "right_wing.stl",
                    "step": None,
                    "source": "generated_part",
                    "type": "GENERATED PART (.STL ONLY)",
                    "color": "#10b981",
                    "features": "100% Bilateral CAD Mirror across Plane.XZ for flight symmetry"
                },
                {
                    "id": "butterfly_legs",
                    "name": "🦿 Biomimetic Butterfly Legs (Tucked 6-Leg Sternum)",
                    "file": "butterfly_legs.stl",
                    "step": None,
                    "source": "generated_part",
                    "type": "GENERATED PART (.STL ONLY)",
                    "color": "#475569",
                    "features": "Streamlined Ventral Sternum Keel nested flush inside thorax saddle + 3 Pairs of Tucked Lepidoptera Legs (Coxa, Femur, Tibia, Tarsus, Paired Claws)"
                },
                {
                    "id": "mg90s_servo",
                    "name": "⚙️ [External] MG90S Micro Servo (Read-Only)",
                    "file": "mg90s_servo.stl",
                    "step": "Servo-sg90.step",
                    "source": "external",
                    "type": "EXTERNAL CAD (READ-ONLY)",
                    "color": "#1d4ed8",
                    "features": "External Read-Only Hardware Model (cad/external/Servo-sg90.step): 180° Metal Gear Micro Servo"
                },
                {
                    "id": "mg90s_servo_horn",
                    "name": "🪓 [External] MG90S Single-Arm Horn (Read-Only)",
                    "file": "mg90s_servo_horn.stl",
                    "step": "SG90-1-arm-horn.step",
                    "source": "external",
                    "type": "EXTERNAL CAD (READ-ONLY)",
                    "color": "#f8fafc",
                    "features": "External Read-Only Hardware Model (cad/external/SG90-1-arm-horn.step): 21T Splined Nylon Horn"
                }
            ]

            for item in catalog:
                base_dir = external_dir if item["source"] == "external" else models_dir
                f_stl = base_dir / item["file"]
                if f_stl.exists():
                    item["size_stl"] = f"{round(f_stl.stat().st_size / 1024, 1)} KB"
                if item["step"]:
                    f_step = base_dir / item["step"]
                    if f_step.exists():
                        item["size_step"] = f"{round(f_step.stat().st_size / 1024, 1)} KB"

            data = json.dumps(catalog).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 2. File Server: CAD Model Assets (/models/...) from cad/models/ or cad/external/
        if self.path.startswith("/models/"):
            filename = self.path[len("/models/"):]
            file_path = self._resolve_model_file(filename)
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
        if self.path.startswith("/models/"):
            filename = self.path[len("/models/"):]
            file_path = self._resolve_model_file(filename)
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
        pass

def start_server(host: str, port: int, open_browser: bool):
    lan_ip = get_lan_ip()
    local_url = f"http://localhost:{port}"
    lan_url = f"http://{lan_ip}:{port}"

    print("=" * 68)
    print("🦋 ELECTRONIC BUTTERFLY — 3D CAD INSPECTOR & KINEMATICS VISUALIZER")
    print("=" * 68)
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
