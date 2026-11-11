# Changelog

## Unreleased

### Added

- Added an excitation-curve preview for ambiguous imports. Choose the sheet, table, and columns after inspecting sample rows.

### Fixed

- Preserve the first measurement in headerless CSVs and leave the loaded curve in place when an import fails or is cancelled.
- Allow Excel imports without an uncertainty column and support legacy .xls workbooks with xlrd.

## 5 November 2026

### Added

- Added `settings.example.json` with blank SRIM and data save paths. HyProC automatically creates a local `settings.json` from this template when missing, preserving existing user settings.
- Added a **Reaction** menu and dialog for editing projectile and target isotope numbers (`Z1`, `A1`, `Z2`, `A2`) and resonance energy, width, and peak cross-section (`E_R`, `Gamma`, `Sigma`). Confirm validates and saves the values to `settings.json`, then reloads the calculation modules; Cancel discards the edits.
- Added a manual K-factor input. A finite, positive value bypasses the standard-based K calculation and disables the standard controls. The input retains its entered precision for calculations while displaying at most nine decimal places after focus leaves the field.
- Added a **None** straggling option.
- Added persistence of reaction and resonance settings and the manual K factor in simulation JSON files. Simulation loading restores these settings, curves, target and standard data, calculation options, energy-range information, and chi-squared history. Older simulation files without reaction/resonance fields remain supported.

### Changed

- Renamed the manual PDF to `manual/HyProC_Manual.pdf`, grouped LaTeX sources and figures under `manual/source/`, and excluded temporary build files from Git. Updated the application's manual link and added rebuild instructions.
- Made the standard areal density 1750 TFU and changed standard-based K evaluation to use `E_R + 100 * Gamma`.
- Kept the user-defined target separate from the internally segmented calculation target. Stopping segmentation remains in effect for calculations, while the target editor and target/simulation saves preserve the original layer list.
- Refactored `assign_stopping()`. The target shown to the user remains the same regardless of any segmentation to keep stopping cross sections accurate.
- Changed the default stopping model to **SCS-25-Solid** and renamed the Doppler checkbox **Quantum Doppler**.
- Expanded the energy-range dialog to define a range by minimum, maximum, and step size, and to reuse current simulated energies. The run menu offers normal, custom-range, and loaded-curve-energy calculations; energy offsets are applied during calculation and reversed for display.
- Added elapsed-time output after successful calculations.
- Reorganized calculation modules as `calc_stopping.py`, `calc_broadening.py`, and `calc_curve.py`, and dialog modules as `dialog_energy_range.py`, `dialog_import.py`, `dialog_reaction.py`, and `dialog_settings.py`.
- Updated the local resonance energy and width in `settings.json`.
- Moved `broadplotter.py` to `tools` folder.

### Fixed

- Reject blank SRIM and data save paths before calculations, prompting users to configure their paths in Settings.
- Fixed **Load Sim curve as Exp curve** to copy both simulated energies and yields into the experimental curve and assign zero uncertainties.
- Fixed `assign_stopping()`. Previously, segmenting a thick layer could cause the total areal density of the target to change.
- Fixed **Remove experimental curve** and **Remove simulated curve** so it doesn't unnecessarily rescale the x-axis if no curve was to be plotted.
