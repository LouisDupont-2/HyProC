# Session: review excitation curve loading

**Date:** 2026-11-11T15:07:39.178Z
**Status:** Grill phase complete

## Problem Statement

HyProC should import experimental excitation curves from more layouts without silently losing measurements or mapping unrelated columns.

## Context & Constraints

- **Current behavior:** Excel matches configured headers and prompts for multiple matching tables. CSV and TXT can fall back to positional columns.
- **Pain point:** Headerless CSV loses its first sample, Excel fails without an uncertainty column, and positional guessing can choose the wrong columns.
- **Dependencies:** Preserve existing supported import flows and the HyProC curve representation.
- **Tech stack:** Python, pandas and Tkinter.

## Success Metrics

- Import automatically when a single table and the energy and yield mapping are clear. Uncertainty is optional.
- When the sheet, table or columns are ambiguous, show sample rows and let the user choose. Headerless CSV or TXT with three numeric columns opens the preview unless its mapping is known.
- Retain the first headerless data row, sort valid points by energy, and keep the previous curve when import fails or is cancelled.

## Architecture & Approach

Read the source and identify candidate tables and mappings before changing the app state. When selection is needed, show the sheet, table and sample values with controls for energy, yield and optional uncertainty. Validate and sort the selected data before applying it to the plot.

## Assumptions & Trade-offs

Use configured headers as a known mapping and keep the automatic path for recognizable files. A positional mapping for three unnamed columns needs user confirmation unless the layout is known.

## Open Questions

None for the approved scope.

## Notes

Update the user manual for the preview workflow and verify the documented file support.
