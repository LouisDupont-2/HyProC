# Session: restore target from chi-square history

**Date:** 2026-11-26T15:43:31.528Z
**Status:** Grill phase complete

## Problem Statement

Let users recover the target associated with a calculation from the chi-squared history graph.

## Context & Constraints

- **Current behavior:** History records chi-squared values and energy bounds but does not retain corresponding targets.
- **Pain point:** Users cannot restore a previous calculation's target from its history row.
- **Dependencies:** Preserve existing simulation files and their history; target snapshots must survive saving and reopening a simulation.
- **Tech stack:** Python, Tkinter, Matplotlib, JSON simulation documents.

## Success Metrics

- Each calculation that adds a chi-squared history entry records the target used for that calculation.
- Clicking an occupied history row asks for confirmation and restores the corresponding target when confirmed; clicking the bar, its value text, or surrounding row space works.
- Saved and reopened simulations retain snapshots; older history entries without snapshots remain visible and report restoration unavailable.

## Architecture & Approach

Keep independent target snapshots aligned with chi-squared entries. Map a click's visible row to its history entry, accounting for scrolling, then confirm and restore that snapshot. Persist the snapshots as an optional simulation document field and refresh the target editor after restoration.

## Assumptions & Trade-offs

Restore the target only. Existing history without snapshots cannot reconstruct previous targets. Empty plot rows do not trigger restoration.

## Open Questions

None.

## Notes

The clickable region should be forgiving and include the histogram bar, adjacent value text, and some surrounding space.
