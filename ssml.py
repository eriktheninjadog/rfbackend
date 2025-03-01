#ssml.py

import random
import re
import time
import json
import subprocess
from typing import List, Dict

from pydub import AudioSegment

import boto3
from newspaper import Article, build
import openrouter
import textprocessing
import ssml
import os
import xml.etree.ElementTree as ET

def is_valid_ssml(ssml_string):
    """
    Verify if a string is a well-formed SSML.

    Args:
        ssml_string (str): The SSML string to verify.

    Returns:
        bool: True if the SSML is valid, False otherwise.
    """
    try:
        # Parse the SSML string
        root = ET.fromstring(ssml_string)
        
        # Check if the root tag is <speak>, which is required for SSML
        return root.tag.lower() == 'speak'
    except ET.ParseError:
        # If there's a parse error, the SSML is not well-formed
        return False



def get_pause_as_ssml_tag():
    return "<break time='0.2s'/>"


def surround_text_with_short_pause(text):
    return get_pause_as_ssml_tag() + text + get_pause_as_ssml_tag()



def wrap_in_ssml(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        translated = openrouter.open_router_chatgpt_4o("You are an SSML assistant, responsible to format text to SSML",
            f"Convert this text into SSML format. Use pauses to make it more suitable for listening. Only return the SSML. Here is the text:\n{text}"
        )
        idx = translated.find('<speak>')
        translated = translated[idx:]        
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""
    
    
def synthesize_ssml_to_mp3(ssml_text, output_file='output.mp3', aws_access_key='YOUR_AWS_ACCESS_KEY', aws_secret_key='YOUR_AWS_SECRET_KEY', region='us-west-2'):
    # Initialize a session using AWS credentials
    session = boto3.Session(region_name='us-east-1')
    

    # Create a Polly client
    polly = session.client('polly')
    

    # Function to split SSML into manageable chunks
    def split_ssml(ssml, max_length=2000):
        ssml_chunks = []
        current_chunk = "<speak>"
        
        words = ssml.split('\n')  # Split the SSML into words
        for word in words:
            # Check if adding this word exceeds the limit
            if len(current_chunk) + len(word) + 1 > max_length:  # +1 for space
                current_chunk += "</speak>"  # Close current SSML chunk
                ssml_chunks.append(current_chunk)  # Add to chunks
                current_chunk = "<speak>" + word  # Start a new chunk
            else:
                current_chunk += " " + word  # Add word to current chunk
                
        # Add the last chunk if it exists
        if current_chunk.strip() != "<speak>":
            current_chunk += "</speak>"
            ssml_chunks.append(current_chunk)

        return ssml_chunks

    # Split the long SSML
    ssml_chunks = split_ssml(ssml_text)

    # List to hold the audio segments
    audio_segments = []

    # Synthesize each chunk
    for index, chunk in enumerate(ssml_chunks):
        if is_valid_ssml(chunk):
            response = polly.synthesize_speech(
                Text=chunk,
                Engine="neural",
                OutputFormat='mp3',
                VoiceId='Hiujin',  # Choose a voice
                TextType='ssml'  # Specify that the input is SSML
            )
            
            if 'AudioStream' in response:
                # Save the audio stream to a temporary file
                temp_file = f'temp_{index}.mp3'
                with open(temp_file, 'wb') as file:
                    file.write(response['AudioStream'].read())
                
                # Load the audio file into pydub
                audio_segments.append(AudioSegment.from_mp3(temp_file))

    # Combine all audio segments into one
    if audio_segments:
        combined = sum(audio_segments)
        combined.export(output_file, format='mp3')
        print(f"MP3 file created successfully: {output_file}")

        # Clean up temporary files
        for index in range(len(audio_segments)):
            os.remove(f'temp_{index}.mp3')
    else:
        print("Error: Could not synthesize speech.")
