import json

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