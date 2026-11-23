# Session: add off-resonance cross section to broadening

**Date:** 2026-11-20T13:29:00.727Z
**Status:** Grill phase complete

## Problem Statement

Include the configured off-resonance cross section when calculating excitation curves.

## Context & Constraints

- **Current behavior:** The Lorentzian alone contributes to broadening; simulation validation and GUI document creation omit the off-resonance setting.
- **Pain point:** A nonzero flat off-resonance cross section has no effect on the calculated yield.
- **Dependencies:** Preserve saved simulation compatibility; missing off-resonance values default to zero. Preserve the existing Sigma interpretation as the Lorentzian peak above the baseline.
- **Tech stack:** Python, NumPy, SciPy, Tkinter, JSON.

## Success Metrics

- The off-resonance cross section in barn contributes uniformly throughout the target, including outside the existing finite broadening grid.
- The same contribution is included in standard normalization and in target calculations.
- Old settings and simulations without the field retain zero-baseline behavior, and the field survives simulation save/load.

## Architecture & Approach

Carry the `Off-resonance` resonance setting through simulation documents and validation. Add its uniform contribution to the yield calculation over the entire target, alongside the broadened Lorentzian, and ensure diagnostic output accurately represents the cross section.

## Assumptions & Trade-offs

The baseline is constant in energy and measured in barn. Sigma remains the amplitude of the Lorentzian above this baseline. The baseline applies to both the standard and the target.

## Open Questions

None.

## Notes

The existing broadening grid is finite, so adding a constant only to that grid would omit contributions from parts of the target outside the grid.
