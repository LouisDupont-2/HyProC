import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import json

# Creating the hydrogen profile from the target
def cH_make(target):
    """
    Creates a hydrogen step profile from the current target.
    
    Parameters:
        target (Target): Target description.

    Returns
    -------
        cH_x (list of float): x values of the hydrogen step profile (TFU).
        cH_y (list of float): y values of the hydrogen step profile (at. %).

    """
    cH_x = np.zeros(len(target["layers"])+1)
    value = 0.0
    for i in range(len(target["layers"])):
        value += target["layers"][i]["areal_density"]
        cH_x[i+1] = value
    cH_y = []
    for layer in target["layers"]:
        z1_fraction = sum(elem["percent_at"] for elem in layer["elements"] if elem["Z"] == 1) 
        cH_y.append(z1_fraction)
    cH_y.insert(0, 0.0) # Inserting 0.0 at index 0

    return cH_x, cH_y

# Calculating yield
def compute_yield(target, x_conv_TFU, y_conv_TFU):
    """
    Calculates the gamma-yield at a given energy based on the hydrogen depth profile of the target and broadening function.

    Parameters:
        target (Target) : Target description.
        x_conv_TFU (list of float) : Thickness values corresponding to the broadening energy profile.
        y_conv_TFU (list of float) : Probability values of the broadening profile mapped to thickness.

    Returns:
        integral (float) : Simulated yield (Count/µC).
    """
    # Hydrogen concentration vector calculation from target
    cH_x, cH_y = cH_make(target)
    cH_fct = interp1d(cH_x, cH_y, kind='next', bounds_error=False, fill_value=0)

    # Broadening vector, but first defining left edges so interp1D can be used with kind next
    x_conv_TFU = np.array(x_conv_TFU)
    edges = np.empty_like(x_conv_TFU)
    edges[1:] = (x_conv_TFU[1:] + x_conv_TFU[:-1]) / 2
    edges[0] = x_conv_TFU[0] - (x_conv_TFU[1] - x_conv_TFU[0]) / 2
    broad = interp1d(edges, y_conv_TFU, kind='next', bounds_error=False, fill_value=0)

    # Setting up boundaries
    a = min(0,min(x_conv_TFU))
    b = max(x_conv_TFU)

    res = 0.1
    xa = np.arange(a,b+res,res)
    f1 = cH_fct(xa)
    f2 = broad(xa)
    area = sum(f1*f2) * res
    integral = area    

    return integral

def chi_squared_test(y_exp, y_sim):
    """
    Chi-squared test between the experimental and simulated excitation curves
    
    Parameters:
        y_exp (list of float): Yield from the experimental excitation curve (Count/µC).
        y_sim (list of float): Yield from the simulated excitation curve (Count/µC).

    Returns:
        chi_squared (float): chi-squared value  
    """
    chi_squared = sum(((ye - ys)) ** 2 for ye, ys in zip(y_exp, y_sim)) / len(y_exp)
    return chi_squared


if __name__ == "__main__":
    
    with open(r"D:\loudupon\OneDrive - Université de Namur\Documents\Mémoire (MA2)\Code\FRIA target 2.json",'r') as f:
        target_input = json.load(f)
        print('Loaded')

    x,y = cH_make(target_input)
    print(x,y)
    cH_fct = interp1d(x, y, kind='next', bounds_error=False, fill_value=0)
    x0 = np.linspace(0,max(x),500)
    y0 = cH_fct(x0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax = plt.step(x,y,where='pre',linewidth=2,color='tab:red')
    # plt.semilogy()
    plt.xlabel("x (TFU)", fontsize=16)
    plt.ylabel("H content (at. %)", fontsize=16)
    plt.xlim(left=0)
    plt.ylim(bottom=0.01)
    plt.ylim(top=max(y)+5)
    plt.grid()
    plt.grid(which='minor')
    highlight_ranges = list(zip(x[:-1], x[1:]))

    #labels = ['Matrice C', 'Matrice Ti','','','']

    ax = plt.gca()
    colors = ["#cfcfcf" if i % 2 == 0 else "#f0f0f0" for i, _ in enumerate(highlight_ranges)]

    # Changing the background of the graph
    for i, (start, end) in enumerate(highlight_ranges):
        ax.axvspan(start, end, color=colors[i % len(colors)], alpha=0.85)
        pass

    #legend_patches = [Patch(facecolor=colors[i], alpha=0.999, label=labels[i]) 
    #    for i in range(len(highlight_ranges))]
    
    # Add text labels above each step
    disp_y_shift = 1*max(y)/100
    for i in range(1,len(x)-1):
        x_mid = (x[i-1] + x[i]) / 2       # midpoint of the horizontal segment
        y_pos = y[i]                # slightly below the step
        plt.text(x_mid, y_pos+disp_y_shift, str(x[i]-x[max(i-1,0)])+" TFU", ha='center', va='bottom', fontsize=9)
        plt.text(x_mid, y_pos+5*disp_y_shift, str(y[i])+" %", ha='center', va='bottom', fontsize=12)

    # Adjust the last point: center relative to previous x
    x_last = (x[-2] + x[-1]) / 2  # midpoint between last two x
    y_last = y[-1]
    plt.text(x_last, y_last+disp_y_shift, str(x[-1]-x[-2])+" TFU", ha='center', va='bottom', fontsize=9)
    plt.text(x_last, y_last+5*disp_y_shift, str(y[-1])+" %", ha='center', va='bottom', fontsize=12)

    plt.show()