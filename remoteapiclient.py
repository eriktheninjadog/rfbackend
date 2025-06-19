#remoteapiclient.py

import requests

def managelist_client(command,word=None,url_base="https://chinese.eriktamm.com/api", name="adventure"):
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

 

if __name__ == "__main__":
    # Example usage
    try:
        result = managelist_client('get')
        print("List contents:", result)
    except Exception as e:
        print("Error:", str(e))
    # Add a word to a list
    try:
        result = managelist_client('addto', '你好')
        print("Add word result:", result)
    except Exception as e:  
        print("Error:", str(e)) 

    try:
        result = managelist_client('get')
        print("List contents:", result)
    except Exception as e:
        print("Error:", str(e))
        
    # Delete a list 
    try:
        result = managelist_client('delete')
        print("Delete list result:", result)
    except Exception as e:
        print("Error:", str(e)) 
        
    try:
        result = managelist_client('get')
        print("List contents:", result)
    except Exception as e:
        print("Error:", str(e))
