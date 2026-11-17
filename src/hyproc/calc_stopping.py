import os
import subprocess
import periodictable
import json
import copy
import math
from functools import lru_cache
from typing import Literal

from .class_models import Layer, Target
from pathlib import Path
from threading import Lock

script_dir = os.path.dirname(os.path.abspath(__file__))
_srim_lock = Lock()

# Stopping cross section variation allowed within a layer (in %)
percentage = 0.5

def check_srim_path(settings_path: str) -> bool:
    with open(settings_path, 'r', encoding="utf-8") as f:
        path = json.load(f)["SRIM_path"]
    return bool(path.strip()) and os.path.isdir(os.path.join(path, "SR Module"))

# Writing input file for SRIM
def write_input(layer: Layer, energy: float, Z1: int, M1: float, srim_directory: Path)->None:
    """
    Writes the SR.IN input file that SRIM uses to calculate the stopping cross section of a given layer.

    Parameters:
        layer (Layer) : layer of a given target.
        energy (float) : Energy (in keV) at which the stopping cross section is going to be calculated.

    Returns
    -------
        None
    """
    file_path = srim_directory / "SR.IN"

    # Delete existing file if it exists
    #if os.path.isfile(file_path):
    #    os.remove(file_path)

    # Precompute element data
    element_data = []
    total_density = 0.0
    for element in layer["elements"]:
        Z = element["Z"]
        percent_at = element["percent_at"]
        el = periodictable.elements[Z]
        name = el.name
        mass = el.mass
        density = el.density

        element_data.append({
            "Z": Z,
            "name": name,
            "percent_at": percent_at,
            "mass": mass
        })

        total_density += density * percent_at/100

    # Write the input file
    with open(file_path, 'w') as file:
        file.write("---Stopping/Range Input Data (Number-format: Period = Decimal Point) \n")
        file.write("---Output File Name\n")
        file.write('"Output"\n')
        file.write("---Ion(Z), Ion Mass(u)\n")
        file.write(f"{Z1}   {M1}\n")
        file.write("---Target Data: (Solid=0,Gas=1), Density(g/cm3), Compound Corr.\n")
        file.write(f"0   {total_density:.4f}    0\n")
        file.write("---Number of Target Elements \n")
        file.write(f"{len(element_data)}\n")
        file.write("---Target Elements: (Z), Target name, Stoich, Target Mass(u) \n")
        for el in element_data:
            file.write(f'{el["Z"]}   "{el["name"]}"   {el["percent_at"]}    {el["mass"]}\n')
        file.write("---Output Stopping Units (1-8) \n")
        file.write("7 \n")  # So the unit is eV/TFU
        file.write("---Ion Energy : E-Min(keV), E-Max(keV) \n")
        file.write("0   0 \n")
        file.write(f"{energy}")

# Reading output file from SRIM
def read_SRIM_stopping_cross_section(srim_directory: Path)-> float:
    """
    Reads the output file from SRIM.

    Parameters
    ----------
        None

    Returns
    -------
        S (float): Stopping cross section in keV/TFU (both electronic and nuclear)
    """
    with open(srim_directory / "Output", 'r') as f: # Output is the file name!!
        lines = f.readlines()
        
    # Find the line containing "Stopping Units"
    for idx, line in enumerate(lines):
        if "Stopping Units =  eV/(1E15 atoms/cm2)" in line:
            target_line_index = idx + 2  # Go two lines down
            break
    else:
        raise ValueError('"Stopping Units" not found in file.')

    # Extract the line and parse values
    target_line = lines[target_line_index].strip()
    parts = target_line.split()
    
    if len(parts) < 3:
        raise ValueError("The data line doesn't have enough columns.")

    try:
        s_elec = float(parts[1])
        s_nuc = float(parts[2])
    except ValueError:
        raise ValueError("Non-numeric values found in expected columns.")

    return s_elec + s_nuc

@lru_cache(maxsize=1)
def _load_dk_parameters() -> list[list[dict | None]]:
    parameter_path = os.path.join(script_dir, "data", "SCS-2025-solid.json")
    with open(parameter_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["parameters"]


def _scs_stopping_cross_section(z2: int, energy_per_u: float, Z1: int) -> float:
    """Return the SCS-25-Solid electronic stopping cross section in 10^-15 eV cm^2 (eV/TFU)."""
    try:
        entry = _load_dk_parameters()[Z1][z2]
    except (IndexError, TypeError) as exc:
        raise ValueError(f"No SCS stopping parameters are available for Z1={Z1}, Z2={z2}.") from exc
    if entry is None:
        raise ValueError(f"No SCS stopping parameters are available for Z1={Z1}, Z2={z2}.")

    f1, s, p, a0, a1, a2, a3, f2, q, r, b0, b1, b2, b3 = entry["params"]
    x = energy_per_u
    try:
        term_a = f1 * x**s * math.log(math.e + p * x) / (
            a0 + a1 * x**0.25 + a2 * x**0.5 + a3 * x ** (1 + s)
        )
        term_b = f2 * x**q * math.log(math.e + r * x) / (
            b0 + b1 * x**0.25 + b2 * x**0.5 + b3 * x ** (1 + q)
        )
        stopping_cross_section = term_a + term_b
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"Could not evaluate the SCS-25-Solid stopping model for Z1={Z1}, Z2={z2}.") from exc
    if not math.isfinite(stopping_cross_section):
        raise ValueError(f"The SCS-25-Solid stopping model returned a non-finite value for Z1={Z1}, Z2={z2}.")
    return stopping_cross_section


def _ziegler_nuclear_stopping_cross_section(z2: int, energy: float, Z1: int, M1: float) -> float:
    """Return the universal nuclear stopping cross section in eV/TFU."""
    target_mass = periodictable.elements[z2].mass
    if not math.isfinite(M1) or M1 <= 0 or not math.isfinite(target_mass) or target_mass <= 0:
        raise ValueError(f"Invalid projectile or target mass for Z1={Z1}, Z2={z2}.")

    reduced_energy = (
        32.53 * target_mass * energy
        / (
            Z1 * z2 * (M1 + target_mass)
            * (Z1**0.23 + z2**0.23)
        )
    )
    reduced_stopping = math.log1p(1.1383 * reduced_energy) / (
        2 * (
            reduced_energy
            + 0.01321 * reduced_energy**0.21226
            + 0.19593 * math.sqrt(reduced_energy)
        )
    )
    return (
        8.462 * Z1 * z2 * M1 * reduced_stopping
        / ((M1 + target_mass) * (Z1**0.23 + z2**0.23))
    )


def _calc_scs_stopping_components(layer: Layer, energy: float, Z1: int, M1: float) -> tuple[float, float]:
    """Return Bragg-weighted electronic and nuclear SCS stopping in keV/TFU."""
    if not math.isfinite(energy) or energy < 0:
        raise ValueError("SCS-25-Solid stopping cross section requires a finite, non-negative energy in keV.")
    if energy == 0:
        return 0.0, 0.0
    if not math.isfinite(M1) or M1 <= 0:
        raise ValueError("The incident-particle mass M1 must be positive for the SCS-25-Solid model.")

    energy_per_u = energy / (1000.0 * M1)
    elements = layer.get("elements", [])
    total_percent = sum(float(element["percent_at"]) for element in elements)
    if not elements or not math.isfinite(total_percent) or total_percent <= 0:
        raise ValueError("The layer must contain elements with a positive total atomic percentage.")

    electronic_stopping_cross_section = 0.0
    nuclear_stopping_cross_section = 0.0
    for element in elements:
        atomic_percent = float(element["percent_at"])
        if not math.isfinite(atomic_percent) or atomic_percent < 0:
            raise ValueError("Layer atomic percentages must be finite and non-negative.")
        z2_value = element["Z"]
        z2 = int(z2_value)
        if z2 < 1 or z2 != z2_value:
            raise ValueError(f"Invalid target atomic number for the SCS-25-Solid model: {z2_value}.")
        atomic_fraction = atomic_percent / total_percent
        electronic_stopping_cross_section += (
            atomic_fraction * _scs_stopping_cross_section(z2, energy_per_u, Z1)
        )
        nuclear_stopping_cross_section += (
            atomic_fraction * _ziegler_nuclear_stopping_cross_section(z2, energy, Z1, M1)
        )

    # Both Bragg-weighted components are in eV/TFU.
    return electronic_stopping_cross_section / 1000.0, nuclear_stopping_cross_section / 1000.0


def _calc_scs_stopping_cross_section(layer: Layer, energy: float, Z1: int, M1: float) -> float:
    electronic_stopping, nuclear_stopping = _calc_scs_stopping_components(layer, energy, Z1, M1)
    return electronic_stopping + nuclear_stopping


def calc_stopping_cross_section(layer: Layer, energy: float, model: Literal["SRIM", "SCS-25-Solid"], *, Z1: int, M1: float, srim_path: str = "") -> float:
    """
    Computes the stopping cross section of a given layer at a certain energy.

    Parameters:
        layer (Layer) : layer of a given target.
        energy (float) : Energy (in keV) at which the stopping cross section is going to be calculated.
        model (str) : "SRIM" or "SCS-25-Solid" (electronic plus Ziegler nuclear).

    Returns:
        S (float) : Stopping cross section in keV/TFU
    """
    if model == "SCS-25-Solid":
        return _calc_scs_stopping_cross_section(layer, energy, Z1, M1)
    if model != "SRIM":
        raise ValueError(f"Unsupported stopping-cross-section model: {model}")

    if not srim_path:
        raise ValueError("Provide a valid SRIM installation path.")
    srim_directory = (Path(srim_path) / "SR Module").resolve()
    with _srim_lock:
        write_input(layer, energy, Z1, M1, srim_directory)
        subprocess.run([str(srim_directory / "SRModule.exe")], cwd=srim_directory, check=True)
        return read_SRIM_stopping_cross_section(srim_directory) / 1000

def assign_stopping(target: Target, energy: float, model: Literal["SRIM", "SCS-25-Solid"], *, Z1: int, M1: float, srim_path: str = "") -> Target:
    """Return a copy of ``target`` with layers subdivided for stopping accuracy.

    Each original layer is repeatedly halved until the stopping cross sections
    at its entry and exit differ by no more than ``percentage``. The resulting
    segments retain the original layer's total areal density.
    """
    new_target = copy.deepcopy(target)
    new_target["layers"] = []
    current_energy = energy
    relative_tolerance = percentage / 100.0

    def stopping_at_layer_bounds(layer: Layer, entry_energy: float, thickness: float)->tuple[float, float]:
        stopping_in = calc_stopping_cross_section(layer, entry_energy, model, Z1=Z1, M1=M1, srim_path=srim_path)
        exit_energy = entry_energy - thickness * stopping_in
        if exit_energy < 0:
            return stopping_in, 0.000001
        stopping_out = calc_stopping_cross_section(layer, exit_energy, model, Z1=Z1, M1=M1, srim_path=srim_path)
        return stopping_in, stopping_out

    for original_index, original_layer in enumerate(target["layers"]):
        original_ad = original_layer["areal_density"]
        segment_count = 1
        segment_ad = original_ad

        # Pick a power-of-two segment count that satisfies the stopping tolerance.
        while current_energy > 0:
            stopping_in, stopping_out = stopping_at_layer_bounds(
                original_layer, current_energy, segment_ad
            )
            max_stopping = max(abs(stopping_in), abs(stopping_out))
            relative_change = (
                abs(stopping_in - stopping_out) / max_stopping
                if max_stopping > 0
                else 0.0
            )
            if relative_change <= relative_tolerance:
                break
            segment_count *= 2
            segment_ad = original_ad / segment_count
        print(f"Layer {original_index + 1}: Stopping cross section judged accurate with {segment_count} segments")

        # Keep the sum of the segment thicknesses equal to the source thickness.
        for segment_index in range(segment_count):
            segment = copy.deepcopy(original_layer)
            segment_thickness = (
                original_ad - segment_ad * (segment_count - 1)
                if segment_index == segment_count - 1
                else segment_ad
            )
            segment["areal_density"] = segment_thickness

            if current_energy <= 0:
                stopping_in = 0.0
                stopping_out = 0.0
                segment["stopping"] = 0.0
            else:
                stopping_in, stopping_out = stopping_at_layer_bounds(
                    segment, current_energy, segment_thickness
                )
                segment["stopping"] = (stopping_in + stopping_out) / 2
                current_energy -= segment_thickness * segment["stopping"]

            new_target["layers"].append(segment)
            print(
                f"Target layer #{original_index + 1}.{segment_index + 1} "
                f"({segment_thickness:.3f} TFU), S = {segment['stopping']:.6f} keV/TFU "
                f"(S_in = {stopping_in:.6f}, S_out = {stopping_out:.6f})"
            )

    return new_target
