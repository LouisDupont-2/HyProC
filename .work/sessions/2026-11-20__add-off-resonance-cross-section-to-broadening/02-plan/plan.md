# Implementation Plan

**Session:** add off-resonance cross section to broadening
**Date:** 2026-11-20T13:30:22.919Z
**Estimated effort:** 3 hours

## Strategy

Implement the setting, full-target baseline contribution, and regression coverage together as one reviewable change.

## Tickets Overview

- **Ticket 1:** Include the off-resonance cross section in target and standard yields, preserving old simulations.

## Sequencing Rationale

The setting and its calculation form one behavior and should be verified together.

## Risks & Mitigation

- **Risk:** The finite broadening grid truncates a flat baseline. → **Mitigation:** Integrate its contribution across the full target independently of the finite Lorentzian grid.
- **Risk:** Existing simulation documents lack the field. → **Mitigation:** Default missing values to zero and test compatibility.

## Assumptions

- The baseline is a nonnegative cross section in barn; Sigma is the Lorentzian peak above the baseline.
- The same physics applies to the standard and the target.
