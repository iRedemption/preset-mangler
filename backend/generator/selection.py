"""Module lookup, schema labels, and parent selection helpers."""

from __future__ import annotations

import argparse
import json
import pathlib
import re

from .constants import (
    MODULE_SELECTOR,
    OSCILLATOR_SUBTYPES,
    OSCILLATOR_TYPES,
    ModuleRef,
)
from .families import FAMILIES


def parse_module(value: str) -> ModuleRef:
    match = MODULE_SELECTOR.fullmatch(value)
    if not match:
        raise argparse.ArgumentTypeError(f"invalid module '{value}'; use Oscillator0, Env0, or LFO0")
    return ModuleRef(match.group(1), int(match.group(2)))


def parse_oscillators(value: str) -> set[int]:
    result = set()
    for token in value.split(","):
        token = token.strip().lower().removeprefix("osc")
        if not token.isdigit() or not 0 <= int(token) <= 4:
            raise argparse.ArgumentTypeError("oscillators must be a comma-separated list such as 0,1 or osc0,osc2")
        result.add(int(token))
    if not result:
        raise argparse.ArgumentTypeError("at least one oscillator must be selected")
    return result


def source_labels(schema_dir: pathlib.Path) -> dict[tuple[int, int], str]:
    path = schema_dir / "sources.json"
    if not path.is_file():
        return {}
    registry = json.loads(path.read_text(encoding="utf-8"))
    labels = {(6, 0): "LFO0"}
    for raw_text, entry in registry.get("by_source_tuple", {}).items():
        if not entry.get("label"):
            continue
        try:
            raw = json.loads(raw_text)
            labels[(int(raw[0]), int(raw[1]))] = entry["label"]
        except (ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
            continue
    return labels


def module_value(data: dict, module: ModuleRef) -> object | None:
    if module.module_type in OSCILLATOR_SUBTYPES:
        wrapper = data.get(f"Oscillator{module.index}")
        return wrapper.get(module.key) if isinstance(wrapper, dict) else None
    return data.get(module.key)


def set_module_value(data: dict, module: ModuleRef, value: object) -> None:
    if module.module_type in OSCILLATOR_SUBTYPES:
        wrapper = data.get(f"Oscillator{module.index}")
        if not isinstance(wrapper, dict):
            raise KeyError(f"Oscillator{module.index} is missing")
        wrapper[module.key] = value
    else:
        data[module.key] = value


def destination_types(module_type: str) -> set[str]:
    return OSCILLATOR_TYPES if module_type == "Oscillator" else {module_type}


def patch_families(path: pathlib.Path) -> set[str]:
    raw_name = path.stem.lower()
    name = re.sub(r"[^a-z0-9]+", " ", raw_name)
    tokens = set(name.split())
    families = set()
    for family, mapping in FAMILIES.items():
        words = mapping.get("words", ())
        abbreviations = mapping.get("abbreviations", ())
        if any(word in tokens or (len(word) > 2 and word in raw_name) for word in words):
            families.add(family)
        if any(re.search(rf"(?<![a-z0-9]){re.escape(abbreviation)}(?![a-z0-9])", raw_name) for abbreviation in abbreviations):
            families.add(family)
    return families


def choose_parents(paths: list[pathlib.Path], mode: str, family: str | None) -> list[pathlib.Path]:
    if mode == "smart" and family:
        matching = [path for path in paths if family in patch_families(path)]
        if matching:
            return matching
    return paths
