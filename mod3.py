import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
import json
import periodictable

m_N = 13972.5 # keV
m_H = 938.272 # keV

# Resonance properties
E_R = 6385.0 # keV
Gamma = 1.8 # keV
sigma_R = 1650 # mb/keV


def gauss(x, x0, sigma):
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-(x - x0)**2 / (2 * sigma**2))

def lorentz(x, x0, gamma,sigma=1.0):
    return sigma *(gamma**2 / 4) / ((gamma**2 / 4) + (x-x0)**2)
    # return sigma*1/(np.pi*gamma / 2) *(gamma**2 / 4) / ((gamma**2 / 4) + (x-x0)**2)

def loss_axis(target):
    """
    Computes the cumulative energy loss through each layer of a multi-layer target, based on stopping power and areal density.
    This is used to identify the layer in which the resonance is reached for a given incident energy.

    Parameters:
        target (dict): A dictionary describing the target structure, including layer properties such as stopping power and areal density.

    Returns:
        E_loss (list): Cumulative energy loss in each layer.
    """
    E_loss = []
    loss = 0.0
    for i in range(len(target["layers"])):
        loss = sum(target["layers"][j]["stopping"]*target["layers"][j]["areal_density"] for j in range(i))
        E_loss.append(loss + target["layers"][i]["stopping"]*target["layers"][i]["areal_density"])
    return E_loss

def find_layer_index(E_in,E_loss):
    """
    For a given incident energy, identifies in which layer the resonance is reached in order to extract its properties.
    To do, the energy loss required to reach the resonance is compared to the the energy loss of each layer.
    
    Parameters:
        E_in (float) : Incident energy
        E_loss (list) : Cumulative energy loss in each layer

    Returns:
        index (int) : Index of the layer in which the resonance is reached.
    """
    deltaE_in = E_in - E_R  # Energy loss to get to the resonance
    if deltaE_in < 0:
        return -2  # Out of target: front of target
    for i, num in enumerate(E_loss):
        if deltaE_in <= num:
            return i
    return -1  # Out of target: back of target

def get_Z(target,index,excl_H=False):
    """
    Determines the effective Z (atomic number) of the layer where the resonance is reached.
    Bragg's rule is used if the layer is made of multiple elements.
    Hydrogen can be excluded from the calculation, which may be useful for Doppler broadening.
    
    Parameters:
        target (dict) : Dictionary representing the target structure, including layers and their elemental compositions.
        index (int) : Index of the layer in which the resonance is reached.
        excl_H (bool, optionnal) : Exclude hydrogen from calculation if True (False by default, True should only be used for Doppler)

    Returns:
        Z (float) : Effective atomic number of the layer in which the resonance is reached.
    """
    listZ = []
    for i in range(len(target["layers"][index]["elements"])):
        listZ.append((target["layers"][index]["elements"][i]["Z"], target["layers"][index]["elements"][i]["percent_at"]))

    # Removing hygrogen from the list if wished
    if excl_H:
        listZ = [item for item in listZ if item[0] != 1]

    # Bragg's rule to find the mean atomic number Z
    Z_mean = sum(a * b/100 for a, b in listZ)

    total_percent_at = sum(b for a, b in listZ)

    # Normalising in case the total atomic percentage isn't 100%
    if not total_percent_at == 100.0:
        Z_mean = Z_mean/total_percent_at*100.0

    return round(Z_mean,2)

def get_A(target,index):
    """
    Determines the effective A (molar mass) of the layer where the resonance is reached.
    Bragg's rule is used if the layer is made of multiple elements.
    
    Parameters:
        target (dict) : Dictionary representing the target structure, including layers and their elemental compositions.
        index (int) : Index of the layer in which the resonance is reached.

    Returns:
        A (float) : Effective molar mass of the layer in which the resonance is reached.
    """
    listA = []
    for i in range(len(target["layers"][index]["elements"])):
        listA.append((periodictable.elements[target["layers"][index]["elements"][i]["Z"]].mass, target["layers"][index]["elements"][i]["percent_at"]))
    # Bragg's rule to find the mean atomic number Z
    A_mean = sum(a * b/100 for a, b in listA)
    return A_mean

def get_density(target,index):
    """
    Determines the effective A (molar mass) of the layer where the resonance is reached.
    Bragg's rule is used if the layer is made of multiple elements.
    
    Parameters:
        target (dict) : Dictionary representing the target structure, including layers and their elemental compositions.
        index (int) : Index of the layer in which the resonance is reached.

    Returns:
        A (float) : Effective molar mass of the layer in which the resonance is reached.
    """
    list = []
    for i in range(len(target["layers"][index]["elements"])):
        list.append((periodictable.elements[target["layers"][index]["elements"][i]["Z"]].density, target["layers"][index]["elements"][i]["percent_at"]))
    # Bragg's rule to find the mean atomic number Z
    mean = sum(a * b/100 for a, b in list)
    return mean

def find_in_layer_thickness(E_in, E_loss, index, target):
    """
    Calculates the thickness within the resonance layer at which the resonance occurs.

    This is determined by comparing the incident energy to the cumulative energy loss up to that layer,
    then computing the thickness fraction in the specified layer corresponding to the remaining energy loss.

    Parameters:
        E_in (float): Incident energy.
        E_loss (list): Cumulative energy loss values for each layer.
        index (int): Index of the layer where the resonance occurs.
        target (dict): Dictionary representing the target structure, including layer stopping powers.

    Returns:
        float: Thickness within the specified layer at which the resonance is reached.
    """
    deltaE_in = E_in - E_R 
    if index == 0:
        inlayer_loss = deltaE_in
    # elif deltaE_in > max(E_loss):
    #     print("Here")
    #     inlayer_loss = E_loss[len(E_loss)-1] - E_loss[len(E_loss)-2]
    else:
        inlayer_loss = deltaE_in - E_loss[index-1]
    thickness = inlayer_loss/target["layers"][index]["stopping"]
    return thickness

def find_total_thickness(E_in, E_loss, index, target):
    """
    Calculates the total thickness traveled by the incident particle up to the resonance point in the target.

    For cases where the resonance occurs before the first layer or after the last layer, it computes
    appropriate offsets or returns the total target thickness. Otherwise, it sums the full thickness
    of all preceding layers and adds the partial thickness in the resonance layer.

    Parameters:
        E_in (float): Incident energy.
        E_loss (list): Cumulative energy loss values for each layer.
        index (int): Index of the layer where the resonance occurs.
                     Special values: -2 if resonance is before the target,
                                     -1 if resonance is beyond the last layer.
        target (dict): Dictionary representing the target structure, including layer areal densities and stopping powers.

    Returns:
        thickness (float): Total thickness traveled up to the resonance point within the target.
    """
    if index==-2:
        offset = E_in - E_R
        return offset/target["layers"][0]["stopping"]
    elif index==-1:
        return sum(layer["areal_density"] for layer in target["layers"])
    thickness = 0.0
    for i in range(index):
        thickness += target["layers"][i]["areal_density"]
    thickness_in_last_layer = find_in_layer_thickness(E_in, E_loss, index, target)
    thickness+= thickness_in_last_layer
    return thickness
    


def DopplerSD(target, index):
    """
    Calculates the Doppler standard deviation (delta_D) for the incident particle 
    based on the atomic number (Z) of the layer where the resonance is reached.

    Specific known values are used for silicon (Z=14), titanium (Z=22), and lead (Z=82).
    For other elements, delta_D is approximated by a linear fit derived from known data.

    Parameters:
        target (dict): Dictionary describing the target structure.
        index (int): Index of the layer where the resonance is reached.

    Returns:
        delta_D (float): Doppler standard deviation (delta_D) for the incident particle in the specified layer.
    """
    Z = get_Z(target,index, excl_H=True)
    #print("Z Doppler", Z)
    if Z == 14:  # H-Si binding
        delta_D = 4.00
    elif Z == 22:  # H-Ti binding
        delta_D = 3.69
    elif Z == 82:  # H-Pb binding
        delta_D = 2.55
    else:  # Other element (approx based on the above data)
        delta_D = -0.0218*Z+4.2421  # parameters calculated from a fit between 2 elements
    return delta_D

def Stragg_law(Z, thickness, model="Rud",A=None,density=None):
    """
    Calculates the standard deviation of the straggling-induced broadening using the specified theoretical model.

    Parameters:
        Z (int or float) : Atomic number of the material.
        thickness (float) : Thickness of the material layer (units depend on the model used).
        model (str, optional) : The straggling model to use; either "Rud" (default) or "Bohr".

    Returns:
        float : Calculated energy straggling value according to the selected model.
    """
    if model == "Rud":
        return 2.03*Z**0.39*np.sqrt(thickness/10.0)/2.355
    if model == "Rud corr":
        return 2.03*Z**0.39*np.sqrt(thickness/10.0)/2.355/1.7
    if model == "Bohr":
        return 0.395*7*np.sqrt(Z*thickness*1E+15*A/(periodictable.constants.avogadro_number/density))

def stragg(E_in, E_loss, index, target):
    """
    Calculates the straggling based on the atomic number,
    material thickness, and selected model.

    Parameters:
        E_in (float): Incident energy.
        E_loss (list): Cumulative energy loss values for each layer.
        index (int): Index of the layer where the resonance occurs.
                     Special values: -2 if resonance is before the target,
                                     -1 if resonance is beyond the last layer.
        target (dict): Dictionary representing the target structure, including layer areal densities and stopping powers.

    Returns:
        float : Calculated straggling value according to the selected model.
    """
    Var_S = 0.0
    model = "Rud corr"
    if False:
        A = get_A(target, index)
        density = get_density(target,index)
    else:
        A, density = 1, 1.0
    if index == -1:
        for j in range(len(target["layers"])):
            Z = get_Z(target, j, excl_H=False) # Extracting elemental composition of the layer
            DeltaTFU = target["layers"][j]["areal_density"]  # Depth in the layer in which the reaction takes place 
            #print("D TFU -1", DeltaTFU)
            delta_S = Stragg_law(Z, DeltaTFU, model, A, density)
            Var_S += delta_S**2
    else:
        for i in range(index+1):
            Z = get_Z(target, i, excl_H=False) 
            if not i == max(range(index+1)):  
                DeltaTFU = target["layers"][i]["areal_density"]  
            else: 
                DeltaTFU = find_in_layer_thickness(E_in, E_loss,i, target) 

            #print("D TFU", DeltaTFU)
            delta_S = Stragg_law(Z, DeltaTFU, model, A, density)
            Var_S += delta_S**2
    #print('stragg index ', index)
    #print("Straggling SD: ", np.sqrt(Var_S))
    return np.sqrt(Var_S)

def save(vector1, vector2, filename):
    """
    Saves two vectors as tab-separated columns to a text file.
    To use in case the broadening data need to be analysed.

    Parameters:
        vector1 (list or iterable) : First vector of values.
        vector2 (list or iterable) : Second vector of values, must be the same length as vector1.
        filename (str) : Path to the output file where data will be saved.

    Raises:
        ValueError: If the input vectors have different lengths.

    Returns:
        None
    """
    if len(vector1) != len(vector2):
        raise ValueError("Vectors must be the same length.")

    with open(filename, 'w') as f:
        for v1, v2 in zip(vector1, vector2):
            f.write(f"{v1}\t{v2}\n")


def broadening(E_in, target, delta_B, Doppler=True, saveData=False,savepath=None):
    """
    Calculates the full energy broadening profile of an incident particle in a multi-layer target,
    accounting for cross section, beam, Doppler, and straggling broadenings, and converts the energy distribution
    into a thickness profile. Optionally saves intermediate data to files.

    Parameters:
        E_in (float) : Incident particle energy (keV).
        target (dict) : Dictionary describing the target structure and layer properties.
        delta_B (float) : Beam energy broadening (keV).
        Doppler (bool, optional) : Whether to include Doppler broadening (default True).
        saveData (bool, optional) : Whether to save intermediate broadening data to files (default False).
        savepath (str, optional) : Path to directory for saving data files if saveData is True.

    Returns:
        center (float) : Thickness within the target at which resonance is reached (in TFU).
        x_conv_TFU (list of float) : Thickness values corresponding to the broadened energy profile.
        y_conv_TFU (list of float) : Intensity values of the broadened profile mapped to thickness.
        layers_contribution (list of float) : Normalized contributions of each layer to the profile.
        outOfTarget (float) : Fraction of the profile corresponding to particles escaping the target.
    """
    E_loss = loss_axis(target)
    index = find_layer_index(E_in, E_loss)
    # print('index',index)
    
    if Doppler: 
        if index==-2:
            delta_D = DopplerSD(target, 0)
            # delta_D = 0
        elif index==-1:
            delta_D = DopplerSD(target, len(target["layers"])-1)
        else:
            delta_D = DopplerSD(target, index)
    else:
        delta_D = 0

    if index==-2:
        delta_S = 0
    else:
        delta_S = stragg(E_in, E_loss, index, target)

    SD_gauss = np.sqrt(delta_B**2+delta_D**2+delta_S**2)

    # Where to center the broadening curve
    if E_in < E_R:
        E_center = E_in
    elif index == -1:
        E_center = E_in - max(E_loss)
    else:
        E_center = E_R
        
    Range = 4
    x = np.linspace(E_center-Range*SD_gauss, E_center+Range*SD_gauss, 1501) 
    dx = x[1] - x[0]
    
    y1 = gauss(x, E_center, SD_gauss)
    y1 /= np.trapz(y1,x)  # Normalising
    mean_y1 = np.trapz(x * y1, x)
    
    y2 = lorentz(x, E_R, Gamma, sigma_R/1000)  # Remove? sigma_R
    #y2 /= np.trapz(y2, x)  # Normalising

    # Convolution between the final Gaussian & Lorentzian
    y_conv = convolve(y1, y2, mode='full') * dx  
    x_conv = np.arange(len(y_conv)) * dx + 2 * x[0]  # Generating x-axis 
    y_conv /= np.trapz(y_conv, x_conv)  # Normalising
    mean_conv = np.trapz(x_conv * y_conv, x_conv)  # Center of the resulting Voigt profile
    x_conv = x_conv - (mean_conv - mean_y1)  # Centering the x axis on the resonance energy

    center = find_total_thickness(E_in, E_loss, index, target)  # Thickness at which the energy resonance is reached for a given incident energy
    # print("c ",center)
    deltaE_in = E_in - E_R  # Energy loss to get to the resonance

    # Changing the x-axis from energy (keV) to thickness (TFU)
    x_conv_TFU = []
    y_conv_TFU = []

    for l,eVal in enumerate(x_conv):
        deltaE = E_R - eVal  # Energy difference relative to E_R
        Eloss_value = deltaE_in - deltaE  # Energy loss for the current energy value
        new_index = find_layer_index(E_in - deltaE, E_loss)
        outOfTarget = 0

        layers_contribution = np.zeros(len(target["layers"]))

        # If target escape (front)
        if new_index == -2:
            #value = center + (Eloss_value - deltaE_in)/target["layers"][0]["stopping"]
            x_value = Eloss_value/target["layers"][0]["stopping"]
            y_value = 0.0
            y_value = y_conv[l]
            # y_conv[np.where(x_conv == eVal)] = 0
            outOfTarget += 1
        
        # If target escape (back)
        if new_index == -1:
            x_value = sum(target["layers"][k]["areal_density"] for k in range(len(target["layers"]))) + (Eloss_value-max(E_loss))/target["layers"][0]["stopping"]
            y_value = 0.0
            # y_conv[np.where(x_conv == eVal)] = 0
            outOfTarget += 1

        # No escape
        if new_index > -1:
            y_value = y_conv[l]
            layers_contribution[new_index] += 1
        
            if new_index != index and index > -1:
                
                low_index = min(index, new_index)
                high_index = max(index, new_index)
                low_loss = min(deltaE_in, Eloss_value)
                high_loss = max(deltaE_in, Eloss_value)

                if abs(new_index-index) >= 2:
                    fullLayerThicknesses = sum(target["layers"][i]["areal_density"] for i in range(low_index + 1, high_index, 1))
                else:
                    fullLayerThicknesses = 0.0
                
                x_value = center + np.sign(new_index - index) * (fullLayerThicknesses + abs(low_loss-E_loss[low_index])/target["layers"][low_index]["stopping"] + abs(high_loss-E_loss[high_index-1])/target["layers"][high_index]["stopping"] )
                
            elif new_index > 0 and index == -2:
                fullLayerThicknesses = sum(target["layers"][i]["areal_density"] for i in range(0, new_index)) 
                x_value = fullLayerThicknesses + (Eloss_value-E_loss[new_index-1])/target["layers"][new_index]["stopping"]

            elif new_index >= 0 and index == -1:
                fullLayerThicknesses = sum(target["layers"][i]["areal_density"] for i in range(new_index+1,len(target["layers"]))) 
                x_value = center - fullLayerThicknesses + (Eloss_value-E_loss[new_index])/target["layers"][new_index]["stopping"]

            else:
                x_value = center + (Eloss_value - deltaE_in)/target["layers"][new_index]["stopping"]  # Here, using index or new_index is equivalent            
        
        x_conv_TFU.append(x_value)
        y_conv_TFU.append(y_value)

    # Normalising to get layer contribution in %
    total = sum(layers_contribution) + outOfTarget
    layers_contribution = [x / total for x in layers_contribution]
    outOfTarget /= sum(layers_contribution) + outOfTarget
    
    if saveData:
        print(savepath)
        save(x, gauss(x,E_center, delta_B), savepath+"\\"+"Beam.txt")
        if delta_S == 0:
            save(x, np.zeros(len(x)), savepath+"\\"+"Stragg.txt")
        else:
            save(x, gauss(x,E_center, delta_S), savepath+"\\"+"Stragg.txt")
        if Doppler:
            save(x, gauss(x,E_center, delta_D), savepath+"\\"+"Doppler.txt")
        save(x, y1,savepath+"\\"+"Total_Gauss.txt")
        save(x, lorentz(x,E_R, Gamma,sigma_R), savepath+"\\"+"xsec.txt")
        save(x_conv, y_conv,savepath+"\\"+"Total_Broadening.txt")
        save(x_conv_TFU, y_conv_TFU,savepath+"\\"+"Total_Broadening_TFU.txt")
        # os.chdir("..")"C:\HyProC\target_data_NEWtest.json"

    return center, x_conv_TFU, y_conv_TFU, layers_contribution, outOfTarget


if __name__ == "__main__":
    with open(r"C:\Users\louis\OneDrive - Université de Namur\Documents\Mémoire (MA2)\OwnCode\Straggling comparison\Ti33H66.json",'r') as f:
        target_input = json.load(f)

    target_input["layers"][0]["areal_density"] = 2500
    print(target_input)

    E_i = 10000
    # x,y = broadening(E_i, target_input )

    Z = get_Z(target_input,0,excl_H=False)
    print(Z)

    x=loss_axis(target_input)
    SD = stragg(E_i, x, -1, target_input)
 




