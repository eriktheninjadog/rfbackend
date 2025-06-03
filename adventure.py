#adventure.py



import openrouter
import json




def create_ground_adventure(scenario):
    api = openrouter.OpenRouterAPI()
    prompt ="""
                                                   
                                                   
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

Example Themes (optional):


Ancient ruins with cursed relics

A spaceship stranded on an alien planet

A haunted mansion with shifting rooms

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
    
    result = api.open_router_gemini_25_flash("You are a creative writer. Your task is to create a 'choose your own adventure' story in JSON format. Follow the provided structure and constraints carefully.",prompt)
    result = result.replace('json','')
    result = result.replace('```','')
    start = result.find('{')
    end = result.rfind('}')
    if start == -1 or end == -1:
        return 'Invalid JSON format returned from the API'
    result = result[start:end+1]
    # Parse the JSON to ensure it's valid
    json_data = json.loads(result)
    return json_data


import textprocessing
def translate_to_cantonese(text):
    api = openrouter.OpenRouterAPI()
    """Translate text to Cantonese using OpenRouter API."""
    text = api.open_router_nova_lite_v1(" Your task is to translate the following text to spoken Cantonese written in Traditional Characters. Only return the chinese, no jyutping or english text with explanations:" +text)
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

import json
import random
if __name__ == "__main__":
    # Example usage
    for i in range(10):
        print("Generating adventure", i+1)
        scenario = "A haunted mansion with shifting rooms"
        adventure = create_ground_adventure(scenario)
        print("Original Adventure:", adventure)
        
        translated_adventure = translate_story_to_chinese(adventure)
        tran = json.dumps(translated_adventure)
        filename = "adventure_"+str(random.randint(0,1000000)) +".json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(tran)
        print("Translated Adventure JSON saved as adventure.json")
        print("Translated Adventure:", translated_adventure)