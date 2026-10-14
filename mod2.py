import os
import subprocess
import periodictable
import json
import copy
import math
from functools import lru_cache
from typing import Literal

from class_models import Element, Layer, Target

# Load settings
script_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(script_dir, 'settings.json')
with open(settings_path, 'r', encoding="utf-8") as f:
    settings = json.load(f)

Z1 = int(settings["reaction"]["Z1"])
A1 = int(settings["reaction"]["A1"])
M1 = periodictable.elements[Z1][A1].mass  # amu
energy_res = settings["resonance"]["E_R"]  # keV

# Stopping cross section variation allowed within a layer (in %)
percentage = 0.5

def check_srim_path(settings_path: str) -> bool:
    with open(settings_path, 'r', encoding="utf-8") as f:
        path = json.load(f)["SRIM_path"]
    return os.path.exists(os.path.join(path, "SR Module"))

# Writing input file for SRIM
def write_input(layer: Layer, energy: float)->None:
    """
    Writes the SR.IN input file that SRIM uses to calculate the stopping cross section of a given layer.

    Parameters:
        layer (Layer) : layer of a given target.
        energy (float) : Energy (in keV) at which the stopping cross section is going to be calculated.

    Returns
    -------
        None
    """
    # Finding out where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    settings_path = os.path.join(script_dir, 'settings.json')

    # Loading the SRIM path from the settings json file
    with open(settings_path,'r', encoding="utf-8") as f:
        filedata = json.load(f)
        path=filedata["SRIM_path"]
    SRIM_path = os.path.join(path,"SR Module")    
    os.chdir(SRIM_path)

    file_path = os.path.join(SRIM_path, "SR.IN")

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
def read_SRIM_stopping_cross_section()-> float:
    """
    Reads the output file from SRIM.

    Parameters
    ----------
        None

    Returns
    -------
        S (float): Stopping cross section in keV/TFU (both electronic and nuclear)
    """
    with open("Output", 'r') as f: # Output is the file name!!
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
    parameter_path = os.path.join(script_dir, "SCS-2025-solid.json")
    with open(parameter_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["parameters"]


def _scs_stopping_cross_section(z2: int, energy_per_u: float) -> float:
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


def _ziegler_nuclear_stopping_cross_section(z2: int, energy: float) -> float:
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


def _calc_scs_stopping_components(layer: Layer, energy: float) -> tuple[float, float]:
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
            atomic_fraction * _scs_stopping_cross_section(z2, energy_per_u)
        )
        nuclear_stopping_cross_section += (
            atomic_fraction * _ziegler_nuclear_stopping_cross_section(z2, energy)
        )

    # Both Bragg-weighted components are in eV/TFU.
    return electronic_stopping_cross_section / 1000.0, nuclear_stopping_cross_section / 1000.0


def _calc_scs_stopping_cross_section(layer: Layer, energy: float) -> float:
    electronic_stopping, nuclear_stopping = _calc_scs_stopping_components(layer, energy)
    return electronic_stopping + nuclear_stopping


def calc_stopping_cross_section(layer: Layer, energy: float, model: Literal["SRIM", "SCS-25-Solid"] = "SRIM") -> float:
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
        return _calc_scs_stopping_cross_section(layer, energy)
    if model != "SRIM":
        raise ValueError(f"Unsupported stopping-cross-section model: {model}")

    write_input(layer, energy)
    subprocess.run(["SRModule.exe"], check=True)

    return read_SRIM_stopping_cross_section()/1000 # Final units: keV/TFU

def assign_stopping(target: Target, energy: float, model: Literal["SRIM", "SCS-25-Solid"] = "SRIM") -> Target:
    '''
    Computes the stopping cross section of each layer based on its composition and the initial beam energy. The stopping cross section is considered constant, therefore layers that are too thick are cut in smaller ones to keep that approximation correct.

    Parameters:
        target (Target): Target  description
        energy (float): Max energy of the excitation curve

    Returns:
        target_copy (Target): Target description. Each layer has a constant stopping cross section (in keV/TFU)

    '''
    new_target = copy.deepcopy(target)
    new_target["layers"].clear()
    partDidntEnterLayer = False
    index = 0
    daughterLayers_by_layer = []

    for i, layer in enumerate(target["layers"]):
        ctr = 1

        # Dummy values to make sure the program enters the while loop
        S_in = 10
        S_out = 1

        while abs(S_in - S_out)/max(abs(S_in), abs(S_out)) > percentage/100.0: 
            if i == 0:
                E_in = energy 
                print(f'--- Layer #0, E in: {E_in:.6f} keV')
            else:
                k = len(new_target["layers"])
                loss = sum(new_target["layers"][n]["areal_density"] * new_target["layers"][n]["stopping"] for n in range(k))
                E_in = energy - loss
                print(f'--- Layer #{i}, E in: {E_in:.6f} keV')

            if E_in <= 0:
                partDidntEnterLayer = True
                break
            S_in = calc_stopping_cross_section(layer, E_in, model)
            print(f"IN - Energy: {E_in:.3f} keV & Stopping: {S_in:.6f} keV/TFU")
            E_out = E_in - layer["areal_density"] * S_in

            if E_out < 0:
                E_out = 0
                S_out = 0.000001
            else:
                S_out = calc_stopping_cross_section(layer, E_out, model)
            print(f'OUT - Energy: {E_out:.3f} keV & Stopping: {S_out:.6f} keV/TFU')

            # Checking for variation between the stopping cross sections on entry VS on exit
            if abs(S_in - S_out)/max(abs(S_in), abs(S_out)) > percentage/100.0:
                print("Layer too thick, cutting")
                layer["areal_density"] /= 2
                ctr+=1
            else:
                layer["stopping"] = (S_in + S_out) / 2 # No segmentation required, assigning stopping cross section (mid layer approx)
                print(f'Final Stopping: {layer["stopping"]:.9f} keV/TFU')

        #NbrDaughter = 2**ctr
        if ctr ==2:
            Count = 2
        else:
            Count = max(1,(ctr-1)**2)

        daughterLayers_by_layer.append(Count) # Count: Number of daughter layers from parent layer
        index += ctr

        # Segmentation sequence
        for k in range(Count):
            new_target["layers"].append(copy.deepcopy(target["layers"][i]))

        # Assigning stopping cross sections to the segmented target
        for k in range(Count):
            nbr = sum(daughterLayers_by_layer[:i])
            if k == 0:
                if partDidntEnterLayer:
                    new_target["layers"][index]["stopping"] = 0

            loss = sum(new_target["layers"][n]["areal_density"] * new_target["layers"][n]["stopping"] for n in range(nbr+k))
            E_in = energy - loss
            if E_in <= 0 or partDidntEnterLayer: # If the particle doesn't reach the start of layer, putting stopping cross section to 0
                new_target["layers"][k+nbr]["stopping"] = 0
                continue

            S_in = calc_stopping_cross_section(new_target["layers"][nbr+k], E_in, model)
            E_out = E_in - new_target["layers"][k+nbr]["areal_density"] * S_in
            if E_out < 0:
                E_out = 0
                S_out = 0.000001
            else:
                S_out = calc_stopping_cross_section(new_target["layers"][k+nbr], E_out, model)

            new_target["layers"][k+nbr]["stopping"] = (S_in + S_out)/2

    return new_target

if __name__ == "__main__":
    # Test case for the stopping cross section calculation
    print("Incoming ion: Z1 =", Z1, "A1 =", A1, "M1 =", M1, "amu")
    example_layer = {
        "elements": [
            {"Z": 14, "percent_at": 33.333},
            {"Z": 8, "percent_at": 66.667}
        ],
        "areal_density": 1500.0
    }
    energy = 5000  # keV
    model = "SCS-25-Solid"  # SRIM or SCS-25-Solid

    if model == "SCS-25-Solid":
        electronic_stopping, nuclear_stopping = _calc_scs_stopping_components(example_layer, energy)
        print(f"Electronic stopping cross section: {electronic_stopping:.7g} keV/TFU")
        print(f"Nuclear stopping cross section: {nuclear_stopping:.7g} keV/TFU")
        stopping_cross_section = electronic_stopping + nuclear_stopping
    else:
        stopping_cross_section = calc_stopping_cross_section(example_layer, energy, model)
    print(f"Total stopping cross section: {stopping_cross_section:.7g} keV/TFU")