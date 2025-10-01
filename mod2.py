import os
import numpy as np
import periodictable
import json
import time
import copy

energy_res = 6385.0 # keV
percentage = 0.5

# Writing input file for SRIM
def write_input(layer, energy, ind=0):
    file_path = "SR.IN"

    # Delete existing file if it exists
    if os.path.isfile(file_path):
        os.remove(file_path)

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
        file.write("7 \n")  # eV/TFU
        file.write("---Ion Energy : E-Min(keV), E-Max(keV) \n")
        file.write("0   0 \n")
        file.write(f"{energy}")

# Reading output file from SRIM
def read_stoppower():
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

# Using SRIM to calculate stopping power
def calc_stopping_power(layer,energy,ind = 0):
    write_input(layer,energy,ind)
    os.startfile(r"SRModule.exe")
    time.sleep(0.25) # Leaving some time so SRIM (SR Module) can run

    return read_stoppower()/1000 # Final units: keV/TFU

def assign_stopping(target, energy):
    '''
    target: 

    energy: Max energy of the excitation curve
    '''
    new_target = copy.deepcopy(target)
    new_target["layers"].clear()
    partDidntEnterLayer = False
    index = 0
    list=[]

    for i in range(len(target["layers"])):
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
            S_in = calc_stopping_power(target["layers"][i],E_in)
            print(f"IN - Energy: {E_in:.3f} & Stopping: {S_in:.6f}")
            E_out = E_in - target["layers"][i]["areal_density"] * S_in

            if E_out < 0:
                E_out = 0
                S_out = 0.000001
            else:
                S_out = calc_stopping_power(target["layers"][i],E_out)
            print(f'OUT - Energy: {E_out:.3f} & Stopping: {S_out:.6f}')

            # Checking for variation 
            if abs(S_in - S_out)/max(abs(S_in), abs(S_out)) > percentage/100.0:
                print("Layer too thick, cutting")
                target["layers"][i]["areal_density"] /= 2
                ctr+=1
            else:
                target["layers"][i]["stopping"] = (S_in + S_out) / 2 # No segmentation required, assigning stopping power (mid layer approx)
                print(f'Final Stopping: {target["layers"][i]["stopping"]} keV/TFU')

        # Onward: out of while loop
        #print("ctr",ctr)
        #NbrDaughter = 2**ctr
        if ctr ==2:
            Count = 2
        else:
            Count = max(1,(ctr-1)**2)

        list.append(Count) # Count: Number of daughter layers from parent layer that is going to be segmented
        index += ctr

        # Segmentation sequence
        for k in range(Count):
            new_target["layers"].append(copy.deepcopy(target["layers"][i]))
            #print(k) 

        # Assigning stopping powers to the segmentated target
        for k in range(Count):
            nbr = sum(list[j] for j in range(i))
            # print('nbr', nbr)
            if k == 0:
                if partDidntEnterLayer:
                    #print(index)
                    new_target["layers"][index]["stopping"] = 0
                #continue
            #print(list)
            #print(k)
            loss = sum(new_target["layers"][n]["areal_density"] * new_target["layers"][n]["stopping"] for n in range(nbr+k))
            #print("loss: ", loss)
            E_in = energy - loss
            #print("E in: ", E_in)
            if E_in <= 0 or partDidntEnterLayer: # If the particle doesn't reach the start of layer, putting stopping power to 0
                # new_target["layers"][k]["stopping"] = new_target["layers"][k-1]["stopping"]
                new_target["layers"][k+nbr]["stopping"] = 0
                continue

            S_in = calc_stopping_power(new_target["layers"][nbr+k], E_in)
            E_out = E_in - new_target["layers"][k+nbr]["areal_density"] * S_in
            if E_out < 0:
                E_out = 0
                S_out = 0.000001
            else:
                S_out = calc_stopping_power(new_target["layers"][k+nbr],E_out)
            # print("k: ",k+nbr,"- S out: ", S_out)

            new_target["layers"][k+nbr]["stopping"] = (S_in + S_out)/2

    return new_target

os.chdir(r"SRIM\SR Module")

if __name__ == "__main__":
    with open("target_data.json",'r') as f:
        target_input = json.load(f)
    print("Number of layer in input file:",len(target_input["layers"]))

    new_target = assign_stopping(target_input,energy_res)

    with open(r"C:\HyProC\target_data_NEW final test.json","w") as f:
         json.dump(new_target,f,indent=4)
