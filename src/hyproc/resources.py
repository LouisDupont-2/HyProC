"""Locate files supplied by the source checkout or the installed wheel."""

from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path


def find_resource(relative_path: str) -> Path | None:
    source = Path(__file__).resolve().parents[2] / relative_path
    if source.is_file():
        return source
    try:
        package = distribution("HyProC")
    except PackageNotFoundError:
        return None
    for entry in package.files or ():
        if entry.parts[-3:] == ("share", "hyproc", source.name):
            installed = Path(package.locate_file(entry)).resolve()
            if installed.is_file():
                return installed
    return None
