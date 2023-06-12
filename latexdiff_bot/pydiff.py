# Usage 
# python pydiff.py --oldtex /path/to/old.tex --newtex /path/to/new.tex --compile --fast --imagediff

import argparse
import os 


def do_pydiff(path_to_oldtex, path_to_newtex, if_compile=True, if_fast=False, if_imagediff=False):

    return 0


if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Intelegent (or not really) python wrapper of the latexdiff")
    
    # Add the named arguments
    parser.add_argument("--oldtex", help="Path to the old tex", required=True)
    parser.add_argument("--newtex", help="Path to the new tex", required=True)
    parser.add_argument("--compile", action="store_true", help="Flag to trigger compilation")
    parser.add_argument("--fast", action="store_true", help="Flag to compile without links and figures")
    parser.add_argument("--imagediff", action="store_true", help="Flag to trigger image comparison tool")

    # Parse the command-line arguments
    args = parser.parse_args()
    # print(args)

    do_pydiff(
        path_to_oldtex=args.oldtex,
        path_to_newtex=args.newtex,
        if_compile=args.compile,
        if_fast=args.fast,
        if_imagediff=args.imagediff
    )

