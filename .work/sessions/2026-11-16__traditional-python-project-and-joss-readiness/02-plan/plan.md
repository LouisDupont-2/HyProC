# Implementation Plan

**Session:** Traditional Python project and JOSS readiness
**Date:** 2026-11-17T11:22:36.978Z
**Estimated effort:** 3–5 working days

## Strategy

Package HyProC, extract the simulation calculation and JSON I/O from the GUI, then expose the shared path through the terminal. This narrowed plan supersedes the earlier testing and JOSS deliverables in the design record.

## Tickets Overview

- **Ticket 1:** Package the desktop app and its resources.
- **Ticket 2:** Extract the shared simulation engine and JSON I/O.
- **Ticket 3:** Add the simulate command and document basic usage.

## Sequencing Rationale

Package resources first, then connect the GUI and Python API to the shared calculation path. The terminal command reuses the engine and JSON I/O.

## Risks & Mitigation

- **Risk:** Installed resource paths and existing simulation files could break. → **Mitigation:** Verify a clean installation and check that a version 1 save can open and rerun.

## Assumptions

- The current scientific calculations remain in scope as existing behavior to preserve. Fitting and changes to segmentation are future work.
- The two designed cases, pre-refactor comparisons, formal regression suite, CI expansion, verification reports, and JOSS materials are deferred. Preserve the existing local captures for later use.
