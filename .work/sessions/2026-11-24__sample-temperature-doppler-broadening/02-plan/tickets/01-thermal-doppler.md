# Ticket 01: thermal-doppler

**Model:** inherit
**Effort:** high

**Acceptance Criteria:**
- [ ] Add target temperature above beam width and standard temperature in the Standard section; both display 20 °C on launch and for legacy files without temperatures.
- [ ] Disable the standard temperature entry when a K factor is entered, retain its value, and ignore it during calculations with a K factor.
- [ ] Calculate thermal Doppler broadening from temperature, resonance energy and projectile and reacting-nucleus isotope masses; combine its variance with existing Gaussian variances independently of Quantum Doppler, using the appropriate temperature for standard and target.
- [ ] Persist temperatures and validate finite numeric temperatures at or above -273.15 °C; report field-specific errors, validate applicable values in headless simulation, and reject invalid saved values before replacing session state.
- [ ] Verify the formula numerically, zero at absolute zero, quadrature, temperature selection, legacy defaults, persistence, validation, and disabled field behavior.

**Files to Touch:**
- `src/hyproc/calc_broadening.py`
- `src/hyproc/simulation.py`
- `src/hyproc/UI.py`
- `src/hyproc/UI_geometry.py`
- `tests/`

**Verification Step:**

Run:
```bash
.venv/Scripts/python -m unittest discover -s tests
```

Expected:
The test suite passes, including focused thermal broadening, simulation compatibility and GUI behavior checks.

**Notes:**

Use the repository's existing test runner if discovery requires a different invocation. Check physical units and the reference before implementing.
