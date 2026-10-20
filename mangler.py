"""Launch Preset Mangler: python mangler.py [source.SerumPreset]."""

from pathlib import Path
import sys


def main():
    try:
        import webview
        from ui.bridge import Bridge
        from ui.assets import application
    except ImportError as error:
        raise SystemExit(f"Missing dependency: {error.name}. Run python -m pip install -r "
                         f'"{Path(__file__).with_name("requirements.txt")}"') from error
    api = Bridge(sys.argv[1] if len(sys.argv) > 1 else "")
    api._window = webview.create_window("Preset Mangler", application(),
                                      js_api=api, width=1220, height=820, min_size=(760, 500))
    webview.start()


if __name__ == "__main__":
    main()
