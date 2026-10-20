"""Stats aggregation over a temporary library built from the bundled Init preset."""

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backend.settings as settings
from backend import stats


class StatsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.library = root / "library"
        self.library.mkdir()
        self.original_config = settings.CONFIG
        settings.CONFIG = root / "settings.json"
        init = settings.ASSETS / "Init.SerumPreset"
        shutil.copy(init, self.library / "Bass One.SerumPreset")
        shutil.copy(init, self.library / "Lead Copy.SerumPreset")
        shutil.copy(init, self.library / "Unnamed.SerumPreset")

    def tearDown(self):
        settings.CONFIG = self.original_config
        self.temporary.cleanup()

    def test_build_counts_and_caches(self):
        payload = stats.build(self.library)
        self.assertEqual(payload["count"], 3)
        self.assertEqual(payload["duplicates"], 2)
        self.assertEqual(payload["with_mods"], 0)
        self.assertIn(["bass", 1], payload["categories"])
        self.assertTrue(settings.CONFIG.with_name("stats-cache.json").exists())
        again = stats.build(self.library)
        self.assertEqual(again["count"], payload["count"])

    def test_empty_library_is_an_error(self):
        empty = self.library.parent / "empty"
        empty.mkdir()
        with self.assertRaises(ValueError):
            stats.build(empty)


if __name__ == "__main__":
    unittest.main()
