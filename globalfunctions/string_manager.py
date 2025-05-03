import json
import os

def get_string(string_id: str, module: str) -> str:
    """
    Retrieves a string from a module's strings.json file.
    
    Args:
        string_id (str): The ID of the string to retrieve (e.g., 'errors.file_required')
        module (str): The module name (e.g., 'ingesta', 'budget', 'reports')
    
    Returns:
        str: The requested string or a default error message if not found
    """
    try:
        # Get the project root directory (two levels up from this file)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Construct the path to the module's strings.json file
        strings_path = os.path.join(base_dir, module, 'strings.json')
        
        if not os.path.exists(strings_path):
            return f"String file not found at: {strings_path}"
        
        with open(strings_path, 'r', encoding='utf-8') as f:
            strings = json.load(f)
        
        # First get the module's strings
        if module not in strings:
            return f"Module {module} not found in strings.json"
        
        module_strings = strings[module]
        
        # Split the string_id into parts and navigate the JSON structure
        parts = string_id.split('.')
        result = module_strings
        for part in parts:
            if part not in result:
                return f"String not found: {string_id} in module {module}"
            result = result[part]
        
        return result
    except FileNotFoundError:
        return f"String file not found for module: {module}"
    except KeyError:
        return f"String not found: {string_id} in module {module}"
    except Exception as e:
        return f"Error retrieving string: {str(e)}" 