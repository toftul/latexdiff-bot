# latexdiff-bot

Welcome to the LaTeX Diff Bot!

This bot allows you to generate a LaTeX diff file by comparing two versions of a LaTeX document and receive a PDF with the highlighted changes using [latexdiff](https://www.overleaf.com/learn/latex/Articles/Using_Latexdiff_For_Marking_Changes_To_Tex_Documents).

Here's how you can use the bot:

1. Send `/start` to begin the interaction.
2. Upload the original LaTeX project by sending a single `.tex` file or an entire `.zip`.
3. If there is an ambiguity which file is the main document you will be promted to select one.
4. Upload the old version (`.tex` or `.zip`).
5. If there is an ambiguity which file is the main document you will be promted to select one.
6. The bot will generate a LaTeX diff file and process it.
7. Once the diff file is processed, the bot will send you a PDF with the changes highlighted.

## TODO
1. imporove image comparison tool (PDFs aren't supported now)
2. detect git, ask which commit to compare with?!
3. Web version 
4. Better support for bibligoraphy?
5. Support for mulfile projects. Add flatten flag.
6. Option to send just `diff.tex`.


## Under the hood

Diff file created by
```shell
latexmk -interaction=nonstopmode -cd -f -pdf diff.tex
```

## Author

Created by Ivan Toftul
