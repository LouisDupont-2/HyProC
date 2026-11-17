---
bump: minor
floor: minor
inUnreleased: true
---
### Added

- Run a saved simulation from Python or with `hyproc simulate`. The terminal command writes a full simulation JSON that the desktop app can reopen.

### Changed

- Install HyProC and its dependencies with pip. Open the desktop app with `hyproc` or run `run_hyproc.py` from the checkout. The installed command uses settings in the current directory, and the checkout launcher uses settings beside the script.
- New desktop sessions default to the Bohr straggling model. Saved simulations retain their selected model.
