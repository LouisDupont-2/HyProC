# Ticket 01: restore-history-target

**Status:** ✅ Done

## Local Test Result

`$env:PYTHONPATH='src'; python -m pytest -q -p no:cacheprovider` — 29 passed. The stated .venv is absent, so the installed Python was used with the source directory on PYTHONPATH. The new history tests pass independently (3 passed).

## Review Notes

Base: 7834140cb59c259031cadbfcc516fa83fafec43c. Pre-existing user changes: src/hyproc/UI_geometry.py and src/hyproc/settings.example.json; preserve both. Implementation is inline; recovery count 0.

Reviewed the diff against the ticket: snapshot captures the simulation document's independent target before calculation; loading validates the history before replacing state; restore copies again; click maps the entire canvas width to visible rows and honors scrolling; reset clears snapshots. Tests cover a calculation, cancellation, restoration, scrolling, copy independence, persistence, legacy rows, malformed history, and reset. The pre-existing files were not modified or included in the ticket.

## Blockers / Challenges

The first full pytest run hit a transient Tk initialization error in an existing test; the affected tests passed separately and a subsequent complete run passed.

## Commits

- 422ece2 feat: restore targets from chi-squared history (ticket 01)

## Time Spent

3m (ticket-start.js to ticket-complete.js)
