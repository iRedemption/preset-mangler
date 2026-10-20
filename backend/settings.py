"""Local library settings and shared module discovery."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONFIG = ROOT / "settings.json"
MODULE_TYPES = {"Oscillator", "VoiceFilter", "Env", "LFO", "Macro", "FXRack"}


def modules(preset):
    return [key for key in preset["data"] if key.rstrip("0123456789") in MODULE_TYPES]


def library_paths(directory):
    if not str(directory).strip():
        raise ValueError("Set a Serum preset library directory in Settings.")
    directory = Path(directory).expanduser()
    if not directory.is_dir():
        raise ValueError("Set a valid Serum preset library directory in Settings.")
    paths = sorted(path for path in directory.iterdir()
                   if path.is_file() and path.suffix.lower() == ".serumpreset")
    if not paths:
        raise ValueError("The library must contain .SerumPreset files directly inside it.")
    return paths


def read_settings():
    try:
        directory = json.loads(CONFIG.read_text(encoding="utf-8")).get("library", "")
    except (OSError, ValueError, AttributeError):
        directory = ""
    try:
        count = len(library_paths(directory)) if directory else 0
        return {"library": directory, "valid": bool(count), "count": count}
    except (ValueError, OSError, TypeError) as error:
        return {"library": directory, "valid": False, "count": 0, "warning": str(error)}


def write_settings(directory):
    paths = library_paths(directory)
    directory = str(Path(directory).expanduser().resolve())
    CONFIG.write_text(json.dumps({"library": directory}, indent=2), encoding="utf-8")
    return {"library": directory, "valid": True, "count": len(paths)}
