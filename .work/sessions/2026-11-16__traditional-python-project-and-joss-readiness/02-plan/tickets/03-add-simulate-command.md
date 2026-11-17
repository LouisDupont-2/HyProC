# Ticket 03: add-simulate-command

**Acceptance Criteria:**
- [ ] hyproc simulate calls the shared engine and writes a complete simulation JSON that can be opened and rerun.
- [ ] The GUI and hyproc simulate produce the same simulated energy grid and yields when run from the same starting JSON with the same calculation settings and energy selection.
- [ ] The README documents how to invoke the command.

**Files to Touch:**
- `src/hyproc/`
- `README.md`

**Verification Step:**

Run:
```bash
hyproc simulate --help
hyproc simulate input.json --output rerun.json
```

Expected:
Help describes the arguments. Use an available saved simulation outside the deferred regression cases. Run it through the CLI and open the same input in the GUI, launch a fresh calculation, and save the result separately. Check that the two saved simulated curves have matching energy and yield arrays. The CLI output opens in the GUI and can be rerun.

**Notes:**

Perform a basic CLI smoke check. Leave the two designed cases and their baselines for future work.
