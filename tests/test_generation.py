"""Generation invariants tested with real exported Serum fixtures."""

import copy
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.generation import compose, destination, generate, identity
from backend.preset import load_preset
from backend.settings import ASSETS, read_settings, write_settings
from ui.bridge import Bridge

FIXTURES = Path(__file__).resolve().parents[3] / "testing/presets-for-tests"


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.base = load_preset(ASSETS / "Init.SerumPreset")
        shutil.copyfile(FIXTURES / "interpolationA.SerumPreset", self.folder / "BS - Test.SerumPreset")
        shutil.copyfile(FIXTURES / "interpolationB.SerumPreset", self.folder / "LD - Test.SerumPreset")

    def test_smart_uses_matching_donors_and_preserves_init(self):
        selection = {f"Oscillator{i}": "generate" for i in range(3)}
        [(output, report)] = generate(self.folder, selection, "smart", "bass", seed=7)
        donor = load_preset(self.folder / "BS - Test.SerumPreset")
        for key in selection:
            self.assertEqual(output["data"][key], donor["data"][key])
        for key in self.base["data"].keys() - selection.keys():
            self.assertEqual(output["data"][key], self.base["data"][key], key)
        self.assertTrue(all("BS - Test" in line for line in report if "←" in line))
        with self.assertRaisesRegex(ValueError, "No pluck filenames matched"):
            generate(self.folder, selection, "smart", "pluck")

    def test_seed_count_and_input_preservation(self):
        selection = {"Oscillator0": "generate", "Oscillator1": "generate"}
        a = generate(self.folder, selection, count=3, mutation=.3, interpolation=.5, seed=7)
        self.assertEqual(a, generate(self.folder, selection, count=3, mutation=.3, interpolation=.5, seed=7))
        self.assertEqual(len(a), 3)
        self.assertEqual(generate(self.folder, {}, seed=7)[0][0], self.base)

    def test_routes_follow_chosen_donor_only_and_are_atomic(self):
        parents = {path: load_preset(path) for path in [FIXTURES / "Init_mod_cutoff.SerumPreset",
                   FIXTURES / "Init_64_mod_mappings.SerumPreset"]}
        original = copy.deepcopy(parents)
        key = "VoiceFilter0"
        chosen = random.Random(3).choice(list(parents))
        output, _ = compose(self.base, parents, {key: "modulations"}, random.Random(3))
        expected = {identity(slot): slot for name, slot in parents[chosen]["data"].items()
                    if name.startswith("ModSlot") and isinstance(slot.get("plainParams"), dict)
                    and destination(slot, key)}
        actual = {identity(slot): slot for name, slot in output["data"].items()
                  if name.startswith("ModSlot") and isinstance(slot.get("plainParams"), dict)}
        self.assertEqual(actual, expected)
        self.assertTrue(actual)
        self.assertEqual(parents, original)
        plain, _ = compose(self.base, parents, {key: "generate"}, random.Random(3))
        self.assertTrue(all(plain["data"][k] == v for k, v in self.base["data"].items() if k.startswith("ModSlot")))

    def test_settings_and_dry_run_do_not_write_presets(self):
        with patch("backend.settings.CONFIG", self.folder / "settings.json"):
            self.assertFalse(read_settings()["valid"])
            self.assertTrue(write_settings(str(self.folder))["valid"])
            bridge = Bridge()
            options = dict(mode="smart", family="bass", count=2, mutation=0, interpolation=0, seed=4, dry_run=True)
            target = self.folder / "not-created"
            result = bridge.generate(str(target), {"Oscillator0": "generate"}, options)
            self.assertNotIn("error", result)
            self.assertFalse(target.exists())
            options["dry_run"] = False
            result = bridge.generate(str(target), {"Oscillator0": "generate"}, options)
            self.assertNotIn("error", result)
            self.assertEqual(len(list(target.glob("*.SerumPreset"))), 2)


if __name__ == "__main__":
    unittest.main()
