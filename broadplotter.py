import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def load_and_plot(filename, delimiter='\t'):
    """
    Load two-column data from a .txt file and plot it.

    Parameters:
        filename (str): Path to the text file.
        delimiter (str): Column separator (default is tab).
    """
    x_vals = []
    y_vals = []

    with open(filename, 'r') as f:
        for line in f:
            if line.strip():  # skip empty lines
                parts = line.strip().split(delimiter)
                if len(parts) == 2:
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        x_vals.append(x)
                        y_vals.append(y)
                    except ValueError:
                        print(f"Skipping invalid line: {line.strip()}")

    for i,x in enumerate(x_vals):
        if None or x < 0:
            y_vals[i]=0

    # Plotting
    plt.rcParams.update({'font.size': 14})
    plt.figure(figsize=(8, 6))
    plt.plot(x_vals, y_vals, marker='o', linestyle='-')
    if filename.endswith("TFU.txt"):
        plt.xlabel("x (TFU)")
    else:
        plt.xlabel("E (keV)")
    if filename.endswith("xsec.txt"):
        plt.ylabel("Cross section (mb)")
    else:
        plt.ylabel("Probability")

    plt.grid(True)
    plt.tight_layout()
    plt.show()

file = r'C:\HyProC\Session 2025-09-12 13-40-52\Run 27\datapoint19/Total Broadening stepped.txt'

load_and_plot(file)