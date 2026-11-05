# Session: make a readme

**Date:** 2026-11-05T15:43:05.153Z
**Status:** Grill phase complete

## Problem Statement

Add a root README so people downloading HyProC can understand the application and get started.

## Context & Constraints

- **Current behavior:** The repository includes a detailed PDF manual and its sources, but no root README.
- **Pain point:** Installation, launch, and first-run settings are not explained at the repository entry point.
- **Dependencies:** Preserve application behavior and existing documentation; derive instructions from the source.
- **Tech stack:** Python, Tkinter, NumPy, SciPy, pandas, Matplotlib, periodictable, xlwings, and openpyxl.

## Success Metrics

- A root README explains setup and launching UI.py on Windows.
- First-run configuration describes blank local paths and optional SRIM setup accurately.
- Local documentation links resolve and the README provides a basic scientific workflow.

## Architecture & Approach

One English Markdown README covering purpose, prerequisites, installation, local settings, usage, repository layout, manual, changelog, and license.

## Assumptions & Trade-offs

Small documentation-only work on the current branch, with no plan, session branch, or PR. Installation instructions list the dependencies used by the code without claiming a tested clean installation.

## Open Questions

N/A.

## Notes

The user requested a README through GPS. Keep scientific detail in the existing manual and personal paths out of documentation.
