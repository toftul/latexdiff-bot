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

DEFAULT_COMPILE_TIME_LIMIT = 30  # s

DEFAULT_DIFF_TEX_NAME = "diff.tex"
DEFAULT_DIFF_PDF_NAME = DEFAULT_DIFF_TEX_NAME.rsplit('.', 1)[0] + '.pdf'


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