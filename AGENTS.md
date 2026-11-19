# HyProC

Python Tkinter app simulating resonant-NRA excitation curves for layered targets.

## Commands

```bash
.venv/Scripts/python -m pip install -e .          # setup
.venv/Scripts/hyproc                              # run the app
```

## Glossary

- **Beam ion / projectile**: The incident ion, identified by atomic number `Z1`
  and mass number `A1`.
- **Profiled element**: The target element of interest, identified by atomic
  number `Z2` and mass number `A2` in the reaction settings.
- **Target**: The sample being modeled, represented as an ordered set of layers.
  Each layer has an areal density and a composition.
  _Avoid_: sample
- **Resonance parameters**: `E_R` is the resonance energy (in keV), `Gamma` its width (in keV),
  and `Sigma` the peak cross section (in barn).
- **Areal density**: Number of atoms per unit area. Layer thickness is expressed
  in TFU, where 1 TFU = 10¹⁵ atoms/cm².
- **Stopping cross section**: The quantity used to calculate the beam's energy
  loss through a layer, expressed in keV/TFU.
  _Avoid_: Stopping power
- **Excitation curve**: Reaction yield as a function of incident beam energy;
  HyProC compares simulated and experimental curves.
  _Avoid_: spectrum
- **Standard**: A reference target with a measured yield, used to determine the
  simulation's normalization factor.
- **K factor**: The experimental setup efficency. It takes into account the 
  solid angle of the detector and its intrinsic detection efficiency. Max value of 4*pi (12.57)
  _Avoid_: calibration factor, efficiency

## Domain gotchas

- Energy is expressed in keV and composition in at. %.
- `assign_stopping` deep-copies the target and returns a new target with layers split into
  sub-layers for stopping accuracy. The shared simulation uses that returned target locally.

## Code gotchas

- `simulation.py` provides the shared headless workflow. The CLI calls `simulate()` with a saved
  simulation dictionary; the GUI calls `_simulate()` with additional calculation options.
- Reaction and resonance settings are dictionaries. The GUI reads them from settings and includes
  them in simulation documents; the shared simulation validates the document's values.
- `settings_config.ensure_settings()` creates `settings.json` in the current working directory by
  default, seeded from `src/hyproc/settings.example.json`. An explicit path can be supplied.
- `GUI_App` in `UI.py` owns GUI state and plotting; `UI_geometry.py` constructs interface sections.
  Calculations run in a worker thread that currently accesses Tk widgets.
- `simulation_io.py` handles version-1 simulation JSON, `curve_import.py` handles curve imports,
  and `UI.py` handles target loading and saving.
  Preserve key names, optional-field defaults, old point-count ranges and extension fields.
  Parse completely before replacing session state.
- `Element` / `Layer` / `Target` subclass `dict` so they serialise straight to the save-file JSON;
  keep new fields JSON-compatible.
- SRIM is Windows-only: it writes `SR.IN` and runs `SRModule.exe` with child-process
  `cwd=<SRIM_path>/SR Module`. Keep the application's cwd unchanged. Calls share a process-local
  lock because SRIM uses fixed filenames. Use `"SCS-25-Solid"` or fake processes in tests.
- Use `resources.find_resource()` to locate shared files in a checkout or installed package.
  The settings template is handled separately by `settings_config.py`.

## Repo

`origin` points to `LouisDupont-2/HyProC`.

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues for LouisDupont-2/HyProC.
See docs/agents/issue-tracker.md.

### Triage labels

Use the default Matt Pocock triage labels.
See docs/agents/triage-labels.md.

### Domain docs

This is a single-context project; its glossary is in AGENTS.md.
See docs/agents/domain.md.
