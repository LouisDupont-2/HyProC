"""Launch the HyProC desktop app from a source checkout."""

from pathlib import Path
import sys


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from hyproc.UI import main as open_desktop

    open_desktop()


if __name__ == "__main__":
    main()
