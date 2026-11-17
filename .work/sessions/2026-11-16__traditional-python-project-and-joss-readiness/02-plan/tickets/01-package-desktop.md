# Ticket 01: package-desktop

**Acceptance Criteria:**
- [ ] A wheel installs in a clean environment and the hyproc launcher opens the existing Tkinter app from outside the checkout.
- [ ] Installed stopping data, defaults, and manual resolve correctly. Existing settings can be carried forward.

**Files to Touch:**
- `pyproject.toml`
- `src/hyproc/`
- `README.md`

**Verification Step:**

Run:
```bash
python -m build
python -m pip install <wheel>
hyproc
```

Expected:
Wheel builds and the GUI opens with its bundled resources available.

**Notes:**

Smoke-test on Windows. Preserve the existing external SRIM integration and review the unused xlwings import.
