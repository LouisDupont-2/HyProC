# Ticket 01: off-resonance

**Status:** ✅ Done

## Local Test Result

`$env:PYTHONPATH = 'src'; python -m unittest discover -s tests`: 19 tests passed. The specified `.venv` does not exist; the installed Python and source path were used instead. The test suite required unrestricted execution because its temporary directory was denied by the sandbox.

## Review Notes

Base: 56d47a2f099697aaab9563dd424eda4429172dc2. The checkout had no pre-existing source changes; GPS session files are owned by this session. Recovery passes: 0. Implementation and review are inline.

Reviewed setting validation and defaults, document creation and loading, shared standard and target calculations, finite-grid diagnostics, and full-target integration against the acceptance criteria. Real broadening and mocked normalization tests verify the baseline independently of the resonance grid. Accepted: all criteria met; no unresolved actionable findings.

## Blockers / Challenges

The planned virtual environment was absent; the installed Python supplied the required dependencies. Sandbox temporary-file permissions required an approved unrestricted test run.

## Commits

- 419bbd6 feat: include off-resonance cross section (ticket 01)

## Time Spent

1h 49m (ticket-start.js to ticket-complete.js)
