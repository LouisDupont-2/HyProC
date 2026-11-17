# Ticket 03: add-simulate-command

**Status:** ✅ Done

## Local Test Result

Built and installed the final wheel. The installed hyproc simulate --help and two consecutive CLI runs succeeded. The GUI freshly calculated and saved the same three-point input, with exactly matching energy and yield arrays. The GUI also opened and reran the CLI output with the same values. All 14 existing tests passed.

## Review Notes

Base: f3eba9a050bd49dd4ab75727dba32115fb9b8854. Exclude the existing fixture, ignore, and manual changes from this ticket.

Reviewed the lazy GUI import, unchanged input document, atomic JSON output, and documented energy selection. Used a separate scratch input for the one-off parity check.

Updated the GPS manual path after the package move. Restored the pre-session Bohr default and edited PDF at their new paths and left them outside ticket commits.

## Blockers / Challenges

External SRIM execution was outside the verified SCS-25-Solid smoke case.

## Commits

- e510742 feat: run saved HyProC simulations from the terminal (ticket 03)

## Time Spent

3m (ticket-start.js to ticket-complete.js)
