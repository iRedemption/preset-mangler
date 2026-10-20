"""UI-independent operations; each generation starts from the original preset."""

import copy
import random
from pathlib import Path

from .container import pack_in_memory, unpack_in_memory
from .mutation import mutate_node


def load_preset(path):
    path = Path(path).expanduser()
    if path.suffix.lower() != ".serumpreset":
        raise ValueError("Choose a .SerumPreset file.")
    return unpack_in_memory(path.read_bytes())


def mangle(preset, modules, amount, seed=None):
    """Modules are explicit paths of dictionary keys, allowing nested subtypes."""
    if not 0 <= amount <= 1:
        raise ValueError("Mutation amount must be between 0% and 100%.")
    paths = sorted(set(tuple(path) for path in modules))
    if any(path[:len(parent)] == parent for parent in paths for path in paths
           if parent != path):
        raise ValueError("Choose either a module or its nested module, not both.")
    output, rng, report = copy.deepcopy(preset), random.Random(seed), []
    for path in paths:
        if not path:
            raise ValueError("A module path cannot be empty.")
        node = output["data"]
        for key in path[:-1]:
            node = node[key]
        original = node[path[-1]]
        node[path[-1]] = mutate_node(original, amount, rng)
        report.append(f"{'.'.join(path)}: " + ("mutated" if node[path[-1]] != original
                                             else "no stored float values changed"))
    report.append("Existing floats varied by the selected percentage; parameter ranges "
                  "are unconfirmed. Defaults, enums, integers and modulation routes are preserved.")
    return output, report


def save_preset(preset, destination, source=None, overwrite=False):
    destination = Path(destination).expanduser()
    if destination.suffix.lower() != ".serumpreset":
        raise ValueError("Output filename must end in .SerumPreset.")
    if source and destination.resolve() == Path(source).expanduser().resolve():
        raise ValueError("Choose a different output path to preserve the source preset.")
    payload = pack_in_memory(preset)
    with destination.open("wb" if overwrite else "xb") as stream:
        stream.write(payload)
    return destination
