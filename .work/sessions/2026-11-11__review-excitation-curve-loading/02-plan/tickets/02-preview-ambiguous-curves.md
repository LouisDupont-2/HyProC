# Ticket 02: preview-ambiguous-curves

**Model:** inherit
**Effort:** inherit

**Acceptance Criteria:**
- [ ] Recognized files load without a preview. Ambiguous files show sample rows and let the user choose sheet, table and columns.
- [ ] Cancellation and validation failure preserve the previously loaded curve.

**Files to Touch:**
- `UI.py`
- `dialog_import.py`
- `tests/test_curve_import_ui.py`

**Verification Step:**

Run:
```bash
python -m unittest discover -s tests -p test_curve_import*.py
```

Expected:
Importer and UI integration regressions pass.

**Notes:**

Leave the rest of the application and curve representation intact.
