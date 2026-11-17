"""Launch the HyProC desktop app from a source checkout."""

from pathlib import Path
import sys


def main() -> None:
    checkout = Path(__file__).resolve().parent
    sys.path.insert(0, str(checkout / "src"))
    from hyproc.UI import main as open_desktop

    open_desktop(settings_path=checkout / "settings.json")


if __name__ == "__main__":
    main()
