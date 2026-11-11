# Ticket 03: document-curve-import

**Model:** inherit
**Effort:** inherit

**Acceptance Criteria:**
- [ ] Document automatic import, conditional preview, supported layouts and optional uncertainty.
- [ ] Verify the LaTeX source builds. GPS Finish publishes the rebuilt PDF.

**Files to Touch:**
- `manual/source/main.tex`

**Verification Step:**

Run:
```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=../../.scratch/tests/2026-11-11__review-excitation-curve-loading/manual -jobname=HyProC_Manual main.tex
```

Expected:
From manual/source, latexmk succeeds and produces HyProC_Manual.pdf in the scratch directory.

**Notes:**

GPS Finish rebuilds and commits the published PDF after the source is committed.
