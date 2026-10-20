"""Desktop bridge behavior tested without opening the native file manager."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui.bridge import Bridge


class RevealTests(unittest.TestCase):
    def test_reveals_file_in_windows_explorer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.SerumPreset"
            path.touch()
            with patch("ui.bridge.sys.platform", "win32"), patch("ui.bridge.subprocess.Popen") as popen:
                result = Bridge().reveal(str(path))
            self.assertEqual(result, {"success": True})
            popen.assert_called_once_with(["explorer", f"/select,{path.resolve()}"])

    def test_opens_directory_in_windows_explorer(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("ui.bridge.sys.platform", "win32"), \
                    patch("ui.bridge.os.startfile", create=True) as startfile:
                result = Bridge().reveal(directory)
            self.assertEqual(result, {"success": True})
            startfile.assert_called_once_with(str(Path(directory).resolve()))

    def test_reports_missing_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing" / "preset.SerumPreset"
            result = Bridge().reveal(str(missing))
            self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
