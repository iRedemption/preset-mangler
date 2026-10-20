"""Selected-module generation: Init base, donor-local routes, strict smart matching."""

import copy
import random

from .generator.constants import PATCH_WORDS
from .generator.selection import destination_types, parse_module, patch_families, source_labels
from .generator.transforms import interpolate_node, mutate_node
from .preset import load_preset
from .settings import ASSETS, library_paths, modules


def prepare_library(directory, mode, family):
    if mode not in {"random", "smart"}:
        raise ValueError("Choose Random or Smart generation.")
    paths = library_paths(directory)
    if mode == "smart":
        if family not in PATCH_WORDS:
            raise ValueError("Choose a valid preset family.")
        paths = [path for path in paths if family in patch_families(path)]
        if not paths:
            raise ValueError(f"No {family} filenames matched. Choose another family or library.")
    parents = {}
    for path in paths:
        try:
            parents[path] = load_preset(path)
        except Exception as error:
            raise ValueError(f"Cannot load {path.name}: {error}") from error
    return parents


def destination(slot, key):
    module = parse_module(key)
    return (slot.get("destModuleTypeString") in destination_types(module.module_type)
            and slot.get("destModuleID") == module.index)


def identity(slot):
    return (tuple(slot.get("source", ())), slot.get("destModuleTypeString"),
            slot.get("destModuleID"), slot.get("destModuleParamID"))


def compose(base, parents, selections, rng, mutation=0, interpolation=0):
    if not 0 <= mutation <= 1 or not 0 <= interpolation <= 1:
        raise ValueError("Mutation and interpolation must be between 0% and 100%.")
    if any(key not in modules(base) or action not in {"generate", "modulations"}
           for key, action in selections.items()):
        raise ValueError("Unsupported module or generation action.")
    output, report, assignments = copy.deepcopy(base), [], {}
    for key in sorted(selections):
        candidates = [path for path, parent in parents.items() if key in parent["data"]]
        if not candidates:
            report.append(f"{key}: absent from donors; kept Init value.")
            continue
        path = rng.choice(candidates)
        assignments[key] = path
    participating = sorted(set(assignments.values()))
    for key, path in assignments.items():
        value = copy.deepcopy(parents[path]["data"][key])
        if interpolation:
            for sibling in participating:
                if sibling != path and key in parents[sibling]["data"]:
                    value = interpolate_node(value, parents[sibling]["data"][key], interpolation)
        output["data"][key] = mutate_node(value, mutation, rng)
        report.append(f"{key} ← {path.name}")

    labels, routes, unknown = source_labels(ASSETS), {}, set()
    sibling_slots = {
        path: {identity(slot): slot for name, slot in parents[path]["data"].items()
               if name.startswith("ModSlot") and isinstance(slot, dict)
               and isinstance(slot.get("plainParams"), dict)}
        for path in participating
    } if interpolation else {}
    for key, path in assignments.items():
        if selections[key] != "modulations":
            continue
        for slot_name, slot in parents[path]["data"].items():
            if not slot_name.startswith("ModSlot") or not isinstance(slot, dict) or not isinstance(slot.get("plainParams"), dict):
                continue
            source = labels.get(tuple(slot.get("source", ())))
            incoming = destination(slot, key)
            if source is None:
                unknown.add((path.name, str(slot.get("source"))))
            if not incoming and source != key:
                continue
            if any(action == "generate" and destination(slot, other) for other, action in selections.items()):
                continue
            route_id = identity(slot)
            if route_id not in routes:
                value = copy.deepcopy(slot)
                for sibling in participating if interpolation else []:
                    if sibling != path and route_id in sibling_slots[sibling]:
                        value = interpolate_node(value, sibling_slots[sibling][route_id], interpolation)
                routes[route_id] = value
    free = [key for key, value in output["data"].items() if key.startswith("ModSlot")
            and isinstance(value, dict) and value.get("plainParams") == "default"]
    if len(routes) > len(free):
        raise ValueError(f"Need {len(routes)} modulation slots; only {len(free)} are free.")
    for key, slot in zip(free, routes.values()):
        output["data"][key] = mutate_node(copy.deepcopy(slot), mutation, rng)
    report.append(f"Copied {len(routes)} complete modulation routes from the selected modules' donors.")
    if unknown:
        report.append(f"Unconfirmed: {len(unknown)} unlabeled source tuples; source-side matches cannot be inferred. "
                      "Destination-side routes are copied when matched.")
        report.extend(f"  {name}: source {raw}" for name, raw in sorted(unknown))
    if any(action == "modulations" for action in selections.values()):
        report.append("Modulation endpoints use existing instance IDs; unselected source modules retain Init settings.")
    if any(key.startswith("FXRack") and action == "modulations" for key, action in selections.items()):
        report.append("FXRack modulation destination mapping is unconfirmed; effect routes cannot be inferred.")
    if mutation:
        report.append("Float mutation uses stored values; unknown ranges/defaults are not inferred.")
    return output, report


def generate(directory, selections, mode="random", family="bass", count=1,
             mutation=0, interpolation=0, seed=None):
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError("Count must be a positive integer.")
    if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
        raise ValueError("Seed must be a whole number, or left blank.")
    parents = prepare_library(directory, mode, family)
    base, rng = load_preset(ASSETS / "Init.SerumPreset"), random.Random(seed)
    return [compose(base, parents, selections, rng, mutation, interpolation) for _ in range(count)]
