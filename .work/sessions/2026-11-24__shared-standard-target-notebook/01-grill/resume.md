# Session: shared standard target notebook

**Date:** 2026-11-24T14:59:37.806Z
**Status:** Grill phase complete

## Problem Statement

The target and standard notebook tabs need an identical layout built from shared UI code.

## Context & Constraints

- **Current behavior:** The target tab has layer and element controls; the standard tab has only element controls.
- **Pain point:** Their layouts differ and element UI construction is duplicated.
- **Dependencies:** Preserve existing target and standard element callbacks and behavior.
- **Tech stack:** Python and Tkinter/ttk.

## Success Metrics

- Both notebook tabs use the same reusable layout class.
- The standard layer list, layer buttons, and areal-density field are visible but disabled.
- Target controls and standard element editing retain their existing behavior.

## Architecture & Approach

Construct both tabs using one reusable class, configured with their existing callbacks and with layer controls disabled for the standard.

## Assumptions & Trade-offs

The standard continues to use its existing single-layer model. This is a UI refactor, not a change to simulation or persistence.

## Open Questions

None.

## Notes

The user approved this design.
