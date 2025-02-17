import json
import os

def read_json_file(file_path):
    """
    Read data from a JSON file and return it as a dictionary
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Data from the JSON file, or None if there was an error
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return None
            
        # Read and parse JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
            
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}")
        print(f"Details: {str(e)}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}")
        print(f"Details: {str(e)}")
        return None
