# Session: sample temperature Doppler broadening

**Date:** 2026-11-24T15:57:29.946Z
**Status:** Grill phase complete

## Problem Statement

Account for temperature-dependent Doppler broadening from thermal motion when simulating excitation curves.

## Context & Constraints

- **Current behavior:** Gaussian broadening combines beam width, quantum Doppler broadening and straggling; temperatures are not recorded.
- **Pain point:** Thermal motion of the reacting target nuclei is omitted.
- **Dependencies:** Preserve version-1 simulation compatibility and support both GUI and headless simulation; use the reaction isotope masses.
- **Tech stack:** Python, Tkinter, NumPy and periodictable.

## Success Metrics

- A target temperature entry in °C appears in Options above beam width; a separate standard temperature entry appears in the Standard section. Both visibly default to 20 at launch and when older files lack values.
- The standard temperature entry is disabled when a K factor is entered, retains its value, and is ignored in that case.
- Thermal Doppler standard deviation uses the applicable temperature and reaction isotope masses and is combined in quadrature independently of the existing Quantum Doppler option for target and standard calculations.
- Values must be finite numbers at or above -273.15 °C; invalid applicable values produce a descriptive error before calculation. Invalid saved values are rejected before replacing session state. Headless simulation applies equivalent calculation validation.
- Temperatures persist in saved simulations and old files remain loadable.

## Architecture & Approach

Add and persist separate target and standard temperature fields; pass the applicable temperature and isotope masses through the shared simulation to thermal broadening. Use the standard temperature during standard normalization unless a manual K factor is used. Combine thermal and existing Gaussian contributions in quadrature.

## Assumptions & Trade-offs

Both temperatures default to 20 °C, including when absent from older simulations. Absolute zero is allowed and yields zero thermal broadening. Quantum Doppler remains independently controlled.

## Open Questions

None.

## Notes

Temperature errors identify the field; disabled standard temperature retains its value for use when the K factor is cleared.
