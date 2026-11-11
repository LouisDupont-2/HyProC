# Ticket 01: validate-curve-data

**Model:** inherit
**Effort:** inherit

**Acceptance Criteria:**
- [ ] Recognized layouts keep the first data row and map optional uncertainty consistently.
- [ ] Ambiguous layouts expose sheet, table and column choices.
- [ ] Validate before applying data and keep energy, yield and uncertainty aligned when sorting.

**Files to Touch:**
- `curve_import.py`
- `tests/test_curve_import.py`
- `README.md`

**Verification Step:**

Run:
```bash
python -m unittest discover -s tests -p test_curve_import.py
```

Expected:
Import regression tests pass.

**Notes:**

Verify CSV, TXT and workbook handling including the legacy Excel engine selection.
