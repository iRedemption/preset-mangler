"""Pure transformations applied to copied preset data."""

from __future__ import annotations

import copy
import random
from math import ceil, floor

from .constants import (
    CONFIRMED_DEFAULT_PARAMETER_VALUES,
    INTEGER_PARAMETER_KEYS,
    NON_INTERPOLATABLE_KEYS,
    OSCILLATOR_SUBTYPES,
    WARP_MODE_VALUE_KEYS,
    WARP_VALUE_KEYS,
)


def mutate_node(node: object, variance: float, rng: random.Random) -> object:
    if isinstance(node, dict):
        return {key: mutate_node(value, variance, rng) for key, value in node.items()}
    if isinstance(node, list):
        return [mutate_node(value, variance, rng) for value in node]
    if isinstance(node, tuple):
        return tuple(mutate_node(value, variance, rng) for value in node)
    if isinstance(node, bool):
        return node
    if isinstance(node, float):
        return node * (1.0 + rng.uniform(-variance, variance))
    return node


def round_nearest_integer(value: float) -> int:
    return floor(value + 0.5) if value >= 0 else ceil(value - 0.5)


def align_sibling_oscillator_warp(selected: dict, sibling: dict) -> dict:
    """Expose an active sibling subtype's compatible warp context to shared interpolation."""
    aligned = copy.deepcopy(sibling)
    for selected_key in selected.keys():
        selected_type = selected_key.rstrip("0123456789")
        if selected_type not in OSCILLATOR_SUBTYPES or not isinstance(selected[selected_key], dict):
            continue
        selected_params = selected[selected_key].get("plainParams")
        if not isinstance(selected_params, dict) or "kParamWarpMenu" not in selected_params:
            continue
        target = aligned.setdefault(selected_key, copy.deepcopy(selected[selected_key]))
        target_params = target.setdefault("plainParams", copy.deepcopy(selected_params))
        if not isinstance(target_params, dict):
            continue
        for mode_key, warp_keys in WARP_MODE_VALUE_KEYS.items():
            selected_mode = selected_params.get(mode_key)
            if selected_mode is None:
                continue
            sibling_params = aligned.get(selected_key, {}).get("plainParams") if isinstance(aligned.get(selected_key), dict) else None
            if isinstance(sibling_params, dict) and sibling_params.get(mode_key) == selected_mode:
                candidate_params = sibling_params
            else:
                candidate_params = None
                for sibling_key, sibling_value in aligned.items():
                    sibling_type = sibling_key.rstrip("0123456789")
                    if sibling_type not in OSCILLATOR_SUBTYPES or not isinstance(sibling_value, dict):
                        continue
                    candidate = sibling_value.get("plainParams")
                    if isinstance(candidate, dict) and candidate.get(mode_key) == selected_mode:
                        candidate_params = candidate
                        break
            if candidate_params is None:
                continue
            for warp_key in warp_keys:
                if warp_key in candidate_params:
                    target_params[warp_key] = candidate_params[warp_key]
                elif warp_key in CONFIRMED_DEFAULT_PARAMETER_VALUES:
                    target_params[warp_key] = CONFIRMED_DEFAULT_PARAMETER_VALUES[warp_key]
            target_params[mode_key] = selected_mode
    return aligned


def interpolate_node(
    selected: object,
    sibling: object,
    strength: float,
    key: str | None = None,
    counts: list[int] | None = None,
) -> object:
    """Move compatible parameter values toward a sibling without changing structure."""
    if key in NON_INTERPOLATABLE_KEYS:
        return copy.deepcopy(selected)
    if isinstance(selected, bool) or isinstance(sibling, bool):
        return copy.deepcopy(selected)
    if isinstance(selected, dict) and isinstance(sibling, dict):
        sibling = align_sibling_oscillator_warp(selected, sibling)
        differing_warp_modes = {
            mode_key
            for mode_key in WARP_MODE_VALUE_KEYS
            if mode_key in selected and mode_key in sibling and selected.get(mode_key) != sibling.get(mode_key)
        }
        output = copy.deepcopy(selected)
        for child_key in selected:
            if any(child_key in value_keys for mode_key, value_keys in WARP_MODE_VALUE_KEYS.items() if mode_key in differing_warp_modes):
                continue
            if child_key in sibling:
                sibling_value = sibling[child_key]
            elif child_key in CONFIRMED_DEFAULT_PARAMETER_VALUES:
                sibling_value = CONFIRMED_DEFAULT_PARAMETER_VALUES[child_key]
            else:
                continue
            output[child_key] = interpolate_node(selected[child_key], sibling_value, strength, child_key, counts)
        for child_key in sibling.keys() - selected.keys():
            if child_key not in CONFIRMED_DEFAULT_PARAMETER_VALUES:
                continue
            if any(child_key in value_keys for mode_key, value_keys in WARP_MODE_VALUE_KEYS.items() if mode_key in differing_warp_modes):
                continue
            output[child_key] = interpolate_node(
                CONFIRMED_DEFAULT_PARAMETER_VALUES[child_key],
                sibling[child_key],
                strength,
                child_key,
                counts,
            )
        return output
    if isinstance(selected, dict) and sibling == "default":
        output = copy.deepcopy(selected)
        for child_key, child_value in selected.items():
            if child_key in CONFIRMED_DEFAULT_PARAMETER_VALUES:
                output[child_key] = interpolate_node(
                    child_value,
                    CONFIRMED_DEFAULT_PARAMETER_VALUES[child_key],
                    strength,
                    child_key,
                    counts,
                )
        return output
    if isinstance(selected, list) and isinstance(sibling, list):
        if len(selected) != len(sibling) or key == "source":
            return copy.deepcopy(selected)
        return [interpolate_node(left, right, strength, key, counts) for left, right in zip(selected, sibling)]
    if isinstance(selected, tuple) and isinstance(sibling, tuple):
        if len(selected) != len(sibling) or key == "source":
            return copy.deepcopy(selected)
        return tuple(interpolate_node(left, right, strength, key, counts) for left, right in zip(selected, sibling))
    if isinstance(selected, (int, float)) and isinstance(sibling, (int, float)):
        value = selected + (strength * 0.5) * (sibling - selected)
        if counts is not None:
            counts[0] += 1
        if key in INTEGER_PARAMETER_KEYS or isinstance(selected, int) and isinstance(sibling, int):
            return round_nearest_integer(value)
        return value
    return copy.deepcopy(selected)
