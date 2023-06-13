# Usage 
# python pydiff.py --oldtex /path/to/old.tex --newtex /path/to/new.tex --compile --fast --imagediff

import argparse
import os 
import subprocess
import zipfile

from settings import *



def extract(path_to_zip, target_dir):
    with zipfile.ZipFile(path_to_zip, 'r') as target_zip:
        target_zip.extractall(target_dir)


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

## OLD
# async def do_latexdiff_and_collage(working_dir, chat_id):
#     touch_images = True
#     config_json = load_json_file(USER_CONFIG_NAME)
#     touch_images = False
#     if str(chat_id) in config_json:
#         touch_images = config_json[str(chat_id)]['touch_images']

    
#     dir_new_full = os.path.join(os.getcwd(), working_dir, DEFAULT_NEW_DIR)
#     dir_old_full = os.path.join(os.getcwd(), working_dir, DEFAULT_OLD_DIR)

#     new_tex_file = os.path.join(dir_new_full, DEFAULT_NEW_TEX)
#     old_tex_file = os.path.join(dir_old_full, DEFAULT_OLD_TEX)
    
#     if touch_images:
#         old_image_paths = get_image_paths(old_tex_file)
#         new_image_paths = get_image_paths(new_tex_file)

#         changed_images = find_changed_images(old_image_paths, new_image_paths)

#         new_image_paths_full = []
#         for i in range(len(new_image_paths)):
#             new_image_paths_full.append(os.path.join(dir_new_full, new_image_paths[i]))

#         old_image_paths_full = []
#         for i in range(len(old_image_paths)):
#             old_image_paths_full.append(os.path.join(dir_old_full, old_image_paths[i]))

#         blank_image_path = os.path.join(os.getcwd(), 'blank.jpg')

#         make_all_collages(old_image_paths_full, new_image_paths_full, changed_images, blank_image_path)
    
#     # DO THE DIFF PDF
#     latexdiffpdf(
#         old_tex_file=os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX),
#         new_tex_file=os.path.join(working_dir, DEFAULT_NEW_DIR, DEFAULT_NEW_TEX),
#         dir_new_full=os.path.join(working_dir, DEFAULT_NEW_DIR),
#         diff_file=DIFF_TEX_NAME
#     )
