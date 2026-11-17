# Ticket 01: package-desktop

**Status:** ✅ Done

## Local Test Result

Built the wheel with setuptools.build_meta.build_wheel, installed it in a scratch venv with existing dependencies, verified all three bundled resources, and invoked the installed launcher from outside the checkout. The Tkinter window opened and closed on a timer. All 14 existing unit tests pass.

## Review Notes

Base: fa96b25f45cb0173dc7099867c35231da383861d. Pre-existing changes: UI.py signature, UI_geometry.py default, manual PDF and source, and the earlier fixture and ignore changes. Preserve them and exclude them from ticket commits. GPS owns the active session files.

The three overlapping modified files were copied byte-for-byte to scratch before relocating the committed versions. Reviewed package paths, settings migration instructions, and unchanged stopping calculations.

## Blockers / Challenges

The build frontend is unavailable locally. Used its setuptools backend directly to build and verify the wheel.

## Commits

- d545513 refactor: package the HyProC desktop application (ticket 01)

## Time Spent

5m (ticket-start.js to ticket-complete.js)
