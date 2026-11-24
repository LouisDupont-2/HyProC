# Ticket 01: shared-tab

**Status:** ✅ Done

## Local Test Result

The documented .venv is absent. With the available Python, `$env:PYTHONPATH='src'; python -m pytest` passed: 20 tests. The suite required execution outside the sandbox because its temporary files were denied inside it. The added GUI test checks both widget trees, disabled controls, and element button routing.

## Review Notes

Base: 9718cc28fdaf03d682dcf9f75ba2aef3b34d5c17. Before implementation, the working tree contained only GPS-owned session status and log changes; ticket-owned files were clean. Inline implementation; one correction pass adjusted extraction markers and the test environment. Reviewed the diff against all acceptance criteria: both tabs use TargetEditorTab, standard layer controls are disabled, and callbacks retain target/standard routing. The existing controller widget names are preserved. The full suite and new GUI test pass. Accepted inline as a localized UI refactor.

## Blockers / Challenges

The documented virtual environment is absent; system Python and PYTHONPATH=src were used instead.

## Commits

- a43bd80 refactor: share target and standard tab layout (ticket 01)

## Time Spent

3m (ticket-start.js to ticket-complete.js)
