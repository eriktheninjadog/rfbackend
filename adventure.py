#adventure.py



import openrouter
import json


import hashlib
import subprocess
import os
import random
import glob







def create_adventure_from_prompt(prompt):
    api = openrouter.OpenRouterAPI()
    
    result = api.open_router_gemini_25_flash("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully.", prompt)
    result = result.replace('json','')
    result = result.replace('```','')
    start = result.find('{')
    end = result.rfind('}')
    if start == -1 or end == -1:
        return 'Invalid JSON format returned from the API'
    result = result[start:end+1]
    # Parse the JSON to ensure it's valid
    done = False
    while not done:
        try:
            json_data = json.loads(result)
            done = True
        except json.JSONDecodeError:
            # If JSON is invalid, try to fix it by removing the last character
            result = api.open_router_nova_lite_v1("Fix the jsoin in this text: " + result)
            start = result.find('{')
            end = result.rfind('}')
            if start == -1 or end == -1:
                return 'Invalid JSON format returned from the API'
            result = result[start:end+1]
            if len(result) == 0:
                return 'Invalid JSON format returned from the API'
    try:
        json_data = json.loads(result)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")

    return json_data

import mp3helper

def generate_audio(text):
    filename = 'adv_' + generate_audio_filename(text)
    mp3helper.cantonese_text_to_mp3(text, filename)
    return filename

def generate_audio_filename(text):
    """
    Generate a unique filename for audio based on MD5 hash of the input text.
    
    Args:
        text: The text string to be hashed
        
    Returns:
        A filename with MD5 hash and .mp3 extension
    """
    md5_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return f"{md5_hash}.mp3"

def get_audio_for_text(text):
    """
    Generate audio for the given text and return the filename.
    
    Args:
        text: The text to convert to audio
        
    Returns:
        Filename of the generated audio
    """
    filename = "adv_"+ generate_audio_filename(text)
    generate_audio(text)
    return filename

def add_audio_to_adventure(adventure_data):
    """
    Parses through the adventure JSON structure and adds audio file references
    for each text entry by calling get_audio_for_text.
    
    Args:
        adventure_data: The JSON adventure data structure
        
    Returns:
        Updated adventure data with audio file paths added
    """
    # Add audio for title if it exists
    if "cantonese_title" in adventure_data:
        adventure_data["title_audio"] = get_audio_for_text("".join(adventure_data["cantonese_title"]))
    
    # Add audio for start node
    if "startNode" in adventure_data:
        add_audio_to_node(adventure_data["startNode"])
    
    # Add audio for all nodes
    if "nodes" in adventure_data:
        for node in adventure_data["nodes"]:
            add_audio_to_node(node)
    
    return adventure_data

def add_audio_to_node(node):
    """
    Adds audio file references to a single node and its choices.
    
    Args:
        node: A node in the adventure structure
    """
    
    # Add audio for Cantonese text if available
    if "cantonese_text" in node:
        node["text_audio"] = get_audio_for_text("".join(node["cantonese_text"]))
    
    # Add audio for ending message if it exists    
    if "cantonese_endingMessage" in node:
        node["endingMessage_audio"] = get_audio_for_text("".join(node["cantonese_endingMessage"]))
    
    # Add audio for choices if they exist
    if "choices" in node and isinstance(node["choices"], list):
        for choice in node["choices"]:            
            if "cantonese_text" in choice:
                choice["text_audio"] = get_audio_for_text("".join(choice["cantonese_text"]))


def create_child_adventure(scenario):
    prompt = """
                                                   
                                                   
"Create a 'choose your own adventure' short story in JSON format. Follow this structure:


Include a unique id (integer) and creative title for the story.

Define a startNode with an engaging opening scene and 2-3 initial choices.

Build a nodes array containing all story paths. Each node must have:
id (string)
text (vivid scene description)
choices array (with text and nextNodeId), or
isEnd: true, isSuccess (boolean), and endingMessage for final outcomes.

Ensure choices lead to logical consequences (e.g., traps, discoveries, alternate paths).

Include at least 2 successful endings and 2 failure endings.

The language should be suitable for 8 year old children, with simple vocabulary and simple but engaging descriptions.

Example Themes (optional):
    - A bullying situation in a school playground
    - A lost pet in a neighborhood
    - A treasure hunt in a local park
    - A rescue mission for a friend in trouble
    - Surviving in a war zone
    - Helping a friend with a difficult family situation
    

Format Reference:

json

{  
  "id": 1,  
  "title": "[Your Story Title]",  
  "startNode": { /* ... */ },  
  "nodes": [ /* ... */ ]  
}  
Constraints:


All nextNodeId values must match existing node IDs.

Avoid dead-ends (non-end nodes must have choices).

Create at least 40 locations with unique scenes.

Use descriptive text to immerse the reader in the setting. """
    
    return create_adventure_from_prompt(prompt)


def create_ground_adventure(scenario):
    prompt = """
                                                   
                                                   
"Create a 'choose your own adventure' short story in JSON format. Follow this structure:


Include a unique id (integer) and creative title for the story.

Define a startNode with an engaging opening scene and 2-3 initial choices.

Build a nodes array containing all story paths. Each node must have:
id (string)
text (vivid scene description)
sdd_prompt (a prompt that will be used for stable diffusion to generate an illustration of the scene. Make sure the prompt include objects important to the story)
choices array (with text and nextNodeId), or
isEnd: true, isSuccess (boolean), and endingMessage for final outcomes.


Ensure choices lead to logical consequences (e.g., traps, discoveries, alternate paths).

Include at least 2 successful endings and 2 failure endings.

Example Themes (optional):
    - A political campaign in a third world corrupted country
    - A prison escape in 1950's russia
    - A survival situation in China during cultural revolution
    - A survival situation in Cambodja during Pol Pot regime
    - Overthrowing a corrupt government in an authoritian state
    - Solving a murder in Iceland   
    

Format Reference:

json

{  
  "id": 1,  
  "title": "[Your Story Title]",  
  "startNode": { /* ... */ },  
  "nodes": [ /* ... */ ]  
}  
Constraints:


All nextNodeId values must match existing node IDs.

Avoid dead-ends (non-end nodes must have choices).

Create at least 40 locations with unique scenes.

Use descriptive text to immerse the reader in the setting. """
    
    return create_adventure_from_prompt(prompt)


import textprocessing
def translate_to_cantonese(text):
    api = openrouter.OpenRouterAPI()
    """Translate text to Cantonese using OpenRouter API."""
    text = api.open_router_claude_3_5_sonnet("You are a cantonese translator."," Your task is to translate the following text to spoken Cantonese written in Traditional Characters. Try to keep it as close to spoken language as possible that people would use if they speak in a casual context. Only return the chinese, no jyutping or english text with explanations:" +text)
    tokens = textprocessing.split_text(text)
    return tokens

def translate_story_to_chinese(story):
    """Translate a story adventure to Chinese (Cantonese)."""
    # Translate the title
    if "title" in story:
        story["cantonese_title"] = translate_to_cantonese(story["title"])
    
    # Translate the start node
    if "startNode" in story:
        translate_node(story["startNode"])
    
    # Translate all nodes
    if "nodes" in story:
        for node in story["nodes"]:
            translate_node(node)
    
    return story

def translate_node(node):
    """Translate a single node and its choices recursively."""
    # Translate the main text of the node
    if "text" in node:
        node["cantonese_text"] = translate_to_cantonese(node["text"])
    
    # Translate ending message if it exists
    if "endingMessage" in node:
        node["cantonese_endingMessage"] = translate_to_cantonese(node["endingMessage"])

    
    # Translate choices if they exist
    if "choices" in node and isinstance(node["choices"], list):
        for choice in node["choices"]:
            if "text" in choice:
                choice["cantonese_text"] = translate_to_cantonese(choice["text"])




def extract_sdd_prompts(adventure_data):
    """
    Extracts all sdd_prompt fields from the adventure JSON structure.
    
    Args:
        adventure_data: The JSON adventure data structure
        
    Returns:
        A list of sdd_prompt strings
    """
    prompts = []
    
    # Check startNode for sdd_prompt
    if "startNode" in adventure_data and "sdd_prompt" in adventure_data["startNode"]:
        prompts.append(adventure_data["startNode"]["sdd_prompt"])
    
    # Check nodes for sdd_prompt
    if "nodes" in adventure_data:
        for node in adventure_data["nodes"]:
            if "sdd_prompt" in node:
                prompts.append(node["sdd_prompt"])
    
    for p in prompts:
        md5signature = hashlib.md5(p.encode('utf-8')).hexdigest()
        # write a file that has the name md5signature.prompt and contains the prompt
        with open(md5signature + ".prompt", "w", encoding="utf-8") as f:
            f.write(p)
            
    # scp all the md5files to a server and then delete them
    remote_destination = "chinese.eriktamm.com:/opt/prompts_to_process"
    
    # Find all adventure JSON filesupload_adventure_files
    all_files = glob.glob("*.prompt")
        
    
    if not all_files:
        print("No files found to upload.")
        return
    
    try:
        # Create the scp command
        scp_command = ["scp"] + all_files + [remote_destination]
        
        # Execute the scp command
        result = subprocess.run(scp_command, check=True, capture_output=True, text=True)        
        print(f"Successfully uploaded {len(all_files)} files to {remote_destination}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during upload: {e}")
        print(f"Command output: {e.stderr}")



def upload_adventure_files():
    """
    Uploads all adventure*.json files and adv_*.mp3 files to the server.
    
    This function uses scp to copy all adventure JSON files and audio MP3 files
    to the specified remote server destination.
    """
    remote_destination = "chinese.eriktamm.com:/var/www/html/adventures"
    
    # Find all adventure JSON filesupload_adventure_files
    json_files = glob.glob("adventure_*.json")
    
    # Find all adventure audio MP3 files
    mp3_files = glob.glob("adv_*.mp3")
    
    # Combine all files to upload
    all_files = json_files + mp3_files
    
    if not all_files:
        print("No files found to upload.")
        return
    
    try:
        # Create the scp command
        scp_command = ["scp"] + all_files + [remote_destination]
        
        # Execute the scp command
        result = subprocess.run(scp_command, check=True, capture_output=True, text=True)
        
        print(f"Successfully uploaded {len(all_files)} files to {remote_destination}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during upload: {e}")
        print(f"Command output: {e.stderr}")


def read_adventure_json(filename):
    """
    Reads a JSON file with UTF-8 encoding and returns the parsed structure.
    
    Args:
        filename: Path to the JSON file to read
        
    Returns:
        The parsed JSON data structure or None if an error occurs
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in {filename}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error reading {filename}: {e}")
        return None






if __name__ == "__main__":
    # Example usage

    print("Generating adventure")
    scenario = "A haunted mansion with shifting rooms"
    #adventure = create_child_adventure(scenario)
    adventure = create_ground_adventure(scenario)
    print("Original Adventure:", adventure)
    translated_adventure = translate_story_to_chinese(adventure)
    tran = json.dumps(translated_adventure)
    #translated_adventure = add_audio_to_adventure(translated_adventure)
    filename = "adventure_"+str(random.randint(0,1000000)) +".json"
    tran = json.dumps(translated_adventure)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tran)
    print("Translated Adventure JSON saved as adventure.json")
    print("Translated Adventure:", translated_adventure)
    upload_adventure_files()
    extract_sdd_prompts(translated_adventure)


    """"
    Hmm, the old bird's nest,' she rasps, taking a long sip. 'Elevated patrols tonight. And cameras, new ones, on the lower levels. Best avoid the obvious paths.' Her eyes gleam with a strange light. You've gained crucial insight, but it cost you an hour and a precious few credits.
    """