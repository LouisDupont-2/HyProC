# HyProC manual

Open [HyProC_Manual.pdf](HyProC_Manual.pdf) to read the manual.

- `source/main.tex`: LaTeX source.
- `source/bibliography.bib`: references.
- `source/figures/`: images used by the manual.
- `build/`: local generated files, ignored by Git.

To rebuild with a LaTeX installation that includes `latexmk` and Biber,
run these commands in PowerShell from the `manual/source` directory:

```powershell
latexmk -pdf '-outdir=../build' '-jobname=HyProC_Manual' main.tex
if ($LASTEXITCODE -eq 0) {
    Copy-Item ../build/HyProC_Manual.pdf ../HyProC_Manual.pdf
}
```

Commit the source files and the updated PDF after rebuilding.
