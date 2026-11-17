# Ticket 02: share-simulation-core

**Acceptance Criteria:**
- [ ] The documented Python entry point accepts explicit inputs and returns the energy and yield arrays without opening Tkinter, modifying the caller's inputs, or writing files.
- [ ] The GUI calls the shared engine. The reader and writer support version 1 saves and preserve complete simulation inputs and embedded curves.

**Files to Touch:**
- `src/hyproc/`
- `README.md`

**Verification Step:**

Run:
```bash
python -m unittest discover -s tests
```

Expected:
Existing checks pass. Also exercise a saved simulation in Python and the GUI and compare outputs.

**Notes:**

Preserve normalization, offsets, and the existing segmentation behavior. Reuse the shared reader and writer for both entry points.
