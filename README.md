# latexdiff-bot

Send a .zip archive with your latex project.
It has to contain at least two files:

1. `ANY_NAME.tex`
2. `ANY_NAME_old.tex`

It is important to have a traling `_old` in the old file. 

Bot will do the rest and after some time send you a `diff.pdf` in response.


List of commands under the hood:

```shell
> latexdiff ANY_NAME.tex ANY_NAME_old.tex > diff.tex
> latex -interaction=nonstopmode diff
> bibtex diff
> latex -interaction=nonstopmode diff
> latex -interaction=nonstopmode diff
> pdflatex -interaction=nonstopmode diff
```

It supports bibligoraphy.