"""Create machine-local settings from the shared, portable template."""

from pathlib import Path


def ensure_settings(settings_path=None):
    """Return the settings path, creating it only when it does not exist."""
    path = Path(settings_path) if settings_path is not None else Path(__file__).with_name("settings.json")
    if not path.exists():
        template = Path(__file__).with_name("settings.example.json").read_text(encoding="utf-8")
        try:
            with path.open("x", encoding="utf-8") as destination:
                destination.write(template)
        except FileExistsError:
            pass  # Another startup already created the local settings.
    return str(path)
