"""Generation invariants tested with real exported Serum fixtures."""

import base64
import copy
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.generation import compose, destination, generate, identity, prepare_library
from backend.generator.families import FAMILIES
from backend.generator.selection import patch_families
from backend.preset import load_preset
from backend.settings import (ASSETS, read_settings, write_output_directory,
                              write_safety_limiter, write_settings)
from ui.bridge import Bridge

FIXTURES = Path(__file__).resolve().parents[1] / "testing/presets-for-tests"
if not FIXTURES.is_dir():
    FIXTURES = Path(__file__).resolve().parents[2] / "serum-preset-mutator/testing/presets-for-tests"


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
        limiter = load_preset(ASSETS / "Init_Safety_Limiter.SerumPreset")["data"]["FXRack0"]["FX"][0]
        for key in selection:
            self.assertEqual(output["data"][key], donor["data"][key])
        for key in self.base["data"].keys() - selection.keys():
            if key == "FXRack0":
                self.assertEqual(output["data"][key]["FX"],
                                 self.base["data"][key]["FX"] + [limiter])
                continue
            self.assertEqual(output["data"][key], self.base["data"][key], key)
        self.assertTrue(all("BS - Test" in line for line in report if "←" in line))
        with self.assertRaisesRegex(ValueError, "No pluck filenames matched"):
            generate(self.folder, selection, "smart", "pluck")

    def test_family_mapping_adds_filename_classification_and_filtering(self):
        ambient = self.folder / "ambient - Test.SerumPreset"
        shutil.copyfile(FIXTURES / "interpolationA.SerumPreset", ambient)
        with patch.dict(FAMILIES, {
            "ambient": {"words": ("ambient",), "abbreviations": ("amb",)}
        }):
            self.assertEqual(patch_families(ambient), {"ambient"})
            self.assertEqual(
                [path.name for path in prepare_library(self.folder, "smart", "ambient")],
                [ambient.name],
            )

    def test_seed_count_and_input_preservation(self):
        selection = {"Oscillator0": "generate", "Oscillator1": "generate"}
        a = generate(self.folder, selection, count=3, mutation=.3, interpolation=.5, seed=7)
        self.assertEqual(a, generate(self.folder, selection, count=3, mutation=.3, interpolation=.5, seed=7))
        self.assertEqual(len(a), 3)
        self.assertEqual(generate(self.folder, {}, seed=7, safety_limiter=False)[0][0], self.base)

    def test_custom_base_and_single_donor(self):
        base_path = FIXTURES / "Init_mod_cutoff.SerumPreset"
        donor_path = self.folder / "LD - Test.SerumPreset"
        base, donor = load_preset(base_path), load_preset(donor_path)
        original_base = copy.deepcopy(base)
        [(output, report)] = generate(
            self.folder, {"Oscillator0": "generate"}, base_path=base_path,
            donor_path=donor_path, seed=7)
        self.assertEqual(output["data"]["Oscillator0"], donor["data"]["Oscillator0"])
        for key, value in base["data"].items():
            if key == "FXRack0":
                limiter = load_preset(ASSETS / "Init_Safety_Limiter.SerumPreset")["data"]["FXRack0"]["FX"][0]
                self.assertEqual(output["data"][key]["FX"], value["FX"] + [limiter])
            elif key != "Oscillator0":
                self.assertEqual(output["data"][key], value, key)
        self.assertEqual(base, original_base)
        self.assertIn(f"Base: {base_path.name}", report)
        self.assertTrue(any(f"Oscillator0 ← {donor_path.name}" in line for line in report))

    def test_macro_generation_adds_missing_macro_modules_only(self):
        base = copy.deepcopy(self.base)
        macro_keys = [key for key in self.base["data"] if key.startswith("Macro")]
        for key in macro_keys:
            del base["data"][key]
        donor_path = FIXTURES / "interpolationA.SerumPreset"
        donor = load_preset(donor_path)
        selections = {key: "generate" for key in macro_keys}

        output, report = compose(
            base, {donor_path: donor}, selections, random.Random(2), safety_limiter=False)

        self.assertEqual(set(output["data"]) - set(base["data"]), set(macro_keys))
        for key in macro_keys:
            self.assertEqual(output["data"][key], donor["data"][key])
        for key, value in base["data"].items():
            self.assertEqual(output["data"][key], value, key)
        self.assertTrue(any("Copied 0 complete modulation routes" in line for line in report))
        unchanged, missing_report = compose(
            base, {}, selections, random.Random(2), safety_limiter=False)
        self.assertEqual(unchanged, base)
        self.assertTrue(any("Macro0: absent from donors; no module added." in line
                            for line in missing_report))
        with self.assertRaisesRegex(ValueError, "Unsupported module"):
            compose(base, {donor_path: donor}, {"Macro99": "generate"}, random.Random(2),
                    safety_limiter=False)

    def test_in_memory_base_and_protects_dropped_source(self):
        base_path = FIXTURES / "Init_mod_cutoff.SerumPreset"
        base = load_preset(base_path)
        [(output, report)] = generate(
            self.folder, {"Oscillator0": "generate"}, donor_path=self.folder / "LD - Test.SerumPreset",
            base_preset=base, base_name=base_path.name, seed=7)
        self.assertEqual(output["data"]["Oscillator1"], base["data"]["Oscillator1"])
        self.assertIn(f"Base: {base_path.name}", report)

        with patch("backend.settings.CONFIG", self.folder / "settings.json"):
            write_settings(str(self.folder))
            bridge = Bridge()
            inspected = bridge.inspect_preset(
                encoded=base64.b64encode(base_path.read_bytes()).decode(),
                name=base_path.name)
            self.assertNotIn("error", inspected)
            output_folder = self.folder / "outputs"
            output_folder.mkdir()
            destination = output_folder / "generated_custom_001.SerumPreset"
            shutil.copyfile(base_path, destination)
            options = dict(mode="random", family="random", count=1, mutation=0,
                           interpolation=0, base_token=inspected["token"],
                           donor_path=str(self.folder / "LD - Test.SerumPreset"))
            result = bridge.generate(str(output_folder), {"Oscillator0": "generate"}, options)
            self.assertIn("error", result)
            self.assertIn("overwrite the dropped base preset", result["error"])

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

    def test_safety_limiter_appends_after_existing_effect_and_can_be_disabled(self):
        limiter = load_preset(ASSETS / "Init_Safety_Limiter.SerumPreset")["data"]["FXRack0"]["FX"][0]
        base = copy.deepcopy(self.base)
        base["data"]["FXRack0"]["FX"].append(copy.deepcopy(limiter))
        original = copy.deepcopy(base)

        output, report = compose(base, {}, {}, random.Random(1))
        self.assertEqual(output["data"]["FXRack0"]["FX"], [limiter, limiter])
        self.assertEqual(base, original)
        self.assertTrue(any("after 1 existing effect(s)" in line for line in report))

        unchanged, report = compose(base, {}, {}, random.Random(1), safety_limiter=False)
        self.assertEqual(unchanged, base)
        self.assertTrue(any("disabled in Settings" in line for line in report))

    def test_settings_and_dry_run_do_not_write_presets(self):
        with patch("backend.settings.CONFIG", self.folder / "settings.json"):
            self.assertFalse(read_settings()["valid"])
            self.assertTrue(read_settings()["safety_limiter"])
            self.assertTrue(write_settings(str(self.folder))["valid"])
            settings = write_safety_limiter(False)
            self.assertFalse(settings["safety_limiter"])
            self.assertFalse(write_settings(str(self.folder))["safety_limiter"])
            self.assertFalse(write_output_directory(str(self.folder))["safety_limiter"])
            write_safety_limiter(True)
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

    def test_default_output_directory_is_saved_and_used_for_mutation(self):
        with patch("backend.settings.CONFIG", self.folder / "settings.json"):
            write_settings(str(self.folder))
            output_directory = self.folder / "default-output"
            output_directory.mkdir()
            settings = write_output_directory(str(output_directory))
            self.assertEqual(settings["output_directory"], str(output_directory.resolve()))
            self.assertEqual(settings["library"], str(self.folder.resolve()))
            loaded = Bridge().load(str(FIXTURES / "interpolationA.SerumPreset"))
            self.assertEqual(Path(loaded["output"]).parent, output_directory.resolve())
            write_output_directory("")
            loaded = Bridge().load(str(FIXTURES / "interpolationA.SerumPreset"))
            self.assertEqual(Path(loaded["output"]).parent, (FIXTURES / "interpolationA.SerumPreset").parent)

    def test_specific_donor_needs_no_library_and_protects_custom_base(self):
        donor = self.folder / "LD - Test.SerumPreset"
        shutil.copyfile(FIXTURES / "interpolationB.SerumPreset", donor)
        base = self.folder / "generated_custom_001.SerumPreset"
        shutil.copyfile(FIXTURES / "interpolationA.SerumPreset", base)
        with patch("backend.settings.CONFIG", self.folder / "missing-settings.json"):
            bridge = Bridge()
            options = dict(mode="random", family="random", count=1, mutation=0,
                           interpolation=0, seed=4, dry_run=False,
                           base_path=str(base), donor_path=str(donor))
            result = bridge.generate(str(self.folder), {"Oscillator0": "generate"}, options)
            self.assertIn("error", result)
            self.assertIn("overwrite a base, donor, or library preset", result["error"])
            self.assertEqual(load_preset(base), load_preset(FIXTURES / "interpolationA.SerumPreset"))


if __name__ == "__main__":
    unittest.main()
