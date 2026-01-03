"""JSON parsing and processing utilities"""
import json
import re
from flask import jsonify


def extract_json(text):
    """Extract JSON object from text using regex"""
    # Regular expression pattern to match JSON
    json_pattern = r'{.*}'    
    # Find all occurrences of the JSON pattern in the text
    json_matches = re.findall(json_pattern, text, re.DOTALL)    
    if json_matches:
        # Extract the first JSON match
        json_string = json_matches[0]        
        try:
            # Parse the JSON string
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError:
            print("Invalid JSON format.")
    else:
        print("No JSON found in the text.")    
    return None


def extract_json_array(text):
    """Extract JSON array from text"""
    try:
        # Find the opening bracket of the JSON array
        start_index = text.index('[')
        # Find the closing bracket of the JSON array
        end_index = text.rindex(']') + 1
        # Extract the JSON array substring
        json_array_str = text[start_index:end_index]
        # Parse the JSON array
        json_array = json.loads(json_array_str)
        return json_array
    except (ValueError, json.JSONDecodeError):
        return None


def is_list(obj):
    """Check if object is a list"""
    return isinstance(obj, list)