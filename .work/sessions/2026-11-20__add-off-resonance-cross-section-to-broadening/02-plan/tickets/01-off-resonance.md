# Ticket 01: off-resonance

**Model:** inherit
**Effort:** high

**Acceptance Criteria:**
- [ ] The `Off-resonance` setting is preserved in simulation documents, validated, and defaults to zero when absent.
- [ ] The baseline contributes uniformly over the full profiled-element content of target and standard, including outside the broadening grid.
- [ ] Zero baseline preserves existing results, and diagnostics represent the cross section consistently.
- [ ] Regression coverage verifies nonzero and zero baselines, full-target contribution, normalization, and invalid values.

**Files to Touch:**
- `src/hyproc/simulation_io.py`
- `src/hyproc/simulation.py`
- `src/hyproc/calc_curve.py`
- `src/hyproc/calc_broadening.py`
- `src/hyproc/UI.py`
- `src/hyproc/settings.example.json`
- `tests/`

**Verification Step:**

Run:
```bash
.venv/Scripts/python -m unittest discover -s tests
```

Expected:
All applicable tests pass; GUI tests may skip when no display is available.

**Notes:**

Preserve extension fields and version-1 simulation compatibility. Check whether reaction settings need a user-visible control and keep diagnostics physically consistent.
