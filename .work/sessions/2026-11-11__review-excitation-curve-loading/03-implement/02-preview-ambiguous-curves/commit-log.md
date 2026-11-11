# Ticket 02: preview-ambiguous-curves

**Status:** ✅ Done

## Local Test Result

Ran python -m unittest discover -s tests -p test_curve_import*.py with the bundled interpreter and installed application dependencies. All 12 tests passed, including a real Tk preview. A separate real .xls fixture also passed.

## Review Notes

Base: f644f2d3951abc1e3185bb5364c6600f85fe3de6. Working tree held only GPS ticket start state. Inline implementation owns UI.py, dialog_import.py and tests/test_curve_import_ui.py. Also corrected the parser and its test when reviewing the tab-delimited preview: an empty cell must not shift a later measurement into the yield column. Verified known layouts bypass the dialog and failure or cancellation leaves the curve and plot intact.

## Blockers / Challenges

The host test run was needed because xlwings changes into the bundled Python installation during import.

## Commits

- 676342a feat: preview ambiguous excitation curve imports (ticket 02)

## Time Spent

5m (ticket-start.js to ticket-complete.js)
