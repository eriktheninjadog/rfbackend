#adventure.py



import openrouter
import json


import hashlib
import subprocess
import os
import random
import glob
import deepinfra


def create_adventure_background_context_from_prompt(themes):
    api = openrouter.OpenRouterAPI()
    
    description = """        
    You are a creative writer. Your task is to create the background for a 'choose your own adventure' story. 
    Outline the enviroment, 
            the main characters (names, gender, character, description),
            locations, 
            the overall goal with the adventure and possible success and failure endings. 
    Here is a list of possible themese:
    """ + themes
    return api.mixtral_8x22b_instruct("You are a creative writer. Your task is to create a 'choose your own adventure' story.",description)


def create_adventure_background_context_from_prompt(themes):
    api = openrouter.OpenRouterAPI()
    
    description = """        
    You are a creative writer. Your task is to create the background for a 'choose your own adventure' story. 
    Outline the enviroment, 
            the main characters (names, gender, character, description),
            locations, 
            the overall goal with the adventure and possible success and failure endings. 
    Here is a list of possible themese:
    """ + themes
    return api.mixtral_8x22b_instruct("You are a creative writer. Your task is to create a 'choose your own adventure' story.",description)





def create_adventure_from_prompt(prompt,dont_use_cantonese=False):  
    api = openrouter.OpenRouterAPI()
    #result = api.open_router_claude_4_0_sonnet("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully. All text descriptions must be in spoken Cantonese using traditional characters. ", prompt)
    #result = api.open_router_gemini_25_flash("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully. All text descriptions must be in spoken Cantonese using traditional characters. ", prompt)
    if dont_use_cantonese:
        api = openrouter.OpenRouterAPI()
        #result = deepinfra.call_deepinfra_gemini_flash_2_5("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully. All text descriptions must be in written Mandarin Taiwanese style using traditional characters. ", prompt)        
        result = api.open_router_gemini_25_flash("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully. All text descriptions must be in written Mandarin Taiwanese style using traditional characters. ", prompt)
    else:
        result = deepinfra.call_deepinfra_gemini_flash_2_5("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully. All text descriptions must be in spoken Cantonese using traditional characters. ", prompt)
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
    lola = str(random.randint(100,999))
    prompt = """
                                                   
                     
"Create a 'choose your own adventure' story in JSON for

mat. All texts should be in spoken Cantonese using traditional characters, Cantonese as spoken in Hong Kong, avoid standard Chinese. Follow this structure:


Include a unique id (integer) and creative title for the story.

Define a startNode with an engaging opening scene and 2-3 initial choices.

Build a nodes array containing all story paths. Each node must have:
id (string)
text (one brief sentence describing scene using simple vocabulary)
sdd_prompt (a prompt that will be used for stable diffusion to generate an illustration of the scene. Make sure the prompt include objects important to the story. The prompt should be in English.)
choices array (with text and nextNodeId), or
isEnd: true, isSuccess (boolean), and endingMessage for final outcomes.

Ensure choices lead to logical consequences (e.g., traps, discoveries, alternate paths).

Include at least 2 successful endings and 2 failure endings.At least 10 different locations.

The language should be suitable for 10 year old children, with simple daily vocabulary. Avoid using vocabulary that is not useful in daily life. Make this about real life and the problems that a child at age 10 might struggle with (bullying, family problems, too much homework, moving to a new school).


""" + lola + """

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

Make sure to only create choices that actually goes to an existing node

Use descriptive text to immerse the reader in the setting. """
    
    return create_adventure_from_prompt(prompt)



def remove_node_from_adventure(adventure_data, node_id_to_remove):
    """
    Removes a node with a specific ID from an adventure and all choices that lead to it.
    
    Args:
        adventure_data: The JSON adventure data structure
        node_id_to_remove: The ID of the node to remove
        
    Returns:
        The updated adventure data structure
    """
    # Check if the node to remove is the start node
    if "startNode" in adventure_data and adventure_data["startNode"].get("id") == node_id_to_remove:
        print(f"Cannot remove start node with ID {node_id_to_remove}")
        return adventure_data
    
    # Remove the node from nodes list
    if "nodes" in adventure_data:
        adventure_data["nodes"] = [node for node in adventure_data["nodes"] if node.get("id") != node_id_to_remove]
    
    # Remove choices that lead to the removed node
    # First in the startNode
    if "startNode" in adventure_data and "choices" in adventure_data["startNode"]:
        adventure_data["startNode"]["choices"] = [
            choice for choice in adventure_data["startNode"]["choices"] 
            if choice.get("nextNodeId") != node_id_to_remove
        ]
    
    # Then in all other nodes
    if "nodes" in adventure_data:
        for node in adventure_data["nodes"]:
            if "choices" in node:
                node["choices"] = [
                    choice for choice in node["choices"] 
                    if choice.get("nextNodeId") != node_id_to_remove
                ]
    
    print(f"Removed node with ID {node_id_to_remove} and all choices leading to it")
    return adventure_data



def fix_dead_ends(adventure_data, max_attempts=10):
    """
    Identifies and removes dead ends in the adventure to ensure a valid story structure.
    
    Args:
        adventure_data: The JSON adventure data structure
        max_attempts: Maximum number of removal attempts to prevent infinite loops
        
    Returns:
        Updated adventure data with dead ends removed
    """
    attempts = 0
    while attempts < max_attempts:
        # Check for dead ends
        dead_ends = check_for_dead_ends(adventure_data)
        
        if not dead_ends:
            print("No dead ends found in the adventure.")
            return adventure_data
            
        print(f"Found {len(dead_ends)} dead ends: {dead_ends}")
        
        # Remove each dead end
        for node_id in dead_ends:
            if node_id == "startNode":
                print("Warning: Start node is a dead end but cannot be removed.")
                continue
                
            print(f"Removing dead end node: {node_id}")
            adventure_data = remove_node_from_adventure(adventure_data, node_id)
        
        attempts += 1
        
        # Recheck after removals
        remaining_dead_ends = check_for_dead_ends(adventure_data)
        if not remaining_dead_ends or remaining_dead_ends == dead_ends:
            # Either all fixed or we can't fix any more
            break
    
    # Final check
    final_dead_ends = check_for_dead_ends(adventure_data)
    if final_dead_ends:
        print(f"Warning: Could not remove all dead ends. Remaining: {final_dead_ends}")
    else:
        print("Successfully removed all dead ends.")
        
    return adventure_data

def check_for_dead_ends(adventure_data):
    """
    Checks for dead-ends in a choose-your-own adventure story.
    A dead-end is a node that isn't marked as an ending but has no choices.
    
    Args:
        adventure_data: The JSON adventure data structure
        
    Returns:
        A list of node IDs that are dead-ends
    """
    dead_ends = []
    
    # Check start node
    if "startNode" in adventure_data:
        if ("choices" not in adventure_data["startNode"] or not adventure_data["startNode"]["choices"]) and \
            ("isEnd" not in adventure_data["startNode"] or not adventure_data["startNode"]["isEnd"]):
            dead_ends.append("startNode")
    
    # Check all other nodes
    if "nodes" in adventure_data:
        for node in adventure_data["nodes"]:
            if "id" in node and \
                ("choices" not in node or not node["choices"]) and \
                ("isEnd" not in node or not node["isEnd"]):
                dead_ends.append(node["id"])
    
    knownids = []
    for node in adventure_data.get("nodes", []):
        knownids.append( node["id"] )
    # Print total number of locations
    print("Total number of locations: " + str(len(knownids)))
    # Check for dead-ends in choices
    for node in adventure_data.get("nodes", []):
        if "choices" in node:
            for choice in node["choices"]:
                next_node_id = choice.get("nextNodeId")
                if next_node_id and next_node_id not in knownids:
                    # If the next node ID is not in known IDs, it's a dead-end
                    dead_ends.append(next_node_id)
                    print("missing " + next_node_id)
                    # If the next node ID is known, check if it has choices
                    # Check if the next node is a dead-end

    return dead_ends




def create_article_adventure(article,words_to_use=None):
    if words_to_use != None:
        wordlist = "\ninclude these words in the adventure " + str(words_to_use) + "\n"
    else:
        wordlist = ""
        
    prompt = """
                                                   
                                                   
"Create a 'choose your own adventure' medium story in JSON format. All texts should be in traditional chinese characters. Follow this structure:


Include a unique id (integer) and creative title for the story.

Define a startNode with an engaging opening scene and 2-3 initial choices.

Build a nodes array containing all story paths. Each node must have:
id (string)
text (one brief sentence describing scene)
sdd_prompt (a prompt that will be used for stable diffusion to generate an illustration of the scene. Make sure the prompt include objects important to the story. The prompt should be in English.)
choices array (with text and nextNodeId), or
isEnd: true, isSuccess (boolean), and endingMessage for final outcomes.


Ensure choices lead to logical consequences (e.g., traps, discoveries, alternate paths).

Include at least 2 successful endings and 3 failure endings. At least 30 different locations.

""" + wordlist + " " + str(random.randint(0,100))+ """ 

The adventure should be based on the following article and use vocabulary from this article: """ + article + """    
        
Format Reference:

json

{  
  "id": 1,  
  "title": "[Your Story Title]",  
  "startNode": { /* ... */ },  
  "overall": "[overall description of the scenario, atmosphere and goals of the adventure]"
  "nodes": [ /* ... */ ]
}  
Constraints:


All nextNodeId values must match existing node IDs. Verify that all choices nextNodeId correspond to an existing node, keep adding nodes that doesn't yet exist.

Avoid dead-ends (non-end nodes must have choices).

Use descriptive text to immerse the reader in the setting. """
    
    return create_adventure_from_prompt(prompt,dont_use_cantonese=True)



def create_vocab_adventure(article,words_to_use=None):
    if words_to_use != None:
        wordlist = "\ninclude these words in the adventure " + str(words_to_use) + "\n"
    else:
        wordlist = ""
        
    prompt = """
                                                   
                                                   
"Create a 'choose your own adventure' medium story in JSON format. All texts should be in traditional chinese characters. Follow this structure:


Include a unique id (integer) and creative title for the story.

Define a startNode with an engaging opening scene and 2-3 initial choices.

Build a nodes array containing all story paths. Each node must have:
id (string)
text (use similar language to the text provided)
sdd_prompt (a prompt that will be used for stable diffusion to generate an illustration of the scene. Make sure the prompt include objects important to the story. The prompt should be in English.)
choices array (with text and nextNodeId), or
isEnd: true, isSuccess (boolean), and endingMessage for final outcomes.


Ensure choices lead to logical consequences (e.g., traps, discoveries, alternate paths).

Include at least 2 successful endings and 3 failure endings. At least 30 different locations.

""" + wordlist + " " + str(random.randint(0,100))+ """ 

Use grammar, vocabulary and the style of this article to construct the adventure: """ + article + """    
        
Format Reference:

json

{  
  "id": 1,  
  "title": "[Your Story Title]",  
  "startNode": { /* ... */ },  
  "overall": "[overall description of the scenario, atmosphere and goals of the adventure]"
  "nodes": [ /* ... */ ]
}  
Constraints:


All nextNodeId values must match existing node IDs. Verify that all choices nextNodeId correspond to an existing node, keep adding nodes that doesn't yet exist.

Avoid dead-ends (non-end nodes must have choices).

Use descriptive text to immerse the reader in the setting but try to follow the style of the text provided. """
    
    return create_adventure_from_prompt(prompt,dont_use_cantonese=True)


def create_ground_adventure(scenario,words_to_use=None):
    if words_to_use != None:
        wordlist = "\ninclude these words in the adventure " + str(words_to_use) + "\n"
    else:
        wordlist = ""
        
    prompt = """
                                                   
                                                   
"Create a 'choose your own adventure' medium story in JSON format. All texts should be in spoken Cantonese using traditional characters. Follow this structure:


Include a unique id (integer) and creative title for the story.

Define a startNode with an engaging opening scene and 2-3 initial choices.

Build a nodes array containing all story paths. Each node must have:
id (string)
text (one brief sentence describing scene)
sdd_prompt (a prompt that will be used for stable diffusion to generate an illustration of the scene. Make sure the prompt include objects important to the story. The prompt should be in English.)
choices array (with text and nextNodeId), or
isEnd: true, isSuccess (boolean), and endingMessage for final outcomes.


Ensure choices lead to logical consequences (e.g., traps, discoveries, alternate paths).

Include at least 2 successful endings and 3 failure endings. At least 30 different locations.

""" + wordlist + " " + str(random.randint(0,100))+ """ 

Example Themes (optional):
    - Hong Kong during the japanese occupation in World War II. Include historical events and figures.
    - The 2003 SARS outbreak in Hong Kong. Include health and safety measures.  
    - The 1997 handover of Hong Kong to China. Include historical events and figures.
    - The fincancial stormy waters of 1990's Hong Kong. Include financial terms and concepts.
    
        
Format Reference:

json

{  
  "id": 1,  
  "title": "[Your Story Title]",  
  "startNode": { /* ... */ },  
  "overall": "[overall description of the scenario, atmosphere and goals of the adventure]"
  "nodes": [ /* ... */ ]
}  
Constraints:


All nextNodeId values must match existing node IDs. Verify that all choices nextNodeId correspond to an existing node, keep adding nodes that doesn't yet exist.

Avoid dead-ends (non-end nodes must have choices).

Use descriptive text to immerse the reader in the setting. """
    
    return create_adventure_from_prompt(prompt)


import textprocessing
def translate_to_cantonese(text):
    api = openrouter.OpenRouterAPI()
    """Translate text to Cantonese using OpenRouter API."""
    text = api.open_router_claude_3_5_sonnet("You are a cantonese translator."," Your task is to translate the following text to spoken Cantonese written in Traditional Characters. Try to keep it as close to spoken language as possible that people would use if they speak in a casual context. Only return the chinese, no jyutping or english text with explanations:" +text)
    tokens = textprocessing.split_text(text)
    return tokens

def tokenize_story(story):
    # Translate the title
    if "title" in story:
        story["cantonese_title"] = textprocessing.split_text(story["title"])
    
    # Translate the start node
    if "startNode" in story:
        tokenize_node(story["startNode"])
    
    # Translate all nodes
    if "nodes" in story:
        for node in story["nodes"]:
            tokenize_node(node)
    
    return story

def tokenize_node(node):
    """Translate a single node and its choices recursively."""
    # Translate the main text of the node
    if "text" in node:
        node["cantonese_text"] = textprocessing.split_text(node["text"])
    
    # Translate ending message if it exists
    if "endingMessage" in node:
        node["cantonese_endingMessage"] = textprocessing.split_text(node["endingMessage"])

    
    # Translate choices if they exist
    if "choices" in node and isinstance(node["choices"], list):
        for choice in node["choices"]:
            if "text" in choice:
                choice["cantonese_text"] = textprocessing.split_text(choice["text"])



def walk_through_ends(adventure_data):
    """
    Returns all possible paths through the adventure from start to end nodes.
    
    Args:
        adventure_data: The JSON adventure data structure
        
    Returns:
        A list of lists, where each inner list represents a complete path through
        the adventure, starting with the start node and ending with an end node.
    """
    all_paths = []
    
    # Create a dictionary to map node IDs to nodes for easy lookup
    node_map = {}
    if "nodes" in adventure_data:
        for node in adventure_data["nodes"]:
            if "id" in node:
                node_map[node["id"]] = node
    
    # Start the traversal from the startNode
    if "startNode" in adventure_data:
        start_node = adventure_data["startNode"]
        # Start a recursive depth-first search from the start node
        traverse_path(start_node, [start_node], node_map, all_paths)
    
    return all_paths

def traverse_path(current_node, current_path, node_map, all_paths):
    """
    Recursively traverses the adventure graph depth-first to find all paths.
    
    Args:
        current_node: The current node being explored
        current_path: The path taken so far (list of nodes)
        node_map: Dictionary mapping node IDs to nodes
        all_paths: List to collect complete paths
    """
    # If this is an end node, we've found a complete path
    if "isEnd" in current_node and current_node["isEnd"]:
        # Make a copy of the current path and add it to all_paths
        all_paths.append(current_path.copy())
        return
    
    # If this node has choices, explore each one
    if "choices" in current_node and isinstance(current_node["choices"], list):
        for choice in current_node["choices"]:
            if "nextNodeId" in choice:
                next_node_id = choice["nextNodeId"]
                if next_node_id in node_map:
                    next_node = node_map[next_node_id]
                    # Only proceed if this doesn't create a cycle
                    if next_node not in current_path:
                        # Continue traversing with the next node added to the path
                        traverse_path(next_node, current_path + [next_node], node_map, all_paths)
    


def enrich_adventure_descriptions(adventure_data,words_to_use=None):
    
    if words_to_use != None:
        add_list = "\ninclude these words where you can " + str(words_to_use) + "\n"
    else:
        add_list = ""

    """
    Enhances the descriptions in all nodes of the adventure by using
    an AI model to expand and enrich them.
    
    Args:
        adventure_data: The JSON adventure data structure
        
    Returns:
        Updated adventure data with enriched descriptions
    """
    api = openrouter.OpenRouterAPI()
    
    # Collect all descriptions
    descriptions = []
    description_mapping = []  # Store (node, field) tuples to map back enriched descriptions
    
    # Check startNode description
    if "startNode" in adventure_data and "text" in adventure_data["startNode"]:
        descriptions.append(adventure_data["startNode"]["text"])
        description_mapping.append((adventure_data["startNode"], "text"))
    
    # Check all nodes descriptions
    if "nodes" in adventure_data:
        for node in adventure_data["nodes"]:
            if "text" in node:
                descriptions.append(node["text"])
                description_mapping.append((node, "text"))
            
            # Also include ending messages if they exist
            if "endingMessage" in node:
                descriptions.append(node["endingMessage"])
                description_mapping.append((node, "endingMessage"))
    
    if not descriptions:
        print("No descriptions found to enrich.")
        return adventure_data
    
    # Prepare prompt for the AI model
    
    prompt = f"""Please expand and enrich the following descriptions to make them more vivid,
    engaging, and immersive. Keep the core meaning and key details intact, but add sensory details,
    atmosphere, and depth to each description. Each description should be enhanced but still concise.
    Return your response as a numbered list matching the input list format.
    {add_list}

    Descriptions:
    """ + "\n".join([f"{i+1}. {desc}" for i, desc in enumerate(descriptions)])
    
    # Call the AI model to enrich descriptions
    print("Enriching descriptions using AI...")
    enriched_text = api.open_router_gemini_25_flash(
        "You are an expert at enhancing descriptive text for interactive stories.",
        prompt
    )
    
    # Parse the enriched descriptions
    enriched_descriptions = []
    
    # Simple parser for numbered list format
    lines = enriched_text.strip().split('\n')
    current_desc = ""
    
    for line in lines:
        if line.strip() == "":
            continue
            
        # Check if this line starts a new numbered item
        if line.strip()[0].isdigit() and ". " in line:
            if current_desc:  # Save previous description if it exists
                enriched_descriptions.append(current_desc.strip())
                current_desc = ""
            
            # Extract just the description part after the number
            parts = line.split(". ", 1)
            if len(parts) > 1:
                current_desc = parts[1]
            else:
                current_desc = parts[0]  # Just in case there's no period after number
        else:
            # Continue previous description
            current_desc += " " + line.strip()
    
    # Add the last description if it exists
    if current_desc:
        enriched_descriptions.append(current_desc.strip())
    
    # Ensure we have the correct number of descriptions
    if len(enriched_descriptions) != len(descriptions):
        print(f"Warning: Got {len(enriched_descriptions)} enriched descriptions but expected {len(descriptions)}.")
        print("Using original descriptions to avoid data loss.")
        return adventure_data
    
    # Replace original descriptions with enriched ones
    for i, (node, field) in enumerate(description_mapping):
        if i < len(enriched_descriptions):
            node[field] = enriched_descriptions[i]
    
    print(f"Successfully enriched {len(enriched_descriptions)} descriptions.")
    return adventure_data


def continue_adventure(adv):
    """
    Takes an existing adventure, removes one of the end-nodes, and expands it into
    a new branch with at least one successful ending and one failure ending.
    The new branch will have a depth between 5-10 levels.
    
    Args:
        adv: The adventure data structure to expand
        
    Returns:
        The updated adventure data structure
    """
    api = openrouter.OpenRouterAPI()
    
    # Find all end nodes
    end_nodes = []
    if "nodes" in adv:
        for node in adv["nodes"]:
            if "isEnd" in node and node["isEnd"]:
                end_nodes.append(node)
    
    if not end_nodes:
        print("No end nodes found to expand.")
        return adv
    
    # Select a random end node to expand
    node_to_expand = random.choice(end_nodes)
    
    # Get the original node's ID and remove isEnd property
    original_id = node_to_expand["id"]
    node_to_expand.pop("isEnd", None)
    node_to_expand.pop("isSuccess", None)
    node_to_expand.pop("endingMessage", None)
    node_to_expand.pop("cantonese_endingMessage", None)
    
    # Extract background context from start node
    background_context = ""
    if "startNode" in adv and "text" in adv["startNode"]:
        background_context = adv["startNode"]["text"]
    elif "overall" in adv:
        background_context = adv["overall"]
    
    # Get the current text of the node to expand
    current_text = node_to_expand.get("text", "")
    
    # Create a prompt for expanding this node
    prompt = f"""
    Continue this adventure branch from the current node. The current scene is:
    "{current_text}"
    
    Background context for the adventure:
    "{background_context}"
    
    Create a branch with 5-10 new nodes that continues from this point. Include:
    - At least one successful ending
    - At least one failure ending
    - Meaningful choices that branch the story
    
    Format the response as a valid JSON array of nodes, where each node has:
    - id: a unique string (use the format "new_[number]")
    - text: descriptive scene text
    - sdd_prompt: English prompt for image generation 
    - choices: array of options (each with text and nextNodeId), or
    - isEnd: true, isSuccess: boolean, and endingMessage for final outcomes
    
    All nextNodeId values should reference valid nodes in your response.
    """
    
    # Get the new nodes from the API
    print("Expanding adventure branch...")
    response = api.open_router_gemini_25_flash(
        "You are an expert adventure story writer creating JSON content.",
        prompt
    )
    
    # Extract the JSON array from the response
    try:
        # Find JSON array in the response
        json_start = response.find('[')
        json_end = response.rfind(']')
        
        if json_start == -1 or json_end == -1:
            print("Could not find JSON array in response. Trying to fix...")
            # Try to request a fix
            response = api.open_router_nova_lite_v1(
                f"Fix the JSON array in this response: {response}\nReturn only the valid JSON array."
            )
            json_start = response.find('[')
            json_end = response.rfind(']')
        
        if json_start != -1 and json_end != -1:
            json_str = response[json_start:json_end + 1]
            new_nodes = json.loads(json_str)
        else:
            print("Failed to extract JSON array. Using fallback approach.")
            # Try to parse the whole response as JSON
            new_nodes = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("Falling back to default expansion.")
        # Create a simple fallback expansion
        new_nodes = [
            {
                "id": "new_1",
                "text": f"Continuing from {current_text}. You face a critical decision.",
                "sdd_prompt": "Character at a crossroads facing a difficult choice in a tense situation",
                "choices": [
                    {"text": "Take the risky path", "nextNodeId": "new_2"},
                    {"text": "Follow the safer route", "nextNodeId": "new_3"}
                ]
            },
            {
                "id": "new_2", 
                "text": "The risky path leads to danger.",
                "sdd_prompt": "Character in dangerous situation with obstacles",
                "isEnd": True,
                "isSuccess": False,
                "endingMessage": "Your risk did not pay off. The adventure ends in failure."
            },
            {
                "id": "new_3",
                "text": "The safer route leads to success.",
                "sdd_prompt": "Character achieving their goal triumphantly",
                "isEnd": True,
                "isSuccess": True,
                "endingMessage": "Your caution was rewarded. You succeed!"
            }
        ]
    
    # Add the new nodes to the adventure
    if "nodes" not in adv:
        adv["nodes"] = []
    
    # Update the original node to point to the first new node
    if new_nodes:
        first_new_node = new_nodes[0]["id"]
        node_to_expand["choices"] = [
            {"text": "Continue your journey", "nextNodeId": first_new_node}
        ]
        
        # Add all the new nodes
        adv["nodes"].extend(new_nodes)
        
        # Translate the new nodes to Cantonese
        for node in new_nodes:
            tokenize_node(node)
    
    # Check for dead ends in the updated adventure
    dead_ends = check_for_dead_ends(adv)
    if dead_ends:
        print(f"Warning: The expanded adventure has {len(dead_ends)} dead ends: {dead_ends}")
    
    return adv

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


def upload_adventure_files(is_audio=False):
    """
    Uploads all adventure*.json files and adv_*.mp3 files to the server.
    
    This function uses scp to copy all adventure JSON files and audio MP3 files
    to the specified remote server destination.
    """
    if is_audio:
        remote_destination = "chinese.eriktamm.com:/var/www/html/audioadventures"
    else:
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
        scp_command = ["scp"]    + all_files + [remote_destination]
        
        # Execute the scp commandn
        result = subprocess.run(scp_command, check=True, capture_output=True, text=True)
        
        print(f"Successfully uploaded {len(all_files)} files to {remote_destination}")
        # Delete any intermediate step files and previous adventure files before upload
        
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


def download_and_check_adventures():
    """
    Downloads all adventure*.json files from the server, checks for dead ends,
    and deletes files with dead ends from the server.
    
    This function uses scp to download all adventure JSON files from the specified
    remote server, then checks each file for dead ends using the check_for_dead_ends function.
    Files with dead ends are deleted from the remote server.
    
    Returns:
        A dictionary mapping filenames to their dead end node IDs
    """
    remote_source = "erik@chinese.eriktamm.com:/var/www/html/adventures/adventure_*.json"
    remote_directory = "chinese.eriktamm.com:/var/www/html/adventures/"
    local_destination = "."
    
    try:
        # Create a temporary directory for downloaded files
        temp_dir = "temp_adventures"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create the scp command to download files
        scp_command = ["scp", remote_source, temp_dir]
        
        print("Downloading adventure files...")
        result = subprocess.run(scp_command, check=True, capture_output=True, text=True)
        print(f"Successfully downloaded adventure files")
        
        # Check each downloaded file for dead ends
        results = {}
        files_to_delete = []
        
        for filename in glob.glob(f"{temp_dir}/adventure_*.json"):
            print(f"Checking {filename} for dead ends...")
            adventure_data = read_adventure_json(filename)
            if adventure_data:
                dead_ends = check_for_dead_ends(adventure_data)
                if dead_ends:
                    print(f"Found {len(dead_ends)} dead ends in {filename}: {dead_ends}")
                    results[filename] = dead_ends
                    # Add file to delete list
                    files_to_delete.append(os.path.basename(filename))
                else:
                    print(f"No dead ends found in {filename}")
                    results[filename] = []
        
        # Delete files with dead ends from the remote server
        if files_to_delete:
            print(f"Deleting {len(files_to_delete)} files with dead ends from server...")
            for file_to_delete in files_to_delete:
                remote_file_path = f"{remote_directory}{file_to_delete}"
                ssh_command = ["ssh", "erik@chinese.eriktamm.com", f"rm -f /var/www/html/adventures/{file_to_delete}"]
                
                try:
                    delete_result = subprocess.run(ssh_command, check=True, capture_output=True, text=True)
                    print(f"Deleted {file_to_delete} from server")
                except subprocess.CalledProcessError as e:
                    print(f"Error deleting {file_to_delete}: {e.stderr}")
        
        return results
        
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e}")
        print(f"Command output: {e.stderr}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}
    
    
def make_child_audio():
        scenario = "A haunted mansion with shifting rooms"
        adventure = create_child_adventure(scenario)
        ids = check_for_dead_ends(adventure)
        while len(ids) > 0:
            print("Found dead ends, filling them in")
            exit(0)                
        #adventure = enrich_adventure_descriptions(adventure)
        print("Original Adventure:", adventure)
        ids = check_for_dead_ends(adventure)
        while len(ids) > 0:
            print("Found dead ends, filling them in")
            exit(0)
        translated_adventure = tokenize_story(adventure)
        tran = json.dumps(translated_adventure)
        print("Dead ends" + str(check_for_dead_ends(translated_adventure)))
        translated_adventure = add_audio_to_adventure(translated_adventure)
        tran = json.dumps(translated_adventure)
        filename = "adventure_"+str(random.randint(0,1000000)) +".json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(tran)
        upload_adventure_files(is_audio=True)
        extract_sdd_prompts(translated_adventure)
    


def make_article_adventure(article_text,words_to_use=None,use_vocab=False):
    if use_vocab:   
        adventure = create_article_adventure(article_text,words_to_use=words_to_use)
    else:
        adventure = create_vocab_adventure(article_text,words_to_use=words_to_use)
    ids = check_for_dead_ends(adventure)
    print("Original Adventure:", adventure)
    ids = check_for_dead_ends(adventure)
    adventure = fix_dead_ends(adventure)
    while len(ids) > 0:
        print("Found dead ends, filling them in")
        exit(0)
    translated_adventure = tokenize_story(adventure)
    tran = json.dumps(translated_adventure)
    filename = "adventure_"+str(random.randint(0,1000000)) +".json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tran)
    upload_adventure_files(is_audio=False)
    extract_sdd_prompts(translated_adventure)

    
import time

def generate_adult_adventure(resume_from_step=None, saved_data_file=None,extend_steps = 0,words_to_use=None,add_audio=False):
    """
    Generates an adult adventure with intermediate results saved to files.
    
    Args:
        resume_from_step: Step number to resume from (1-8)
        saved_data_file: Path to saved data file to load
        
    Steps:
        1. Create initial adventure
        2. Continue adventure (multiple rounds)
        3. Enrich descriptions
        4. Tokenize story
        5. Write to file and upload
        6. Extract prompts
    """
    adventure = None
    step_number = 1
    
    # Load saved data if resuming
    if resume_from_step and saved_data_file:
        try:
            with open(saved_data_file, "r", encoding="utf-8") as f:
                adventure = json.load(f)
            print(f"Loaded saved data from {saved_data_file}")
            step_number = resume_from_step
        except Exception as e:
            print(f"Error loading saved data: {e}")
            return
    
    # Step 1: Create initial adventure
    if step_number <= 1:
        print("Step 1: Generating initial adventure")
        scenario = "A haunted mansion with shifting rooms"
        adventure = create_ground_adventure(scenario,words_to_use=words_to_use)
        
        # Save intermediate result
        step_file = f"a_step1_{int(time.time())}.json"
        with open(step_file, "w", encoding="utf-8") as f:
            json.dump(adventure, f, ensure_ascii=False, indent=2)
        print(f"Saved step 1 result to {step_file}")
        
        # Check for dead ends
        ids = check_for_dead_ends(adventure)
        if len(ids) > 0:
            print(f"Found dead ends: {ids}")
            print("Please fix these before continuing")
            return
    
    # Step 2: Continue adventure
    if step_number <= 2:
        print("Step 2: Expanding adventure branches")
        for i in range(extend_steps):
            print(f"Expansion round {i+1}/8")
            adventure = continue_adventure(adventure)
            
            # Save intermediate result after each expansion
            step_file = f"a_step2_{i+1}_{int(time.time())}.json"
            with open(step_file, "w", encoding="utf-8") as f:
                json.dump(adventure, f, ensure_ascii=False, indent=2)
            print(f"Saved expansion {i+1} result to {step_file}")
            
            # Check for dead ends
            ids = check_for_dead_ends(adventure)
            if len(ids) > 0:
                print(f"Found dead ends: {ids}")
                print("Please fix these before continuing")
                return
    
    # Step 3: Enrich descriptions
    if step_number <= 3:
        print("Step 3: Enriching adventure descriptions")
        adventure = enrich_adventure_descriptions(adventure,words_to_use=words_to_use)
        
        # Save intermediate result
        step_file = f"a_step3_{int(time.time())}.json"
        with open(step_file, "w", encoding="utf-8") as f:
            json.dump(adventure, f, ensure_ascii=False, indent=2)
        print(f"Saved step 3 result to {step_file}")
        
        # Check for dead ends
        ids = check_for_dead_ends(adventure)
        if len(ids) > 0:
            print(f"Found dead ends: {ids}")
            print("Please fix these before continuing")
            return
    
    # Step 4: Tokenize the story
    if step_number <= 4:
        print("Step 4: Translating and tokenizing story")
        translated_adventure = tokenize_story(adventure)
        
        # Save intermediate result
        step_file = f"a_step4_{int(time.time())}.json"
        with open(step_file, "w", encoding="utf-8") as f:
            json.dump(translated_adventure, f, ensure_ascii=False, indent=2)
        print(f"Saved step 4 result to {step_file}")
        
        print("Dead ends: " + str(check_for_dead_ends(translated_adventure)))
        adventure = translated_adventure
    
    # Step 5: Write to file and upload
    if step_number <= 5:
        print("Step 5: Writing to file and uploading")
        filename = "adventure_" + str(random.randint(0, 1000000)) + ".json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(adventure, f, ensure_ascii=False, indent=2)
        print(f"Saved final adventure to {filename}")
        upload_adventure_files()
    
    # Step 6: Extract prompts
    if step_number <= 6:
        print("Step 6: Extracting prompts for image generation")
        extract_sdd_prompts(adventure)
        print("Completed all steps")
    
    if add_audio:
        print("Adding audio to adventure")
        translated_adventure = add_audio_to_adventure(adventure)
        filename = "adv_" + str(random.randint(0, 1000000)) + ".json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(translated_adventure, f, ensure_ascii=False, indent=2)
        print(f"Saved adventure with audio to {filename}")
        upload_adventure_files(is_audio=True)
        
           
    

    if __name__ == "__main__":
        """
        upload_adventure_files(is_audio=True)
        for i in range(0,5):
            make_child_audio()
        exit(0)
       """
        # Example 
        #result = create_adventure_background_context_from_prompt("A protest turning into a riot during Hong Kong protests 2019\nBeijing during the Cultural Revolution\nNorthern Burma in civil war")
        #print(result)
        
        #exit(-1)

        #download_and_check_adventures()
        #adv = read_adventure_json("temp_adventures/adventure_268473.json")
        #paths = walk_through_ends(adv)
        """"
        Hmm, the old bird's nest,' she rasps, taking a long sip. 'Elevated patrols tonight. And cameras, new ones, on the lower levels. Best avoid the obvious paths.' Her eyes gleam with a strange light. You've gained crucial insight, but it cost you an hour and a precious few credits.
        """        
        # To run from beginning:
        #generate_adult_adventure()
        
        
       

import remoteapiclient

if __name__ == "__main__":
    words = remoteapiclient.managelist_client("get",name="nextadventure")
    
    print(str(words))
    
    make_article_adventure("""

中共中央政治局委員、國務院副總理何立峰，在北京人民大會堂會見荷蘭路易達孚集團董事會主席瑪格麗特。

何立峰表示，中國致力全面推進高質量發展，正在加快建設發展全國統一大市場，人民對美好生活的嚮往正不斷推動農食產業發展釋放巨大內需潛力，強調中國著力創建穩定開放的貿易和營商環境，歡迎路易達孚集團在內的更多外資企業深化對華務實合作，共享發展機遇。

瑪格麗特表示，集團將繼續深耕中國市場，積極推進農產品進口來源多元化，為維護全球農業供應鏈穩定暢通貢獻積極力量。

""",use_vocab=True)
    
    
    
    make_article_adventure("""

一名49歲越南女子失蹤，警方正循謀殺方向調查，追緝一名持「行街紙」的非華裔男子。調查發現，失蹤女子與涉案男子曾進入長沙灣一幢大廈，其後男子多次持重物出入，並懷疑不斷棄置物品，而在涉事單位就發現懷疑血濺痕跡，不排除案件涉及金錢糾紛。

另外，警方拘捕一名25歲非華裔、持「行街紙」女子，相信她涉嫌多次向男子提供藏身地點，而被捕女子與男子相信屬情侶關係。

警方表示，失蹤女子持香港身份證，她的家人上周六報案，指女子失蹤。警方之後發現有可疑，發現失蹤女子曾與一名男子進入青山道152號一幢大廈，其後女事主並無離開，但男子多次出入，並手持較重物品，懷疑在附近後巷等位置不斷棄置物品。調查相信，失蹤女子與疑犯相識。

警方下午到屯門稔灣堆填區搜證。警方指，案情嚴重，期望可從中找到重要線索，亦會繼續在本港多處繼續搜證。
""",use_vocab=True)

    # generate_adult_adventure(extend_steps=7, words_to_use=words,add_audio=False)
    # Uncomment to generate a child adventure


    #generate_adul(extend_steps=4,e(0,5):
    #    make_child_audio()
  
    """
    upload_adventure_files(is_audio=True)
    for i in range(0,5):
        make_child_audio()
    exit(0)
   """
    # Example 
    #result = create_adventure_background_context_from_prompt("A protest turning into a riot during Hong Kong protests 2019\nBeijing during the Cultural Revolution\nNorthern Burma in civil war")
    #print(result)
    
    #exit(-1)

    #download_and_check_adventures()
    #adv = read_adventure_json("temp_adventures/adventure_268473.json")
    #paths = walk_through_ends(adv)
    """"
    Hmm, the old bird's nest,' she rasps, taking a long sip. 'Elevated patrols tonight. And cameras, new ones, on the lower levels. Best avoid the obvious paths.' Her eyes gleam with a strange light. You've gained crucial insight, but it cost you an hour and a precious few credits.
    """