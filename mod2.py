import os
import subprocess
import periodictable
import json
import copy

from class_models import Element, Layer, Target

energy_res = 6385.0 # keV
percentage = 0.5

# Writing input file for SRIM
def write_input(layer: Layer, energy: float)->None:
    """
    Writes the SR.IN input file that SRIM uses to calculate the stopping power of a given layer.

    Parameters:
        layer (Layer) : layer of a given target.
        energy (float) : Energy (in keV) at which the stopping power is going to be calculated.

    Returns
    -------
        None
    """
    file_path = "SR.IN"

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
        file.write("7   15.000\n")
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
def read_stoppower()-> float:
    """
    Reads the output file from SRIM.

    Parameters
    ----------
        None

    Returns
    -------
        S (float): Stopping power in keV/TFU (both electronic and nuclear)
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

def calc_stopping_power(layer: Layer, energy: float) -> float:
    """
    Computes the stopping power of a given layer at a certain energy using SRIM.

    Parameters:
        layer (Layer) : layer of a given target.
        energy (float) : Energy (in keV) at which the stopping power is going to be calculated.

    Returns:
        S (float) : Stopping power in keV/TFU
    """
    write_input(layer, energy)
    subprocess.run(["SRModule.exe"], check=True)

    return read_stoppower()/1000 # Final units: keV/TFU

def assign_stopping(target: Target, energy: float) -> Target:
    '''
    Computes the stopping power of each layer based on its composition and the initial beam energy. The stopping power is considered constant, therefore layers that are too thick are cut in smaller ones to keep that approximation correct. 

    Parameters:
        target (Target): Target  description
        energy (float): Max energy of the excitation curve

    Returns:
        target_copy (Target): Target description. Each layer has a constant stopping power (in keV/TFU)

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
                print('--- Layer #0, E in: ', E_in)
            else:
                k = len(new_target["layers"])
                loss = sum(new_target["layers"][n]["areal_density"] * new_target["layers"][n]["stopping"] for n in range(k))
                E_in = energy - loss
                print(f'--- Layer #{i}, E in: ', E_in)

            if E_in <= 0:
                partDidntEnterLayer = True
                break
            S_in = calc_stopping_power(layer,E_in)
            print(f"IN - Energy: {E_in:.3f} & Stopping: {S_in:.6f}")
            E_out = E_in - layer["areal_density"] * S_in

            if E_out < 0:
                E_out = 0
                S_out = 0.000001
            else:
                S_out = calc_stopping_power(layer, E_out)
            print(f'OUT - Energy: {E_out:.3f} & Stopping: {S_out:.6f}')

            # Checking for variation between the stopping powers on entry VS on exit
            if abs(S_in - S_out)/max(abs(S_in), abs(S_out)) > percentage/100.0:
                print("Layer too thick, cutting")
                layer["areal_density"] /= 2
                ctr+=1
            else:
                layer["stopping"] = (S_in + S_out) / 2 # No segmentation required, assigning stopping power (mid layer approx)
                print(f'Final Stopping: {layer["stopping"]} keV/TFU')

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

        # Assigning stopping powers to the segmented target
        for k in range(Count):
            nbr = sum(daughterLayers_by_layer[:i])
            if k == 0:
                if partDidntEnterLayer:
                    new_target["layers"][index]["stopping"] = 0

            loss = sum(new_target["layers"][n]["areal_density"] * new_target["layers"][n]["stopping"] for n in range(nbr+k))
            E_in = energy - loss
            if E_in <= 0 or partDidntEnterLayer: # If the particle doesn't reach the start of layer, putting stopping power to 0
                new_target["layers"][k+nbr]["stopping"] = 0
                continue

            S_in = calc_stopping_power(new_target["layers"][nbr+k], E_in)
            E_out = E_in - new_target["layers"][k+nbr]["areal_density"] * S_in
            if E_out < 0:
                E_out = 0
                S_out = 0.000001
            else:
                S_out = calc_stopping_power(new_target["layers"][k+nbr],E_out)

            new_target["layers"][k+nbr]["stopping"] = (S_in + S_out)/2

    return new_target

# Finding out where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__)) 
settings_path = os.path.join(script_dir, 'settings.json')

# Loading the SRIM path from the settings json file
with open(settings_path,'r', encoding="utf-8") as f:
    filedata = json.load(f)
    path=filedata["SRIM_path"]
SRIM_path = os.path.join(path,"SR Module")    
os.chdir(SRIM_path)