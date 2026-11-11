# Implementation Plan

**Session:** review excitation curve loading
**Date:** 2026-11-11T15:12:42.876Z
**Estimated effort:** 1 day

## Strategy

Build a testable importer, connect it to a conditional preview, then update and rebuild the manual.

## Tickets Overview

- **Ticket 1:** Read, identify and validate experimental curve data.
- **Ticket 2:** Add conditional preview and apply validated curves to the GUI.
- **Ticket 3:** Document import and verify the manual build.

## Sequencing Rationale

The GUI uses the tested importer. The manual describes the resulting flow.

## Risks & Mitigation

- **Risk:** A plausible guess can misidentify measurements. → **Mitigation:** Require confirmation for ambiguous mappings and test that failed imports preserve the loaded curve.

## Assumptions

- Existing recognized layouts retain automatic import. Uncertainty is optional.
