# B.Tech project report (LaTeX)

`main.pdf` is the compiled report. To rebuild it:

```bash
cd report
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Fill in `[DEPARTMENT NAME]` and `[COLLEGE NAME]` at the top of `main.tex` (and uncomment the logo
line if you have the college logo as `figures/logo.png`). Chapters are in `chapters/`, references in
`references.bib`. Figures are read from the results folders of the project (`../07_comparison/...`,
`../08_forward_test/...`) and `figures/website.png`.
