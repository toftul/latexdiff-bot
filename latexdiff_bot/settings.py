import json

# default names across the project
DEFAULT_NEW_TEX = 'main_new.tex'
DEFAULT_OLD_TEX = 'main_old.tex'

DEFAULT_OLD_ZIP = 'old.zip'
DEFAULT_NEW_ZIP = 'new.zip'

DEFAULT_NEW_DIR = 'new'
DEFAULT_OLD_DIR = 'old'

USER_CONFIG_NAME = 'user_settings.json'
USER_DATA_DIR = 'user_data'

DEFAULT_COMPILE_TIME_LIMIT = 30  # [s]

DEFAULT_DIFF_TEX_NAME = "diff.tex"
DEFAULT_DIFF_PDF_NAME = DEFAULT_DIFF_TEX_NAME.rsplit('.', 1)[0] + '.pdf'

SETTINGS_MENU_MESSAGES = [
    'Image comparison tool',
    'Fast compilation mode',
    'Compile PDF file'
]
SETTINGS_MENU_OFF_ADDTION = ' (currently OFF)'
SETTINGS_MENU_ON_ADDTION = ' (currently ON)'

DEFAULT_USER_SETTINGS = {
    "imagediff": False,
    "fast": False,
    "compile": True
}

# messages
MESSAGE_CANCEL = 'Canceled! You can start over.'
MESSAGE_MORE_THAN_ONE_TEX = 'It seems that there are more then one main `.tex` files\. Select the one you wish to compare\.'
MESSAGE_SORRY_NO_TEX = 'Sorry, I could not find any `.tex` file with `\documentclass` in it\. Try another one\.'
MESSAGE_MAKING_DIFF = 'Got you\! Making `diff.pdf` now\.\.\.'
MESSAGE_FAILED = 'Failed :('
MESSAGE_UNDERSTOOD_NEW = '''Understood\! Now send the old version \(`tex` or `zip`\)\.'''
MESSAGE_START_TEXT = "Send me a `.tex` or `.zip` of your current latex project\."
MESSAGE_HELP_TEXT = """
*Welcome to the LaTeX Diff Bot\!*

This bot allows you to generate a LaTeX diff file by comparing two versions of a LaTeX document and receive a PDF with the highlighted changes using [latexdiff](https://www.overleaf.com/learn/latex/Articles/Using_Latexdiff_For_Marking_Changes_To_Tex_Documents)\.

Here's how you can use the bot:

1\. Send /start to begin the interaction\.
2\. Upload the original LaTeX project by sending a single `.tex` file or an entire `.zip`\.
3\. If there is an ambiguity which file is the main document you will be promted to select one\.
4\. Upload the old version \(`.tex` or `.zip`\)\.
5\. If there is an ambiguity which file is the main document you will be promted to select one\.
6\. The bot will generate a LaTeX diff file and process it\.
7\. Once the diff file is processed, the bot will send you a PDF with the changes highlighted\.

Project page: 
[gh/toftul/latexdiff\-bot](https://github.com/toftul/latexdiff-bot)

Created by [Ivan Toftul](tg://user?id=63688320)
"""

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # handle file not found or invalid JSON formar errors
        print(f"Error while loading JSON file: {e}")
        return None
    
def write_json_file(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    except (IOError, TypeError) as e:
        # Handle IO error or invalid data type errors
        print(f"Error while writing JSON file: {e}")