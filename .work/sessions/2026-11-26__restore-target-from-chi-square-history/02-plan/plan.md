# Implementation Plan

**Session:** restore target from chi-square history
**Date:** 2026-11-26T15:58:08.850Z
**Estimated effort:** 3 hours

## Strategy

Implement aligned, independent target snapshots and persistence together with the row-click restore interaction, then verify history, loading, and selection behavior.

## Tickets Overview

- **Ticket 1:** Record and restore calculation targets from chi-squared history.

## Sequencing Rationale

Snapshot storage, persistence, and interaction form one user-visible behavior and should be verified together.

## Risks & Mitigation

- **Risk:** Snapshot and history entries become misaligned or old files fail to load. → **Mitigation:** Validate complete data before applying it, handle missing legacy snapshots, and test scrolling, persistence, and reset.
- **Risk:** Restoring or editing a target mutates a saved snapshot. → **Mitigation:** Copy snapshots independently when recording and restoring.

## Assumptions

- Only the target is restored; existing calculation settings and history remain intact.
- Previously existing worktree changes must be preserved.
