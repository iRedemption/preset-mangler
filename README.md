# Preset Mangler

A desktop tool for mutating, generating, and inspecting Serum 2 `.SerumPreset` files.

## Features

| Feature | Description |
| ------- | ----------- |
| [Mutate](./docs/mutate.md) | Randomly perturb values in an existing preset |
| [Generate](./docs/generate.md) | Build on Init or a chosen preset; optionally append a safety limiter |
| [Stats](./docs/stats.md) | Charts and summaries of your preset library |
| [Settings](./docs/settings.md) | Set your preset library, default output folder, and generation limiter |

## Quick start

Requires Python 3.10 or newer. Check with `python --version` (Windows) or `python3 --version` (macOS).

**Install Python if needed:**

Windows (PowerShell):
```powershell
winget install -e --id Python.Python.3.12
```

macOS (Homebrew):
```bash
brew install python
```

Or download the installer from [python.org](https://www.python.org/downloads/).

**1. Get the code** (skip if you downloaded a ZIP instead):

```bash
git clone https://github.com/iRedemption/serum-preset-mutator.git
cd serum-preset-mutator/src/preset-mangler
```

**2. Create a virtual environment and install dependencies:**

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

**3. Launch:**

Windows:
```powershell
.\.venv\Scripts\python.exe mangler.py
```

macOS:
```bash
python3 mangler.py
```

On Windows, the window uses Microsoft Edge WebView2, which is installed on most systems. On macOS, it uses the built-in WebKit.

Use the folder button beside a path field to reveal its file or containing folder in Explorer, Finder, or the system file manager.

In Generate mode, drag a `.SerumPreset` onto the window to use it as the base preset. In Mutate mode, a dropped preset is loaded as the source.
