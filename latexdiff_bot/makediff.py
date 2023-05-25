import os
import shutil
import subprocess
import zipfile

#from icecream import ic

from collage import make_diff_image

def get_main_tex_files(directory):
    files = os.listdir(directory)
    # Filter out the .tex files that contain '\documentclass{'
    tex_files_with_documentclass = []
    for file_name in files:
        if file_name.endswith('.tex'):
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'r') as file:
                content = file.read()
                if '\documentclass{' in content:
                    tex_files_with_documentclass.append(file_name)
    return tex_files_with_documentclass


def extract(path_to_zip, target_dir):
    with zipfile.ZipFile(path_to_zip, 'r') as target_zip:
        target_zip.extractall(target_dir)
        
        
def find_main_tex(path):
    directory = os.path.join(os.getcwd(), path)
    tex_file = None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tex'):
                tex_file = os.path.join(root, file)
                break
        if tex_file:
            break
    return tex_file


def get_image_paths(target_tex_file):
    image_paths = []
    with open(target_tex_file, 'r') as tex_file:
        for line in tex_file:
            if not line.strip().startswith('%') and 'includegraphics' in line:
                start_index = line.find('{') + 1
                end_index = line.find('}')
                image_path = line[start_index:end_index]
                image_paths.append(image_path)
    return image_paths


def find_changed_images(old_image_paths, new_image_paths):
    """
        for the input
            old_image_paths = ['fig1', 'fig2', 'fig3', 'fig4', 'fig5']
            new_image_paths = ['fig1', 'fig2_new', 'fig3', 'fig4', 'fig5', 'fig6']
        the return would be
            [False, True, False, False, False, True]
    """
    changed_images = [True] * len(new_image_paths)

    for index, new_imag in enumerate(new_image_paths):
        if index < len(old_image_paths):
            if old_image_paths[index] == new_imag:
                changed_images[index] = False
                
    return changed_images


def make_all_collages(old_image_paths_full, new_image_paths_full, changed_images, blank_image_path):
    for i, new_image_path in enumerate(new_image_paths_full):
        if changed_images[i]:
            if i < len(old_image_paths_full):
                make_diff_image(
                    path_img_old=old_image_paths_full[i], 
                    path_img_new=new_image_paths_full[i], 
                    path_img_diff=new_image_paths_full[i]
                )
            else:
                make_diff_image(
                    path_img_old=blank_image_path, 
                    path_img_new=new_image_paths_full[i], 
                    path_img_diff=new_image_paths_full[i]
                )

def latexdiffpdf(old_tex_file, new_tex_file, dir_new_full, diff_file):
    full_path_diff_file = os.path.join(dir_new_full, diff_file)
    latexdiff_command = f'latexdiff {old_tex_file} {new_tex_file} > {full_path_diff_file}'
    subprocess.run(
        latexdiff_command, 
        shell=True, 
        #check=True
    )
    
    # Compile the diff.tex file
    latexmk_command = f'latexmk -interaction=nonstopmode -cd -f -pdf {full_path_diff_file}'
    subprocess.run(
        latexmk_command, 
        shell=True, 
        #check=True
    )

def create_diffpdf(old_tex_file, new_tex_file, dir_new_full):
    diff_file = 'diff.tex'
    latexdiff_command = f'latexdiff {old_tex_file} {new_tex_file} > {dir_new_full}/{diff_file}'
    subprocess.run(
        latexdiff_command, 
        shell=True, 
        #check=True
    )
    
    os.chdir(dir_new_full)
    
    # Compile the diff.tex file
    latexmk_command = f'latexmk -interaction=nonstopmode -f -pdf {diff_file}'
    subprocess.run(
        latexmk_command, 
        shell=True, 
        #check=True
    )

    os.chdir('..')
    
    shutil.move('new/diff.pdf', 'diff.pdf')
    
    
def do_stuff(old_zip, new_zip, touch_images=True):
    dir_new = 'new'
    dir_old = 'old'
    
    dir_new_full = os.path.join(os.getcwd(), dir_new)
    dir_old_full = os.path.join(os.getcwd(), dir_old)

    extract(new_zip, dir_new)
    extract(old_zip, dir_old)

    old_tex_file = find_main_tex(dir_old)
    new_tex_file = find_main_tex(dir_new)
    
    if touch_images:
        old_image_paths = get_image_paths(old_tex_file)
        new_image_paths = get_image_paths(new_tex_file)

        changed_images = find_changed_images(old_image_paths, new_image_paths)

        new_image_paths_full = []
        for i in range(len(new_image_paths)):
            new_image_paths_full.append(os.path.join(dir_new_full, new_image_paths[i]))

        old_image_paths_full = []
        for i in range(len(old_image_paths)):
            old_image_paths_full.append(os.path.join(dir_old_full, old_image_paths[i]))

        blank_image_path = os.path.join(os.getcwd(), 'blank.jpg')

        make_all_collages(old_image_paths_full, new_image_paths_full, changed_images, blank_image_path)
    
    create_diffpdf(old_tex_file, new_tex_file, dir_new_full)
    
    # Clean up temporary directories and files
    shutil.rmtree(dir_new_full)
    shutil.rmtree(dir_old_full)
    
    
if __name__ == "__main__":
    new_zip = 'new.zip'
    old_zip = 'old.zip'
    do_stuff(old_zip, new_zip, touch_images=True)
    