"""Serve only bundled interface files and screenshots through pywebview."""

from pathlib import Path
from bottle import Bottle, static_file


def application():
    app, root = Bottle(), Path(__file__).resolve().parent.parent
    app.get("/")(lambda: static_file("index.html", root=root / "ui"))
    for folder in ("ui", "assets"):
        app.get(f"/{folder}/<path:path>")(
            lambda path, folder=folder: static_file(path, root=root / folder))
    return app
