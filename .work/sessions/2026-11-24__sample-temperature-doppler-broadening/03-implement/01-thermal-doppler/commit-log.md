# Ticket 01: thermal-doppler

**Status:** ✅ Done

## Local Test Result

The specified .venv executable is absent. Ran `python -m unittest discover -s tests` with PYTHONPATH=src and TEMP/TMP set to the session scratch directory, outside the sandbox after its default temporary directory denied writes: 24 tests passed.

## Review Notes

Base: 1a8d925d1b6ab8e5691c5c84b5174710eeb37148. Initial changes: GPS session state and this log only; no pre-existing source changes. Implementation inline.

Reviewed the diff against all acceptance criteria. The thermal standard deviation follows the free-gas target-motion expression sigma² = 2 E_R k_B T m_projectile / m_target, in lab beam energy; the IAEA TECDOC 1822 section 2.7 describes thermal Doppler broadening. Tests cover numerical width, absolute zero, quadrature, separate temperatures, old-file defaults, invalid-load preservation, K factor disabling and headless validation. The GUI serialization test checks saved values. Independent reviewer not required for inline implementation; reviewed directly. Acceptance: criteria satisfied and suite passes. Recovery/correction passes: zero.

## Blockers / Challenges

The repository has no .venv; system Python had dependencies available. Sandbox temporary-file permissions required the approved escalated test invocation.

## Commits

- 20e7fec feat: add thermal Doppler broadening (ticket 01)

## Time Spent

4m (ticket-start.js to ticket-complete.js)
