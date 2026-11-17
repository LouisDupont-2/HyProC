# Ticket 02: share-simulation-core

**Status:** ✅ Done

## Local Test Result

All 14 existing tests passed. A separate three-point SCS-25-Solid smoke input produced identical GUI and Python energy and yield arrays. The Python call left its input unchanged and did not import Tkinter.

## Review Notes

Base: af25887e2599e1cd033b15e61dcebf26d715db51. Exclude existing fixture, ignore, and manual source changes. Overlapping UI edits and manual PDF are backed up from ticket 01 and will be accounted for before returning the workspace.

Reviewed the stopping and broadening parameter flow and left the segmentation calculation intact. Standard normalization is now explicit and the old default on the GUI-only standard calculation method is superseded by the required model in shared calculation inputs.

## Blockers / Challenges

External SRIM is not configured for smoke verification. It still uses its own input and output files under its installation path.

## Commits

- c3442e1 refactor: share the HyProC simulation engine (ticket 02)

## Time Spent

5m (ticket-start.js to ticket-complete.js)
