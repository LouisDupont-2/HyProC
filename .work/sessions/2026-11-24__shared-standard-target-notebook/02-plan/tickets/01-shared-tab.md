# Ticket 01: shared-tab

**Model:** inherit
**Effort:** inherit

**Acceptance Criteria:**
- [ ] Both notebook tabs are constructed by the same reusable class with identical layout.
- [ ] The standard layer list, layer buttons, and areal-density field are visible and disabled.
- [ ] Target controls and standard element editing retain their existing behavior.

**Files to Touch:**
- `src/hyproc/UI_geometry.py`
- `src/hyproc/UI.py` if integration requires it
- GUI tests as appropriate

**Verification Step:**

Run:
```bash
.venv/Scripts/python -m pytest
```

Expected:
Relevant tests pass, including checks for the shared layout and disabled standard layer controls.

**Notes:**

Preserve existing callback and widget access patterns where practical. Verify the standard element controls remain active.
