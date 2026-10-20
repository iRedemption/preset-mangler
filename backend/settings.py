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
        stored = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError, AttributeError):
        stored = {}
    directory = stored.get("library", "")
    output_directory = stored.get("output_directory", "")
    safety_limiter = stored.get("safety_limiter", True)
    if not isinstance(safety_limiter, bool):
        safety_limiter = True
    try:
        count = len(library_paths(directory)) if directory else 0
        return {"library": directory, "output_directory": output_directory,
                "safety_limiter": safety_limiter, "valid": bool(count), "count": count}
    except (ValueError, OSError, TypeError) as error:
        return {"library": directory, "output_directory": output_directory,
                "safety_limiter": safety_limiter, "valid": False, "count": 0,
                "warning": str(error)}


def write_settings(directory):
    paths = library_paths(directory)
    directory = str(Path(directory).expanduser().resolve())
    settings = read_settings()
    output_directory = settings["output_directory"]
    safety_limiter = settings["safety_limiter"]
    CONFIG.write_text(json.dumps({"library": directory, "output_directory": output_directory,
                                  "safety_limiter": safety_limiter}, indent=2), encoding="utf-8")
    return {"library": directory, "output_directory": output_directory,
            "safety_limiter": safety_limiter,
            "valid": True, "count": len(paths)}


def write_output_directory(directory):
    if directory.strip():
        path = Path(directory).expanduser()
        if not path.is_dir():
            raise ValueError("Choose a valid output directory.")
        output_directory = str(path.resolve())
    else:
        output_directory = ""
    settings = read_settings()
    CONFIG.write_text(json.dumps({"library": settings["library"],
                                  "output_directory": output_directory,
                                  "safety_limiter": settings["safety_limiter"]}, indent=2),
                      encoding="utf-8")
    return read_settings()


def write_safety_limiter(enabled):
    if not isinstance(enabled, bool):
        raise ValueError("Safety limiter setting must be enabled or disabled.")
    settings = read_settings()
    CONFIG.write_text(json.dumps({"library": settings["library"],
                                  "output_directory": settings["output_directory"],
                                  "safety_limiter": enabled}, indent=2), encoding="utf-8")
    return read_settings()
