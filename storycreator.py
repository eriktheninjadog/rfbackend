#storycreator.py
# This is a module that creates a story out of the most diffult words that we failed in todays test and makes a mp3 from it


import requests
import random
import openrouter
import boto3
import textprocessing
import time
import json
import subprocess

payload = {
    "onlyFailed": True,
    "number": 40,
    "level": "A1",
    "language": "hi",
    "store": False,
    "all":True
}


def cantonese_text_to_mp3(text: str, output_file: str) -> None:
    """Convert a string of text to an MP3 file using AWS Polly."""
    session = boto3.Session(region_name='us-east-1')
    polly_client = session.client('polly')

    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Hiujin',
            Engine='neural',
            TextType='ssml'            
        )

        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"MP3 file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred while creating MP3: {e}")


def make_stories():
    url = "https://chinese.eriktamm.com/api/poeexamples"
    # Send the JSON request
    totalstr = ''
    response = requests.post(url, json=payload)
    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        response_data = response.json()
        # Process the response data as needed
        print(response_data)
        result = response_data['result']
        hinttext = ''
        hints=[]
        text = ''
        totalseconds = 0
        random.shuffle(result)
        timesignatures = []
        for i in result:
            #english = i['english']
            tok = i['chinese']
            txt = ''
            for t in tok:
                txt = txt + str(t)
            chinese = txt
            if chinese not in hints:
                hints.append(chinese)
                text = text + txt
        # great now we hve the text

        story = openrouter.do_open_opus_questions("Pick out the 20 most difficult words in this text and create a 500 word story in spoken Cantonese suitable for a 6 year old child that contains most of them. Start with the words and a explanation of the meaning suitable for a 7 year old in Cantonese but do not include pronounciation. Here is the text\n" + text)         
        splits = textprocessing.split_text(story)
        filename = f"spokenarticle_story{time.time()}_{0}.mp3"

        cantonese_text_to_mp3(story,filename)
        hint_filename = filename + ".hint.json"
        with open(hint_filename, "w") as f:
            json.dump(splits, f)
        scp_command = f"scp "+ filename +"* chinese.eriktamm.com:/var/www/html/mp3"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)        
        return story
    
    
    
import re

def strip_ssml_tags(ssml_string):
    """
    Strips SSML tags from a given string.
    
    Args:
        ssml_string (str): The input string containing SSML tags.
        
    Returns:
        str: The input string with SSML tags removed.
    """
    # Regular expression pattern to match SSML tags
    ssml_tag_pattern = r'<[^>]+>'
    
    # Substitute the SSML tags with an empty string
    stripped_string = re.sub(ssml_tag_pattern, '', ssml_string)
    
    # Optionally, strip leading/trailing whitespace and reduce multiple spaces
    stripped_string = ' '.join(stripped_string.split())
    
    return stripped_string


def make_wordlists():
    url = "https://chinese.eriktamm.com/api/poeexamples"
    # Send the JSON request
    totalstr = ''
    response = requests.post(url, json=payload)
    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        response_data = response.json()
        # Process the response data as needed
        print(response_data)
        result = response_data['result']
        hinttext = ''
        hints=[]
        text = ''
        totalseconds = 0
        random.shuffle(result)
        timesignatures = []
        for i in result:
            #english = i['english']
            tok = i['chinese']
            txt = ''
            for t in tok:
                txt = txt + str(t)
            chinese = txt
            if chinese not in hints:
                hints.append(chinese)
                text = text + txt
        # great now we hve the text

        story = openrouter.do_open_opus_questions("Pick out the 20 most difficult words into a list. Return a json-array (and no other text but json) looking like this [[word 1,explanation of word 1 in Cantonese suitable for a 7 year old, first example sentence containing word 1, second example sentence containing word 1],...]    ]  For each word in the list:  Here is the text\n" + text)
        print(story)
        thestuff = json.loads(story)
        filename = f"spokenarticle_list{time.time()}_{0}.mp3"
        thetotalssml = "<speak>"
        for word in thestuff:   
            for i in range(2):
                thetotalssml += word[0] + "<break time=\"0.2s\"/>"
                thetotalssml += word[1] + "<break time=\"0.5s\"/>"
            thetotalssml += word[2] + "<break time=\"0.5s\"/>"
            thetotalssml += word[2] + "<break time=\"0.5s\"/>"
            thetotalssml += word[3] + "<break time=\"0.5s\"/>"
            thetotalssml += word[3] + "<break time=\"0.5s\"/>"
        
        random.shuffle(thestuff)
        for word in thestuff:   
            thetotalssml += word[2] + "<break time=\"0.5s\"/>"
            thetotalssml += word[3] + "<break time=\"0.5s\"/>"

        thetotalssml += "</speak>"
        splits = textprocessing.split_text(strip_ssml_tags(thetotalssml))
        cantonese_text_to_mp3(thetotalssml,filename)
        hint_filename = filename + ".hint.json"
        with open(hint_filename, "w") as f:
            json.dump(splits, f)
        scp_command = f"scp "+ filename +"* chinese.eriktamm.com:/var/www/html/mp3"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)        
        return story
    
    
def make_wordlists_from_list(alist):
    url = "https://chinese.eriktamm.com/api/poeexamples"
    # Send the JSON request
    totalstr = ''
    random.shuffle(alist)
    words = ''
    for i in range(20):
        words = words + alist[i] + '\n'

    story = openrouter.do_open_opus_questions("A list of Cantonese terms and words is provided. Return a json-array (and no other text but json) looking like this [[word 1,explanation of word 1 in Cantonese suitable for a 7 year old, first example sentence containing word 1, second example sentence containing word 1],...]    ]  For each word in the list:  Here is the list\n\n" + words)
    print(story)
    thestuff = json.loads(story)
    filename = f"spokenarticle_list{time.time()}_{0}.mp3"
    thetotalssml = "<speak>"
    for word in thestuff:   
        for i in range(2):
            thetotalssml += word[0] + "<break time=\"0.2s\"/>"
            thetotalssml += word[1] + "<break time=\"0.5s\"/>"
        thetotalssml += word[2] + "<break time=\"0.5s\"/>"
        thetotalssml += word[2] + "<break time=\"0.5s\"/>"
        thetotalssml += word[3] + "<break time=\"0.5s\"/>"
        thetotalssml += word[3] + "<break time=\"0.5s\"/>"
    
    random.shuffle(thestuff)
    for word in thestuff:   
        thetotalssml += word[2] + "<break time=\"0.5s\"/>"
        thetotalssml += word[3] + "<break time=\"0.5s\"/>"

    thetotalssml += "</speak>"
    splits = textprocessing.split_text(strip_ssml_tags(thetotalssml))
    cantonese_text_to_mp3(thetotalssml,filename)
    hint_filename = filename + ".hint.json"
    with open(hint_filename, "w") as f:
        json.dump(splits, f)
    scp_command = f"scp "+ filename +"* chinese.eriktamm.com:/var/www/html/mp3"
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)        
    return story
    
f = open('/home/erik/Downloads/2500tradhsk.txt','r',encoding='utf-8')
lines = f.readlines()
f.close()
for i in range(10):
    make_wordlists_from_list(lines)
    
#for i in range(10):
#    make_wordlists()