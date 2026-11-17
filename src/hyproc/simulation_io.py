"""Read and write the desktop application's version 1 simulation format."""

import copy
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
import periodictable

from .class_models import Layer, Target


def load_simulation(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as source:
        data = json.load(source)
    if not isinstance(data, dict):
        raise ValueError("The simulation file must contain a JSON object.")
    if data.get("format") != "HyProC simulation" or data.get("version") != 1:
        raise ValueError("This file is not a supported HyProC simulation.")
    return data


def save_simulation(path: str | Path, simulation: dict) -> None:
    path = Path(path)
    temporary_path = None
    try:
        with NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as destination:
            temporary_path = Path(destination.name)
            json.dump(simulation, destination, indent=4, allow_nan=False)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def make_target(data: dict) -> Target:
    layers = data["layers"]
    if not isinstance(layers, list) or not layers:
        raise ValueError("A target or standard must contain a nonempty layer list.")
    target = Target()
    target.update(copy.deepcopy(data))
    target["layers"] = [Layer(layer) for layer in target["layers"]]
    return target


def validate_physics(
    reaction: object,
    resonance: object,
)->tuple[dict[str, str], dict[str, float]]:
    if not isinstance(reaction, dict) or not isinstance(resonance, dict):
        raise ValueError("Saved reaction and resonance settings must be JSON objects.")

    reaction_values: dict[str, str] = {}
    for key in ("Z1", "A1", "Z2", "A2"):
        value = reaction.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValueError(f"Saved reaction value {key} must be an integer.")
        try:
            int_value = int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Saved reaction value {key} must be an integer.") from exc
        if str(int_value) != str(value).strip():
            raise ValueError(f"Saved reaction value {key} must be an integer.")
        reaction_values[key] = str(int_value)

    for z_key, a_key in (("Z1", "A1"), ("Z2", "A2")):
        z_value = int(reaction_values[z_key])
        a_value = int(reaction_values[a_key])
        if not 1 <= z_value <= 118 or a_value <= 0:
            raise ValueError(f"Saved {z_key} must be between 1 and 118 and {a_key} must be positive.")
        isotope_mass = periodictable.elements[z_value][a_value].mass
        if isotope_mass is None or not np.isfinite(float(isotope_mass)):
            raise ValueError(f"No isotope mass is available for {z_key}={z_value}, {a_key}={a_value}.")

    resonance_values: dict[str, float] = {}
    for key in ("E_R", "Gamma", "Sigma"):
        try:
            value = float(resonance[key])
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Saved resonance value {key} must be numeric.") from exc
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"Saved resonance value {key} must be finite and greater than zero.")
        resonance_values[key] = value
    return reaction_values, resonance_values

