# Usage 
# python pydiff.py --oldtex /path/to/old.tex --newtex /path/to/new.tex --compile --fast --imagediff

import argparse
import os 
import subprocess

from settings import *


def do_pydiff(path_to_oldtex, path_to_newtex, compile=True, fast=False, imagediff=False, time_limit=DEFAULT_COMPILE_TIME_LIMIT, difftexname=DEFAULT_DIFF_TEX_NAME):
    # make diff.tex 
    newtex_dir = os.path.dirname(path_to_newtex)
    path_to_difftex = os.path.join(newtex_dir, difftexname)
    # TODO
    # https://tex.stackexchange.com/a/598735/249682
    # to make flatten work properly
    latexdiff_command = f'latexdiff --flatten {path_to_oldtex} {path_to_newtex} > {path_to_difftex}'
    subprocess.run(
        latexdiff_command, 
        shell=True, 
        #check=True
    )

    path_to_diffpdf = path_to_difftex.rsplit('.', 1)[0] + '.pdf'
    if compile:
        # Compile the diff.tex to diff.pdf
        if imagediff:
            # do collages
            print('Option imagediff is not ready yet, sorry.')

        if fast:
            # no biblio, no references
            latexmk_command = f"pdflatex -interaction=batchmode -output-directory='{newtex_dir}' '{path_to_difftex}'"
        else:  
            latexmk_command = f'latexmk -interaction=batchmode -cd -f -pdf {path_to_difftex}'
        try:
            subprocess.run(
                latexmk_command, 
                shell=True,
                timeout=time_limit,  # s 
                #check=True
            )
        except subprocess.TimeoutExpired:
            print("Timeout!")
        except subprocess.CalledProcessError:
            print("Something went wrong.")
        else:
            print("The diff.pdf is ready!")

        return path_to_difftex, path_to_diffpdf



if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Intelegent (or not really) python wrapper of the latexdiff")
    
    # Add the named arguments
    parser.add_argument("--oldtex", help="Path to the old tex", required=True)
    parser.add_argument("--newtex", help="Path to the new tex", required=True)
    parser.add_argument("--compile", action="store_true", help="Flag to trigger compilation")
    parser.add_argument("--fast", action="store_true", help="Flag to compile without links and figures")
    parser.add_argument("--imagediff", action="store_true", help="Flag to trigger image comparison tool")
    parser.add_argument("--timelimit", help=f'Time limit in seconds (default {DEFAULT_COMPILE_TIME_LIMIT} sec)', required=False)
    parser.add_argument("--difftexname", help=f'Diff .tex filename (default {DEFAULT_DIFF_TEX_NAME})', required=False)

    # Parse the command-line arguments
    args = parser.parse_args()
    print(args)

    kwargs = {
        "path_to_oldtex": args.oldtex,
        "path_to_newtex": args.newtex,
        "compile": args.compile,
        "fast": args.fast,
        "imagediff": args.imagediff,
    }

    if args.timelimit is not None:
        kwargs["time_limit"] = args.timelimit

    if args.difftexname is not None:
        kwargs["difftexname"] = args.difftexname

    do_pydiff(**kwargs)

