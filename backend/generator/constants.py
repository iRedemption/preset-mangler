"""Shared constants and small value objects for preset generation."""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass


PACKAGE_DIR = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_BASE_PRESET = PACKAGE_DIR / "assets" / "Init.SerumPreset"
MODULE_SELECTOR = re.compile(r"^([A-Za-z]+?)(\d+)$")
OSCILLATOR_TYPES = {"Oscillator", "WTOsc", "SampleOsc", "MultiSampleOsc", "SpectralOsc", "GranularOsc", "NoiseOsc", "SubOsc"}
OSCILLATOR_SUBTYPES = OSCILLATOR_TYPES - {"Oscillator"}
MODULE_GROUPS = {
    "oscillators": ("Oscillator", 5),
    "sub-oscillator": ("SubOsc", 1),
    "filter": ("VoiceFilter", 2),
    "envelopes": ("Env", 4),
    "lfos": ("LFO", 10),
    "macros": ("Macro", 8),
    "fx": ("FXRack", 3),
    "routing": ("RoutingSlot", 7),
}
PATCH_WORDS = {
    "bass": ("bass", "808", "reese", "sub", "bs", "ba"),
    "lead": ("lead", "ld", "synthlead"),
    "keys": ("keys", "key", "piano", "ky"),
    "arp": ("arp", "arpeggio", "ar"),
    "pluck": ("pluck", "plk", "plucks", "plucke", "pl"),
}
PATCH_ABBREVIATIONS = {
    "bass": ("bs", "ba"),
    "lead": ("ld",),
    "keys": ("ky",),
    "arp": ("ar",),
    "pluck": ("plk", "pl"),
}
NON_INTERPOLATABLE_KEYS = {
    "source",
    "destModuleTypeString",
    "destModuleID",
    "destModuleParamID",
    "destModuleParamName",
    "kParamEnable",
    "kParamBeatSync",
    "kParamWarpMenu",
    "kParamWarpMenu2",
    "kParamDetuneMode",
    "kParamUnisonStack",
}
WARP_VALUE_KEYS = {"kParamWarp", "kParamWarp2", "kParamWarpVar", "kParamWarpVar2"}
WARP_MODE_VALUE_KEYS = {
    "kParamWarpMenu": ("kParamWarp", "kParamWarpVar"),
    "kParamWarpMenu2": ("kParamWarp2", "kParamWarpVar2"),
}
CONFIRMED_DEFAULT_PARAMETER_VALUES = {
    "kParamDetune": 0.25,
    "kParamUnison": 1.0,
    "kParamRandomPhase": 100.0,
    "kParamWarp": 0.0,
    "kParamWarp2": 0.0,
}
INTEGER_PARAMETER_KEYS = {"kParamUnison"}


@dataclass(frozen=True)
class ModuleRef:
    module_type: str
    index: int

    @property
    def key(self) -> str:
        return f"{self.module_type}{self.index}"
