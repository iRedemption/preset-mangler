"""Preservation checks using real Serum-exported repository fixtures."""

import copy
from pathlib import Path
import random
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.container import pack_in_memory, unpack_in_memory
from backend.mutation import mutate_node
from backend.preset import load_preset, mangle, save_preset


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.source = Path(__file__).resolve().parents[3] / "testing/presets-for-tests/interpolationA.SerumPreset"
        self.preset = load_preset(self.source)

    def test_scoped_mutation_preserves_source_and_siblings(self):
        original = copy.deepcopy(self.preset)
        output, _ = mangle(self.preset, [("Oscillator0",)], .3, seed=7)
        self.assertEqual(self.preset, original)
        self.assertNotEqual(output["data"]["Oscillator0"], original["data"]["Oscillator0"])
        for key in original["data"].keys() - {"Oscillator0"}:
            self.assertEqual(output["data"][key], original["data"][key], key)
        self.assertEqual(unpack_in_memory(pack_in_memory(output)), output)

    def test_keep_and_zero(self):
        self.assertEqual(mangle(self.preset, [], 1)[0], self.preset)
        self.assertEqual(mangle(self.preset, [("LFO0",)], 0)[0], self.preset)

    def test_types_and_percentage(self):
        node = [True, 12, "default", b"opaque", 0.0, 10.0, -10.0]
        result = mutate_node(node, .3, random.Random(7))
        self.assertEqual(result[:5], node[:5])
        self.assertTrue(7 <= result[5] <= 13)
        self.assertTrue(-13 <= result[6] <= -7)

    def test_export_protects_source_and_existing_files(self):
        with self.assertRaises(ValueError):
            save_preset(self.preset, self.source, self.source)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.SerumPreset"
            save_preset(self.preset, path)
            self.assertEqual(load_preset(path), self.preset)
            with self.assertRaises(FileExistsError):
                save_preset(self.preset, path)

    def test_reject_invalid_and_overlapping_selections(self):
        with self.assertRaises(ValueError):
            unpack_in_memory(b"not a preset")
        with self.assertRaises(ValueError):
            mangle(self.preset, [("Oscillator0",), ("Oscillator0", "WTOsc0")], .3)
        with self.assertRaises(ValueError):
            mangle(self.preset, [], 1.1)


if __name__ == "__main__":
    unittest.main()
