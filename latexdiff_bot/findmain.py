import argparse
import os


def find_main_tex(path_to_dir):
    files = os.listdir(path_to_dir)
    # Filter out the .tex files that contain '\documentclass'
    tex_files_with_documentclass = []
    for file_name in files:
        if file_name.endswith('.tex'):
            file_path = os.path.join(path_to_dir, file_name)
            with open(file_path, 'r') as file:
                content = file.read()
                if '\documentclass' in content:
                    tex_files_with_documentclass.append(file_name)
    return tex_files_with_documentclass


if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Find main tex files")
    
    # Add the named arguments
    parser.add_argument("--dir", help="Path to the folder to analyse", required=True)

    # Parse the command-line arguments
    args = parser.parse_args()
    # print(args)

    find_main_tex(
        path_to_dir=args.dir
    )

