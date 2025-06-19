#remoteapiclient.py

import requests

def managelist_client(command,url_base="https://chinese.eriktamm.com/api", name="adventure",  word=None):
    """
    Client function to interact with the managelist endpoint.
    
    Args:
        url_base (str): The base URL of the API server (e.g., 'https://example.com/api')
        name (str): The name of the list to manage
        command (str): The command to execute ('get', 'addto', or 'delete')
        word (str, optional): The word to add when using the 'addto' command
    
    Returns:
        dict: The response from the server
    
    Raises:
        Exception: If the request fails
    """
    
    endpoint = f"{url_base}/managelist"
    
    # Prepare the payload
    payload = {
        "name": name,
        "command": command
    }
    
    # Add word if provided
    if word is not None:
        payload["word"] = word
    
    # Make the POST request
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request to managelist failed: {str(e)}")

    # Example usage:
    # Get all words in a list
    # result = managelist_client('https://chinese.eriktamm.com/api', 'mylist', 'get')
    # 
    # Add a word to a list
    # result = managelist_client('https://chinese.eriktamm.com/api', 'mylist', 'addto', '你好')
    # 
    # Delete a list
    # result = managelist_client('https://chinese.eriktamm.com/api', 'mylist', 'delete')
