"""Run a saved HyProC simulation without starting its desktop interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import periodictable

from . import calc_broadening, calc_curve, calc_stopping
from .simulation_io import make_target, validate_physics, validate_temperature


@dataclass
class SimulationResult:
    energy: list[float]
    yield_values: list[float]
    normalization_factor: float
    standard_stopping: float | None


def energy_values(minimum: float, maximum: float, step_size: float) -> list[float]:
    if not all(np.isfinite(value) for value in (minimum, maximum, step_size)):
        raise ValueError("The energy range and step size must be finite.")
    if minimum > maximum or step_size <= 0:
        raise ValueError("The energy range must be ordered and the step size positive.")
    interval_count = (maximum - minimum) / step_size
    if not np.isfinite(interval_count):
        raise ValueError("The energy range and step size produce too many calculation points.")
    energies = [minimum + index * step_size for index in range(int(np.floor(interval_count)) + 1)]
    if np.isclose(energies[-1], maximum, rtol=1e-12, atol=1e-12):
        energies[-1] = maximum
    else:
        energies.append(maximum)
    return energies


def saved_energy_values(simulation: dict) -> list[float]:
    saved = simulation["simulated_curve"]["energy"] or simulation["experimental_curve"]["energy"]
    if saved:
        return list(saved)
    grid = simulation["energy_range"]
    minimum, maximum = grid["minimum"], grid["maximum"]
    if minimum is None or maximum is None:
        raise ValueError("The simulation has no saved energy grid or complete energy range.")
    step = grid.get("step_size")
    if step is None:
        points = grid.get("points")
        step = (maximum - minimum) / (points - 1) if isinstance(points, int) and points > 1 else 1.0
    return energy_values(minimum, maximum, step)


def projectile_arguments(reaction: dict, srim_path: str) -> dict:
    z, a = int(reaction["Z1"]), int(reaction["A1"])
    return {"Z1": z, "M1": periodictable.elements[z][a].mass, "srim_path": srim_path}


def simulate(simulation: dict, *, srim_path: str = "") -> SimulationResult:
    """Calculate a curve from a version 1 simulation without modifying its inputs."""
    return _simulate(simulation, srim_path=srim_path)


def _simulate(
    simulation: dict,
    *,
    srim_path: str,
    incident_energies: list[float] | None = None,
    diagnostic_path: Callable[[int, float], Path] | None = None,
) -> SimulationResult:
    reaction, resonance = validate_physics(simulation["reaction"], simulation["resonance"])
    options = simulation["options"]
    offset = float(options["offset"] or 0)
    beam_width = float(options["beam_width"])
    if not np.isfinite(offset) or not np.isfinite(beam_width):
        raise ValueError("The energy offset and beam width must be finite.")
    if incident_energies is None:
        incident_energies = [energy - offset for energy in saved_energy_values(simulation)]
    if not incident_energies or not all(np.isfinite(energy) for energy in incident_energies):
        raise ValueError("The simulation must contain finite incident energies.")

    z2 = int(reaction["Z2"])
    projectile = projectile_arguments(reaction, srim_path)
    target_temperature = validate_temperature(options.get("target_temperature", "20"), "Target")
    target_mass = periodictable.elements[int(reaction["Z2"])][int(reaction["A2"])].mass
    stopping_model = options.get("stopping_model", "SRIM")
    straggling_model = options["straggling_model"]
    if straggling_model not in {"None", "Rud", "Rud corr", "Bohr"}:
        raise ValueError(f"Unsupported straggling model: {straggling_model}.")
    broadening_arguments = {
        "E_R": resonance["E_R"],
        "Gamma": resonance["Gamma"],
        "sigma_R": resonance["Sigma"],
        "Z1": projectile["Z1"],
        "projectile_mass": projectile["M1"],
        "target_mass": target_mass,
        "off_resonance": resonance["Off-resonance"],
    }

    manual_k = options.get("manual_k_factor", "").strip()
    standard_stopping = None
    if manual_k:
        normalization = float(manual_k)
        if not np.isfinite(normalization) or normalization <= 0:
            raise ValueError("Manual K factor must be finite and greater than zero.")
    else:
        standard_temperature = validate_temperature(options.get("standard_temperature", "20"), "Standard")
        standard = make_target(simulation["standard"])
        layer = standard["layers"][0]
        if not layer.find_element(z2):
            raise ValueError("The standard does not contain the reacting target element.")
        layer.normalize()
        standard_energy = resonance["E_R"] + 100 * resonance["Gamma"]
        standard_stopping = calc_stopping.calc_stopping_cross_section(
            layer, standard_energy, stopping_model, **projectile
        )
        layer["stopping"] = standard_stopping
        _, x, y, _, _ = calc_broadening.broadening(
            standard_energy, standard, beam_width, options["doppler"], straggling_model,
            temperature_c=standard_temperature, **broadening_arguments,
        )
        standard_integral = calc_curve.compute_yield(standard, x, y, z2, resonance["Off-resonance"])
        if not np.isfinite(standard_integral) or standard_integral == 0:
            raise ValueError(f"Standard yield integral is invalid ({standard_integral}).")
        normalization = float(options["standard_yield"]) / standard_integral
        if not np.isfinite(normalization):
            raise ValueError("Standard yield must be finite.")

    target = make_target(simulation["target"])
    target.normalize_all_layers()
    target = calc_stopping.assign_stopping(target, min(incident_energies), stopping_model, **projectile)
    yields = []
    for index, energy in enumerate(incident_energies):
        path = diagnostic_path(index, energy) if diagnostic_path is not None else None
        _, x, y, _, _ = calc_broadening.broadening(
            energy, target, beam_width, options["doppler"], straggling_model,
            saveData=path is not None, savepath=str(path) if path is not None else None,
            temperature_c=target_temperature, **broadening_arguments,
        )
        yields.append(float(normalization * calc_curve.compute_yield(target, x, y, z2, resonance["Off-resonance"])))
    return SimulationResult([energy + offset for energy in incident_energies], yields, normalization, standard_stopping)
