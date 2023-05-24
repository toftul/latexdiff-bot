# latexdiff-bot

**! UNDER DEVELOPMENT !**

**Currently this bot does not work as inteded.**

## TODO
1. image comparison tool
2. peek old and file
3. detect git, ask which commit to compare with
4. Web version 


## Old way

Send a .zip archive with your latex project.
It has to contain at least two files:

1. `ANY_NAME.tex`
2. `ANY_NAME_old.tex`

It is important to have a traling `_old` in the old file. 

Bot will do the rest and after some time send you a `diff.pdf` in response.


Commands under the hood:

```shell
latexdiff ANY_NAME_old.tex ANY_NAME.tex > diff.tex
latex -interaction=nonstopmode diff
bibtex diff
latex -interaction=nonstopmode diff
latex -interaction=nonstopmode diff
pdflatex -interaction=nonstopmode diff
```

It supports bibligoraphy.

## Technical info

Using library https://github.com/python-telegram-bot/python-telegram-bot
