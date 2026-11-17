# Session: Traditional Python project and JOSS readiness

**Date:** 2026-11-16T14:24:24.895Z
**Status:** Grill phase complete

## Problem Statement

Restructure HyProC as a conventional installable Python desktop application and prepare it for JOSS review. Make a saved simulation runnable from the GUI, Python, and the terminal.

## Context & Constraints

- **Current behavior:** The Tkinter application coordinates numerical calculations, settings, and version 1 simulation JSON. Calculation modules read reaction settings at import time.
- **Pain point:** Users install dependencies manually and need the GUI to run a simulation. The calculation cannot yet be verified through the planned Python and terminal entry points.
- **Dependencies:** Preserve existing settings and saved simulations. The reference workflow uses bundled SCS-25-Solid data and can run without SRIM. Maintain support for existing SRIM workflows.
- **Tech stack:** Python, Tkinter, NumPy, SciPy, Matplotlib, and GitHub Actions.

## Success Metrics

- A fresh install includes the required resources and can launch the GUI or run a saved simulation through the documented Python and CLI entry points.
- A simulation JSON stays complete across saving, opening, and rerunning. The calculation can repeatedly run from explicit inputs without changing the input model.
- After the Python and CLI paths are available, rerun both fixtures independently against the captured curves and segment counts. Then build the common regression suite and generate a short report once the user approves checkpoints, reference data, and tolerances.
- Document installation, contribution, support, and an approved worked example. Prepare the JOSS manuscript with evidence of research use and AI disclosure.

## Architecture & Approach

Use pyproject.toml and src/hyproc. Keep the existing Tkinter desktop experience and give it a hyproc launcher. Share a simulation JSON reader and writer and one calculation entry point among the GUI, Python scripts, and hyproc simulate. The simulation function uses explicit inputs and returns results without GUI or file-writing side effects. Preserve the saved target, reaction, normalization, options, energy range, and embedded experimental data. Compare the refactored implementation with the pre-refactor captures before formalizing tests.

## Assumptions & Trade-offs

The formal suite follows working Python and CLI interfaces. Both fixtures use the same independently runnable checks. The existing segmentation rule checks the candidate at each original layer's entry energy. Expanding the check to all segments, adding an optimizer or hyproc fit, and settling fit-specific fields are future work. A future fitted JSON should be rerunnable with the fitted target, embedded data, and fit instructions carried forward.

## Open Questions

The user will select or approve intermediate checkpoints, references, and tolerances after the post-refactor comparison. Sharing of the measured fixture remains undecided. JOSS research impact and authorship details need confirmation for the manuscript.

## Notes

Candidate baselines were captured independently before refactoring. The synthetic example has 126 points and 32 segments at 420 keV. The local measured-data example matched all 321 previously saved yields and gave segment counts of 1, 1, and 2. The measured fixture and capture are Git-ignored. The repository has been public since September 2025 according to the user.
