# Ticket 01: restore-history-target

**Effort:** high

**Acceptance Criteria:**
- [ ] Each recorded chi-squared entry has an independent snapshot of the target used in the corresponding calculation.
- [ ] Clicking an occupied visible row, including bar, value label, and surrounding area, selects the correct entry even after scrolling; confirmation restores its target and cancellation leaves state unchanged.
- [ ] Saving and loading a simulation preserves target history; legacy entries without snapshots remain visible and show that restoration is unavailable.
- [ ] Resetting history clears associated snapshots; invalid saved snapshots are rejected before replacing session state.

**Files to Touch:**
- `src/hyproc/UI.py`
- `src/hyproc/UI_geometry.py`
- `tests/` (appropriate existing or new tests)

**Verification Step:**

Run:
```bash
.venv/Scripts/python -m unittest discover -s tests
```

Expected:
All relevant tests pass, including coverage of snapshot independence, persistence, row selection, confirmation, and legacy history.

**Notes:**

Check the repository's test runner and use the equivalent supported command if necessary. Preserve pre-existing user edits and all existing simulation compatibility requirements.
