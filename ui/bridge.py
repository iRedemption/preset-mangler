"""Small desktop API; preset work remains in backend."""

import base64
from pathlib import Path
from threading import RLock

import webview

from backend.container import unpack_in_memory
from backend.preset import load_preset, mangle, save_preset
from backend.generation import generate
from backend.generator.constants import PATCH_WORDS
from backend.stats import build as build_stats
from backend.settings import ASSETS, library_paths, modules, read_settings, write_settings


class Bridge:
    def __init__(self, initial=""):
        self._window, self.initial = None, initial
        self._preset, self._source, self._lock = None, None, RLock()
        self._name = ""

    def startup(self):
        return {"settings": read_settings(), "families": sorted(PATCH_WORDS),
                "modules": modules(load_preset(ASSETS / "Init.SerumPreset")),
                "source": self.load(self.initial) if self.initial else None}

    def settings(self, directory):
        try:
            return write_settings(directory)
        except Exception as error:
            return {"error": str(error)}

    def library_stats(self):
        try:
            config = read_settings()
            if not config["valid"]:
                raise ValueError("Set the library directory in Settings first.")
            return build_stats(config["library"])
        except Exception as error:
            return {"error": str(error)}

    def browse(self, kind):
        result = self._window.create_file_dialog(
            webview.FileDialog.FOLDER if kind in {"library", "directory"} else
            webview.FileDialog.OPEN if kind == "input" else webview.FileDialog.SAVE,
            save_filename="Mangled.SerumPreset", file_types=("Serum preset (*.SerumPreset)",))
        return result[0] if result else ""

    def load(self, path, encoded=None):
        with self._lock:
            try:
                preset = unpack_in_memory(base64.b64decode(encoded, validate=True)) if encoded else load_preset(path)
                source = None if encoded else Path(path).expanduser().resolve()
                self._preset, self._source = preset, source
                self._name = Path(path).name
                output = (source.parent if source else Path.cwd()) / f"{Path(path).stem} (Mangled).SerumPreset"
                return {"input": str(source or path), "output": str(output), "modules": modules(preset)}
            except Exception as error:
                return {"error": str(error)}

    def generate(self, destination, selections, options):
        with self._lock:
            try:
                config = read_settings()
                if not config["valid"]:
                    raise ValueError("Set the library directory in Settings first.")
                results = generate(config["library"], selections, mode=options["mode"],
                                   family=options["family"], count=options["count"],
                                   mutation=options["mutation"] / 100,
                                   interpolation=options["interpolation"] / 100,
                                   seed=options.get("seed"))
                dry = options.get("dry_run", False)
                folder = Path(destination).expanduser()
                if not destination.strip() and not dry:
                    raise ValueError("Choose an output directory.")
                prefix = options["family"] if options["mode"] == "smart" else "random"
                paths = [folder / f"generated_{prefix}_{index:03d}.SerumPreset"
                         for index in range(1, len(results) + 1)]
                if not dry:
                    inputs = {path.resolve() for path in library_paths(config["library"])}
                    if any(path.resolve() in inputs for path in paths):
                        raise ValueError("Choose an output directory that will not overwrite library presets.")
                    if any(path.exists() for path in paths) and not self._window.create_confirmation_dialog(
                            "Replace outputs?", "Replace existing generated files in this output directory?"):
                        return {"cancelled": True}
                    folder.mkdir(parents=True, exist_ok=True)
                report = []
                for path, (preset, events) in zip(paths, results):
                    if not dry:
                        save_preset(preset, path, overwrite=True)
                    report.extend([f"\n{path.name}", *events])
                return {"message": f"{'Previewed' if dry else 'Saved'} {len(results)} generated preset(s)",
                        "report": report}
            except Exception as error:
                return {"error": str(error)}

    def export(self, destination, modules, percent):
        with self._lock:
            try:
                if self._preset is None:
                    raise ValueError("Load a source preset first.")
                output, report = mangle(self._preset, [(key,) for key in modules], float(percent) / 100)
                path = Path(destination).expanduser()
                if self._source and path.resolve() == self._source:
                    raise ValueError("Choose a different output path to preserve the source preset.")
                if self._source is None and path.name.lower() == self._name.lower():
                    raise ValueError("Use a different output filename to preserve the dropped source.")
                if path.exists() and not self._window.create_confirmation_dialog(
                        "Replace output?", f"Replace {path.name}?"):
                    return {"cancelled": True}
                save_preset(output, path, self._source, overwrite=True)
                return {"message": f"Saved {path}", "report": report}
            except Exception as error:
                return {"error": str(error)}
