# Implementation Plan

**Session:** sample temperature Doppler broadening
**Date:** 2026-11-24T16:03:53.043Z
**Estimated effort:** 1 day

## Strategy

Implement the approved thermal broadening, GUI inputs, persistence, and validation together so the feature is usable and verifiable end to end.

## Tickets Overview

- **Ticket 1:** Add temperature-dependent Doppler broadening and separate target and standard temperature controls.

## Sequencing Rationale

The shared calculation and its GUI and saved-document inputs form one connected behavior and can be reviewed as one change.

## Risks & Mitigation

- **Risk:** Incorrect physics units or mass handling → **Mitigation:** Verify the formula against a primary reference and add numerical checks with known inputs.
- **Risk:** Old simulations change or fail unexpectedly → **Mitigation:** Apply the approved 20 °C defaults and test legacy loading and headless execution.
- **Risk:** Invalid saved values partially replace session state → **Mitigation:** Validate before updating widgets and test rejection.

## Assumptions

- Target and standard temperatures default to 20 °C, including for old saved simulations.
- The standard temperature is ignored when a manual K factor is supplied; thermal and Quantum Doppler contributions are independent.
