# HyProC

HyProC is a Python desktop application for modelling hydrogen concentration
profiles from resonant nuclear reaction analysis excitation curves. Build a
layered target, simulate its excitation curve, and compare it with experimental
measurements using plots and chi-squared history.

For the calculation models and detailed controls, see the
[user manual](manual/HyProC_Manual.pdf).

## Features

- Create, edit, save, and load layered targets and standards.
- Configure the reaction isotopes and resonance parameters.
- Calculate stopping cross sections with the bundled SCS-25-Solid model or an
  external SRIM installation.
- Configure beam broadening, Quantum Doppler, and straggling options.
- Import experimental excitation curves from Excel or text files.
- Normalize using a measured standard or a manually supplied K factor.
- Compare simulated and experimental curves, with an optional energy window
  for chi-squared evaluation.
- Save and restore simulation state and export simulated curve data.

## Installation

The instructions below use Windows PowerShell. SRIM integration requires an
external Windows SRIM installation; SRIM is not included in this repository.

You need Python 3.10 or newer with Tkinter, and Git if cloning from a terminal.
Alternatively, download and extract the repository ZIP from GitHub and open
PowerShell in the extracted folder.

```powershell
git clone https://github.com/LouisDupont-2/HyProC.git
cd HyProC
python -m venv .venv
```

Install the application dependencies in the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install numpy scipy pandas matplotlib periodictable xlwings openpyxl
```

Launch the application:

```powershell
.\.venv\Scripts\python.exe UI.py
```

These commands use the environment's Python directly, so activating the
environment is optional. The dependency list comes from the current source;
the repository does not yet provide a pinned dependency file.

## First-run settings

HyProC automatically creates `settings.json` from
[`settings.example.json`](settings.example.json) when the local file is missing.
Existing settings are preserved. The template starts with blank paths.

Open **Settings** and configure:

- **HyProC data save path:** an existing folder for calculation output.
- **SRIM Path:** the installation folder containing `SR Module`, if using the
  SRIM stopping model. This can remain blank when using SCS-25-Solid.
- **Column headers:** match the energy, yield, and yield uncertainty headers
  in your experimental data.

Your `settings.json` is ignored by Git. Edit the example file only when changing
the defaults distributed to new users.

## Basic workflow

1. Open **Reaction** and check the projectile, target isotope, and resonance
   parameters for your measurement.
2. Create or load the layered target.
3. Create or load a standard and enter its measured yield, or enter a manual
   K factor.
4. Choose the stopping model and calculation options.
5. Load an experimental excitation curve, or define a custom energy range.
6. Run the calculation and compare the curves. Adjust the target and options
   as needed, using the chi-squared history to track the comparisons.
7. Save the simulation to resume it later, or export the simulated curve.

See the [manual](manual/HyProC_Manual.pdf) for input formats, units, model
details, and the full workflow.

## Repository layout

| Path | Purpose |
| --- | --- |
| `UI.py`, `UI_geometry.py` | Application entry point and interface layout |
| `dialog_*.py` | Settings, reaction, import, and energy-range dialogs |
| `class_models.py` | Target, layer, and element models |
| `calc_stopping.py` | Stopping cross-section calculations |
| `calc_broadening.py`, `calc_curve.py` | Broadening and excitation-curve calculations |
| `data/` | Bundled stopping-model parameters |
| `settings_config.py`, `settings.example.json` | Local settings initialization and shared defaults |
| `manual/` | PDF manual, LaTeX sources, and [rebuild instructions](manual/README.md) |
| `tools/` | Supporting scripts |

## Documentation and license

- [User manual](manual/HyProC_Manual.pdf)
- [Changelog](CHANGELOG.md)
- [GNU General Public License, version 3](LICENSE)
