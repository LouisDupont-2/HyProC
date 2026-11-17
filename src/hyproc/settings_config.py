"""Create machine-local settings from the shared, portable template."""

import os
from pathlib import Path


def ensure_settings(settings_path=None):
    """Return the settings path, creating it only when it does not exist."""
    if settings_path is None:
        config_home = os.getenv("APPDATA") if os.name == "nt" else os.getenv("XDG_CONFIG_HOME")
        directory = Path(config_home) if config_home else Path.home() / ".config"
        path = directory / "HyProC" / "settings.json"
    else:
        path = Path(settings_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        template = Path(__file__).with_name("settings.example.json").read_text(encoding="utf-8")
        try:
            with path.open("x", encoding="utf-8") as destination:
                destination.write(template)
        except FileExistsError:
            pass  # Another startup already created the local settings.
    return str(path)
