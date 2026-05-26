import json
import os
import folder_paths


def _safe_resolve_path(base_dir, user_path):
    """
    Safely join base_dir and user_path, ensuring the result is contained
    within base_dir. Raises ValueError on path traversal attempts.
    """
    # Normalize and resolve to an absolute path
    resolved = os.path.realpath(os.path.join(base_dir, user_path))
    base_resolved = os.path.realpath(base_dir)
    # Ensure the resolved path starts with the base directory
    if not (resolved == base_resolved or resolved.startswith(base_resolved + os.sep)):
        raise ValueError(
            f"Path traversal detected: '{user_path}' resolves outside the output directory"
        )
    return resolved


class AppendInputToJSONArrayFile:
    """
    A simple node that appends a string input to a JSON array file.
    Creates the file if it doesn't exist.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/lite-text.json"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "append_to_file"
    CATEGORY = "lite-text-to-file"
    OUTPUT_NODE = True

    def append_to_file(self, text_input, file_prefix):
        try:
            # Get the output directory from ComfyUI's folder_paths
            output_dir = folder_paths.get_output_directory()
            
            # Combine output directory with file prefix
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Read existing data or create new array
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = [data]  # Convert to list if it's not already
                    except json.JSONDecodeError:
                        data = []  # Start fresh if file is corrupted
            else:
                data = []
            
            # Append the new text input
            data.append(text_input)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            status = f"✓ Appended to {file_path} (total items: {len(data)})"
            return (status,)
            
        except Exception as e:
            error_msg = f"✗ Error: {str(e)}"
            return (error_msg,)


class WriteToTextFile:
    """
    Writes or overwrites a text file with the input string.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/output.txt"
                }),
                "mode": (["overwrite", "append", "prepend"], {
                    "default": "overwrite"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "write_to_file"
    CATEGORY = "lite-text-to-file"
    OUTPUT_NODE = True

    def write_to_file(self, text_input, file_prefix, mode):
        try:
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write to file
            # Read existing content if prepending
            existing_content = ""
            if mode == "prepend":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                except FileNotFoundError:
                    # If the file doesn't exist yet, it will just write it fresh
                    pass 
            
            # Write to file
            write_mode = 'a' if mode == "append" else 'w'
            with open(file_path, write_mode, encoding='utf-8') as f:
                if mode == "prepend":
                    # Write new text, a newline, and then the original content
                    f.write(text_input + '\n' + existing_content)
                else:
                    f.write(text_input)
                    if mode == "append":
                        f.write('\n')  # Add newline when appending
            
            # Update status message
            if mode == "append":
                action = "Appended to"
            elif mode == "prepend":
                action = "Prepended to"
            else:
                action = "Wrote to"
                
            # status = f"✓ {action} {file_path}"
            status = f"{file_path}"
            return (status,)
            
        except Exception as e:
            error_msg = f"✗ Error: {str(e)}"
            return (error_msg,)


class LoadFromTextFile:
    """
    Loads text content from a file.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/output.txt"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_content",)
    FUNCTION = "load_from_file"
    CATEGORY = "lite-text-to-file"

    def load_from_file(self, file_prefix):
        try:
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            if not os.path.exists(file_path):
                return (f"Error: File not found at {file_path}",)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return (content,)
            
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            return (error_msg,)


class LoadFromJSONFile:
    """
    Loads and formats JSON content from a file.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/lite-text.json"
                }),
                "output_format": (["pretty", "compact", "array_items"], {
                    "default": "pretty"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_content",)
    FUNCTION = "load_from_file"
    CATEGORY = "lite-text-to-file"

    def load_from_file(self, file_prefix, output_format):
        try:
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            if not os.path.exists(file_path):
                return (f"Error: File not found at {file_path}",)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if output_format == "pretty":
                content = json.dumps(data, indent=2, ensure_ascii=False)
            elif output_format == "compact":
                content = json.dumps(data, ensure_ascii=False)
            elif output_format == "array_items":
                if isinstance(data, list):
                    content = '\n'.join(str(item) for item in data)
                else:
                    content = str(data)
            
            return (content,)
            
        except json.JSONDecodeError as e:
            return (f"Error: Invalid JSON - {str(e)}",)
        except Exception as e:
            return (f"Error reading file: {str(e)}",)


class ClearJSONArrayFile:
    """
    Clears a JSON array file (resets it to an empty array).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/lite-text.json"
                }),
                "trigger": ("STRING", {
                    "multiline": False,
                    "default": "clear"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "clear_file"
    CATEGORY = "lite-text-to-file"
    OUTPUT_NODE = True

    def clear_file(self, file_prefix, trigger):
        try:
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write empty array
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            
            status = f"✓ Cleared {file_path}"
            return (status,)
            
        except Exception as e:
            error_msg = f"✗ Error: {str(e)}"
            return (error_msg,)


class AppendLineToTextFile:
    """
    Appends a line of text to a text file.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/log.txt"
                }),
                "add_timestamp": ("BOOLEAN", {
                    "default": False
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "append_line"
    CATEGORY = "lite-text-to-file"
    OUTPUT_NODE = True

    def append_line(self, text_input, file_prefix, add_timestamp):
        try:
            from datetime import datetime
            
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Prepare text with optional timestamp
            if add_timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                line = f"[{timestamp}] {text_input}\n"
            else:
                line = f"{text_input}\n"
            
            # Append to file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(line)
            
            # Count lines
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            status = f"✓ Appended to {file_path} (total lines: {line_count})"
            return (status,)
            
        except Exception as e:
            error_msg = f"✗ Error: {str(e)}"
            return (error_msg,)


class SaveTextIntoJSON:
    """
    Saves text into a JSON file using a key-value structure.
    Creates or updates the key in the JSON object.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "forceInput": True
                }),
                "key": ("STRING", {
                    "multiline": False,
                    "default": "data"
                }),
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/data.json"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "save_to_json"
    CATEGORY = "lite-text-to-file"
    OUTPUT_NODE = True

    def save_to_json(self, text_input, key, file_prefix):
        try:
            # SANITIZE ALL INPUTS FIRST - convert everything to strings
            # Handle key
            if isinstance(key, list):
                key = str(key[0]) if len(key) > 0 else "data"
            elif isinstance(key, (dict, tuple)):
                key = str(key)
            else:
                key = str(key) if key else "data"
            
            # Handle file_prefix
            if isinstance(file_prefix, list):
                file_prefix = str(file_prefix[0]) if len(file_prefix) > 0 else "text/data.json"
            elif isinstance(file_prefix, (dict, tuple)):
                file_prefix = str(file_prefix)
            else:
                file_prefix = str(file_prefix) if file_prefix else "text/data.json"
            
            # Handle text_input
            if isinstance(text_input, list):
                text_value = json.dumps(text_input, ensure_ascii=False)
            elif isinstance(text_input, dict):
                text_value = json.dumps(text_input, ensure_ascii=False)
            else:
                text_value = str(text_input) if text_input is not None else ""
            
            # Now proceed with the sanitized inputs
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Read existing data or create new object
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, dict):
                            data = {}  # Convert to dict if it's not already
                    except json.JSONDecodeError:
                        data = {}  # Start fresh if file is corrupted
            else:
                data = {}
            
            # Set or update the key (key is now guaranteed to be a string)
            data[key] = text_value
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            status = f"✓ Saved key '{key}' to {file_path} (total keys: {len(data)})"
            return (status,)
            
        except Exception as e:
            import traceback
            error_msg = f"✗ Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # Print to console for debugging
            return (error_msg,)


class LoadTextFromJSONFromKey:
    """
    Loads text from a JSON file using a specific key.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {
                    "multiline": False,
                    "default": "data"
                }),
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/data.json"
                }),
            },
            "optional": {
                "default_value": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_value",)
    FUNCTION = "load_from_json"
    CATEGORY = "lite-text-to-file"

    def load_from_json(self, key, file_prefix, default_value=""):
        try:
            # SANITIZE ALL INPUTS FIRST - convert everything to strings
            # Handle key
            if isinstance(key, list):
                key = str(key[0]) if len(key) > 0 else "data"
            elif isinstance(key, (dict, tuple)):
                key = str(key)
            else:
                key = str(key) if key else "data"
            
            # Handle file_prefix
            if isinstance(file_prefix, list):
                file_prefix = str(file_prefix[0]) if len(file_prefix) > 0 else "text/data.json"
            elif isinstance(file_prefix, (dict, tuple)):
                file_prefix = str(file_prefix)
            else:
                file_prefix = str(file_prefix) if file_prefix else "text/data.json"
            
            # Handle default_value
            if isinstance(default_value, list):
                default_value = json.dumps(default_value, ensure_ascii=False)
            elif isinstance(default_value, dict):
                default_value = json.dumps(default_value, ensure_ascii=False)
            else:
                default_value = str(default_value) if default_value is not None else ""
            
            # Now proceed with the sanitized inputs
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            if not os.path.exists(file_path):
                if default_value:
                    return (default_value,)
                return (f"Error: File not found at {file_path}",)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                return (f"Error: JSON file is not a key-value object",)
            
            if key not in data:
                if default_value:
                    return (default_value,)
                return (f"Error: Key '{key}' not found in JSON file",)
            
            value = data[key]
            
            # Convert to string if it's not already
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            
            return (value,)
            
        except json.JSONDecodeError as e:
            return (f"Error: Invalid JSON - {str(e)}",)
        except Exception as e:
            import traceback
            error_msg = f"Error reading file: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # Print to console for debugging
            return (error_msg,)

class LoadTextFromJSONArrayByIndex:
    """
    Loads text from a JSON array file by index position.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_prefix": ("STRING", {
                    "multiline": False,
                    "default": "text/lite-text.json"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999
                }),
            },
            "optional": {
                "default_value": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_value",)
    FUNCTION = "load_from_array"
    CATEGORY = "lite-text-to-file"

    def load_from_array(self, file_prefix, index, default_value=""):
        try:
            # SANITIZE ALL INPUTS FIRST - convert everything to proper types
            # Handle file_prefix
            if isinstance(file_prefix, list):
                file_prefix = str(file_prefix[0]) if len(file_prefix) > 0 else "text/lite-text.json"
            elif isinstance(file_prefix, (dict, tuple)):
                file_prefix = str(file_prefix)
            else:
                file_prefix = str(file_prefix) if file_prefix else "text/lite-text.json"
            
            # Handle index
            if isinstance(index, list):
                index = int(index[0]) if len(index) > 0 else 0
            elif isinstance(index, str):
                try:
                    index = int(index)
                except ValueError:
                    index = 0
            else:
                index = int(index) if index is not None else 0
            
            # Handle default_value
            if isinstance(default_value, list):
                default_value = json.dumps(default_value, ensure_ascii=False)
            elif isinstance(default_value, dict):
                default_value = json.dumps(default_value, ensure_ascii=False)
            else:
                default_value = str(default_value) if default_value is not None else ""
            
            # Now proceed with the sanitized inputs
            output_dir = folder_paths.get_output_directory()
            file_path = _safe_resolve_path(output_dir, file_prefix)
            
            if not os.path.exists(file_path):
                if default_value:
                    return (default_value,)
                return (f"Error: File not found at {file_path}",)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return (f"Error: JSON file is not an array",)
            
            if index < 0 or index >= len(data):
                if default_value:
                    return (default_value,)
                return (f"Error: Index {index} out of range (array length: {len(data)})",)
            
            value = data[index]
            
            # Convert to string if it's not already
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            
            return (value,)
            
        except json.JSONDecodeError as e:
            return (f"Error: Invalid JSON - {str(e)}",)
        except Exception as e:
            import traceback
            error_msg = f"Error reading file: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # Print to console for debugging
            return (error_msg,)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "AppendInputToJSONArrayFile": AppendInputToJSONArrayFile,
    "WriteToTextFile": WriteToTextFile,
    "LoadFromTextFile": LoadFromTextFile,
    "LoadFromJSONFile": LoadFromJSONFile,
    "ClearJSONArrayFile": ClearJSONArrayFile,
    "AppendLineToTextFile": AppendLineToTextFile,
    "SaveTextIntoJSON": SaveTextIntoJSON,
    "LoadTextFromJSONFromKey": LoadTextFromJSONFromKey,
    "LoadTextFromJSONArrayByIndex": LoadTextFromJSONArrayByIndex,
}

# Display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "AppendInputToJSONArrayFile": "Append Input To JSON Array File",
    "WriteToTextFile": "Write To Text File",
    "LoadFromTextFile": "Load From Text File",
    "LoadFromJSONFile": "Load From JSON File",
    "ClearJSONArrayFile": "Clear JSON Array File",
    "AppendLineToTextFile": "Append Line To Text File",
    "SaveTextIntoJSON": "Save Text Into JSON",
    "LoadTextFromJSONFromKey": "Load Text From JSON From Key",
    "LoadTextFromJSONArrayByIndex": "Load Text From JSON Array By Index",
}