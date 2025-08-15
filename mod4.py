import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.interpolate import interp1d
from scipy.signal import convolve
import json

# Creating the hydrogen profile from the target
def cH_make(target):
    cH_x = np.zeros(len(target["layers"])+1)
    value = 0.0
    for i in range(len(target["layers"])):
        value += target["layers"][i]["areal_density"]
        cH_x[i+1] = value
    cH_y = []
    for layer in target["layers"]:
        z1_fraction = sum(elem["percent_at"] for elem in layer["elements"] if elem["Z"] == 1) 
        cH_y.append(z1_fraction)
    cH_y.insert(0, 0.0)

    return cH_x, cH_y

# Calculating yield
def compute_yield(target, x_conv_TFU, y_conv, H_std=None, Y_sample=None, S_sample=None):
    # Hydrogen concentration vector calculation from target
    cH_x, cH_y = cH_make(target)
    cH_fct = interp1d(cH_x, cH_y, kind='next', bounds_error=False, fill_value=0)

    # Broadening vector, but first defining left edges so interp1D can be used with kind next
    x_conv_TFU = np.array(x_conv_TFU)
    edges = np.empty_like(x_conv_TFU)
    edges[1:] = (x_conv_TFU[1:] + x_conv_TFU[:-1]) / 2
    edges[0] = x_conv_TFU[0] - (x_conv_TFU[1] - x_conv_TFU[0]) / 2
    broad = interp1d(edges, y_conv, kind='next', bounds_error=False, fill_value=0)

    # Setting up boundaries
    a = min(0,min(x_conv_TFU))
    b = max(x_conv_TFU)

    xa = np.arange(a,b+1,1)
    f1 = cH_fct(xa)
    f2 = broad(xa)
    area = sum(f1*f2)
    integral = area    

    return integral

def chi_squared_test(y_exp, y_sim):
    chi_squared = sum(((ye - ys)) ** 2 for ye, ys in zip(y_exp, y_sim)) / len(y_exp)
    return chi_squared


if __name__ == "__main__":
    with open(r"C:\Users\louis\OneDrive - Université de Namur\Documents\Mémoire (MA2)\OwnCode\target_data.json",'r') as f:
        target_input = json.load(f)
        print('Loaded')

    x,y = cH_make(target_input)
    print(x,y)
    cH_fct = interp1d(x, y, kind='next', bounds_error=False, fill_value=0)
    x0 = np.linspace(0,max(x),500)
    y0 = cH_fct(x0)
    fig, ax = plt.subplots()
    ax = plt.step(x,y,where='pre')
    ax = plt.plot(x0,y0, label='interp')
    plt.legend()
    plt.show()