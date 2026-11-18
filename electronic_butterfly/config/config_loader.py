"""
Configuration Loader & Validator for Electronic Butterfly
Loads, parses, validates, and manages YAML configurations with environment variable overrides.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict
import yaml

CONFIG_DIR = Path(__file__).parent.resolve()

class ConfigDict(dict):
    """Dot-accessible dictionary for clean, intuitive parameter querying."""
    def __getattr__(self, key: str) -> Any:
        try:
            val = self[key]
            if isinstance(val, dict) and not isinstance(val, ConfigDict):
                val = ConfigDict(val)
                self[key] = val
            return val
        except KeyError:
            raise AttributeError(f"Configuration key '{key}' not found.")

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Recursively merges source dict into target dict."""
    for key, value in source.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            deep_merge(target[key], value)
        else:
            target[key] = value

def auto_load_dotenv(config_dir: Path = CONFIG_DIR) -> None:
    """
    Searches for and loads key=value pairs from .env files into os.environ.
    Checks:
    1. electronic_butterfly/.env
    2. project root .env
    """
    candidates = [
        config_dir.parent / ".env",
        config_dir.parent.parent / ".env",
    ]
    for env_path in candidates:
        if env_path.exists() and env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Safely loads a YAML configuration file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_all_configs(config_dir: Path = CONFIG_DIR, ignore_json: bool = False) -> ConfigDict:
    """
    Loads all parameter files and merges them into a unified configuration tree:
    - network.param.yaml
    - hardware.param.yaml
    - kinematics.param.yaml
    - effects.param.yaml
    - default_config.json (if modified by user)
    - .env environment variable overrides
    """
    # 1. Auto-discover and load .env files into os.environ
    auto_load_dotenv(config_dir)

    merged: Dict[str, Any] = {}

    files = [
        config_dir / "network.param.yaml",
        config_dir / "hardware.param.yaml",
        config_dir / "kinematics.param.yaml",
        config_dir / "effects.param.yaml",
    ]

    yaml_mtimes = []
    for file_path in files:
        if file_path.exists():
            data = load_yaml(file_path)
            merged.update(data)
            yaml_mtimes.append(file_path.stat().st_mtime)

    # 2. Check if default_config.json has user modifications or overrides
    json_path = config_dir / "default_config.json"
    if not ignore_json and json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            # If default_config.json exists, merge user changes
            latest_yaml = max(yaml_mtimes) if yaml_mtimes else 0
            # If json is newer or contains dev_port customization, merge it
            if json_path.stat().st_mtime >= latest_yaml:
                deep_merge(merged, json_data)
            else:
                # Even if older, preserve explicit port changes if yaml was untouched
                json_server = json_data.get("network", {}).get("server", {})
                yaml_server = merged.get("network", {}).get("server", {})
                if json_server.get("dev_port") and json_server.get("dev_port") != 8080:
                    yaml_server["dev_port"] = json_server["dev_port"]
        except Exception:
            pass

    # 3. Apply environment variable overrides if present
    apply_env_overrides(merged)

    # 4. Validate logical boundaries
    validate_config(merged)

    return ConfigDict(merged)

def apply_env_overrides(cfg: Dict[str, Any]) -> None:
    """Overrides configuration with environment variables if set."""
    net = cfg.setdefault("network", {})
    ap = net.setdefault("access_point", {})
    server = net.setdefault("server", {})

    if "BUTTERFLY_SSID" in os.environ:
        ap["ssid"] = os.environ["BUTTERFLY_SSID"]
    if "BUTTERFLY_PASS" in os.environ:
        ap["password"] = os.environ["BUTTERFLY_PASS"]
    if "BUTTERFLY_HOST" in os.environ:
        server["host"] = os.environ["BUTTERFLY_HOST"]
    if "BUTTERFLY_PORT" in os.environ:
        server["http_port"] = int(os.environ["BUTTERFLY_PORT"])
    if "BUTTERFLY_DEV_PORT" in os.environ:
        server["dev_port"] = int(os.environ["BUTTERFLY_DEV_PORT"])

def validate_config(cfg: Dict[str, Any]) -> None:
    """Validates physical and electrical boundaries to ensure safe robot operation."""
    # Validate Kinematics limits
    kin = cfg.get("kinematics", {}).get("limits", {})
    min_a = kin.get("min_safe_angle_deg", 15.0)
    max_a = kin.get("max_safe_angle_deg", 85.0)
    if min_a < 0.0 or max_a > 180.0 or min_a >= max_a:
        raise ValueError(f"Invalid servo angle limits: min={min_a}, max={max_a}. Must satisfy 0 <= min < max <= 180.")

    # Validate Network Ports
    server = cfg.get("network", {}).get("server", {})
    port = server.get("http_port", 80)
    if not (1 <= port <= 65535):
        raise ValueError(f"Invalid HTTP server port: {port}. Must be between 1 and 65535.")

    # Validate LED count
    leds = cfg.get("effects", {}).get("leds", {})
    total = leds.get("total_count", 16)
    per_wing = leds.get("leds_per_wing", 8)
    if total != per_wing * 2:
        raise ValueError(f"Mismatch in LED count: total={total} but per_wing={per_wing} * 2.")

def export_json(output_path: Path = CONFIG_DIR / "default_config.json") -> Path:
    """Exports the merged configuration as a static JSON file for web apps or firmware."""
    cfg = load_all_configs()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return output_path

if __name__ == "__main__":
    config = load_all_configs()
    json_path = export_json()
    print("=" * 60)
    print("🦋 ELECTRONIC BUTTERFLY CONFIGURATION LOADED SUCCESSFULLY")
    print(f"Network SoftAP SSID:   {config.network.access_point.ssid}")
    print(f"Server Host & Port:    {config.network.server.host}:{config.network.server.http_port} (Dev: {config.network.server.dev_port})")
    print(f"Servo Pins:            Left=GPIO{config.hardware.pins.servo_left}, Right=GPIO{config.hardware.pins.servo_right}")
    print(f"Flap Range Limits:     {config.kinematics.limits.min_safe_angle_deg}° to {config.kinematics.limits.max_safe_angle_deg}°")
    print(f"Total WS2812B LEDs:    {config.effects.leds.total_count} ({config.effects.leds.leds_per_wing} per wing)")
    print(f"Exported JSON:         {json_path}")
    print("=" * 60)
