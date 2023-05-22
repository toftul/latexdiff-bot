import os
import shutil
import subprocess
import zipfile

# Extract the contents of new.zip and old.zip
with zipfile.ZipFile('new.zip', 'r') as new_zip, zipfile.ZipFile('old.zip', 'r') as old_zip:
    new_zip.extractall('new')
    old_zip.extractall('old')

# Find the main .tex file in the new directory
new_directory = os.path.join(os.getcwd(), 'new')
new_tex_file = None
for root, dirs, files in os.walk(new_directory):
    for file in files:
        if file.endswith('.tex'):
            new_tex_file = os.path.join(root, file)
            break
    if new_tex_file:
        break

# Find the main .tex file in the old directory
old_directory = os.path.join(os.getcwd(), 'old')
old_tex_file = None
for root, dirs, files in os.walk(old_directory):
    for file in files:
        if file.endswith('.tex'):
            old_tex_file = os.path.join(root, file)
            break
    if old_tex_file:
        break

# Create the diff.tex file using latexdiff
diff_file = 'diff.tex'
latexdiff_command = f'latexdiff {old_tex_file} {new_tex_file} > new/{diff_file}'
subprocess.run(latexdiff_command, shell=True, check=True)

os.chdir('new')

# Compile the diff.tex file
pdflatex_command = f'latexmk -f -pdf {diff_file}'
subprocess.run(pdflatex_command, shell=True, check=True)

os.chdir('..')

shutil.move('new/diff.pdf', 'diff.pdf')

# Clean up temporary directories and files
shutil.rmtree('new')
shutil.rmtree('old')
