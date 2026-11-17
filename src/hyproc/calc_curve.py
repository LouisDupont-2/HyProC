import numpy as np
from scipy.interpolate import interp1d
from numpy.typing import NDArray
from .class_models import Target

def cH_make(target: Target, Z2: int)-> tuple[list[float], list[float]]:
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
    for i, layer in enumerate(target["layers"]):
        value += layer["areal_density"]
        cH_x[i+1] = value
    cH_y = []
    for layer in target["layers"]:
        z1_fraction = sum(elem["percent_at"] for elem in layer["elements"] if elem["Z"] == Z2) 
        cH_y.append(z1_fraction)
    cH_y.insert(0, 0.0) # Inserting 0.0 at index 0

    return cH_x, cH_y

# Calculating yield
def compute_yield(target: Target, x_conv_TFU: NDArray[np.float64], y_conv_TFU: NDArray[np.float64], Z2: int)-> float:
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
    cH_x, cH_y = cH_make(target, Z2)
    cH_fct = interp1d(cH_x, cH_y, kind='next', bounds_error=False, fill_value=0)

    # Broadening vector, but first defining left edges so interp1D can be used with kind next
    x_conv_TFU = np.asarray(x_conv_TFU, dtype=float)
    y_conv_TFU = np.asarray(y_conv_TFU, dtype=float)

    if x_conv_TFU.ndim != 1 or y_conv_TFU.ndim != 1 or x_conv_TFU.size != y_conv_TFU.size:
        raise ValueError("Broadening arrays must be one-dimensional and have the same length.")
    #if x_conv_TFU.size < 2:
    #    return 0.0
    if not np.all(np.isfinite(x_conv_TFU)) or not np.all(np.isfinite(y_conv_TFU)):
        n_bad_x = np.sum(~np.isfinite(x_conv_TFU))
        n_bad_y = np.sum(~np.isfinite(y_conv_TFU))
        raise ValueError(f"Broadening arrays contain non-finite values: {n_bad_x} in x, {n_bad_y} in y.")

    # Ensure x values are sorted and unique for interp1d
    #order = np.argsort(x_conv_TFU)
    #x_conv_TFU = x_conv_TFU[order]
    #y_conv_TFU = y_conv_TFU[order]
    #unique_x, unique_indices = np.unique(x_conv_TFU, return_index=True)
    #if unique_x.size != x_conv_TFU.size:
    #    x_conv_TFU = x_conv_TFU[unique_indices]
    #    y_conv_TFU = y_conv_TFU[unique_indices]
    #if x_conv_TFU.size < 2:
    #    return 0.0

    edges = np.empty_like(x_conv_TFU)
    edges[1:] = (x_conv_TFU[1:] + x_conv_TFU[:-1]) / 2
    edges[0] = x_conv_TFU[0] - (x_conv_TFU[1] - x_conv_TFU[0]) / 2
    broad = interp1d(edges, y_conv_TFU, kind='next', bounds_error=False, fill_value=0)

    # Setting up boundaries
    a = min(0.0, float(np.min(x_conv_TFU)))
    b = float(np.max(x_conv_TFU))
    if b <= a:
        return 0.0

    res = float(np.min(np.diff(np.sort(x_conv_TFU))))  # use native spacing
    xa = np.arange(a, b + res, res)
    f1 = cH_fct(xa)
    f2 = broad(xa)
    area = float(np.sum(f1 * f2) * res)
    if not np.isfinite(area):
        raise ValueError("Computed yield integral is not finite.")

    return area

def chi_squared_test(x_exp: list[float], y_exp: list[float], x_sim: list[float], y_sim: list[float]) -> float:
    """
    Chi-squared test between the experimental and simulated excitation curves.

    Parameters:
        x_exp (list of float): Energy values for the experimental excitation curve.
        y_exp (list of float): Yield from the experimental excitation curve (Count/µC).
        x_sim (list of float): Energy values for the simulated excitation curve.
        y_sim (list of float): Yield from the simulated excitation curve (Count/µC).

    Returns:
        chi_squared (float): chi-squared value
    """
    try:
        x_exp = np.asarray(x_exp, dtype=float)
        y_exp = np.asarray(y_exp, dtype=float)
        x_sim = np.asarray(x_sim, dtype=float)
        y_sim = np.asarray(y_sim, dtype=float)

        if x_exp.ndim != 1 or y_exp.ndim != 1 or x_sim.ndim != 1 or y_sim.ndim != 1:
            return -1.0

        if x_exp.size != y_exp.size:
            return -1.0

        exp_order = np.argsort(x_exp)
        sim_order = np.argsort(x_sim)
        x_exp = x_exp[exp_order]
        y_exp = y_exp[exp_order]
        x_sim = x_sim[sim_order]
        y_sim = y_sim[sim_order]

        if x_exp.size == x_sim.size and np.allclose(x_exp, x_sim, rtol=0.0, atol=1e-12):
            y_sim_interp = y_sim
        else:
            y_sim_interp = np.interp(x_exp, x_sim, y_sim, left=np.nan, right=np.nan)

        valid = np.isfinite(y_exp) & np.isfinite(y_sim_interp)
        if not np.any(valid):
            return -1.0

        chi_squared = np.mean((y_exp[valid] - y_sim_interp[valid]) ** 2)
        return float(chi_squared)
    except Exception:
        return -1.0
