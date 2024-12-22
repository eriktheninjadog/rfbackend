import boto3
from pydub import AudioSegment
from io import BytesIO
import subprocess

def synthesize_speech(text, voice_id, language_code):
    """
    Synthesize speech using AWS Polly.
    
    Parameters:
    - text: The text to convert into speech.
    - voice_id: The Polly voice ID for the desired voice.
    - language_code: The language code for the Polly voice.
    
    Returns:
    - audio_segment: A Pydub AudioSegment of the synthesized speech.
    """
    polly = boto3.client('polly', region_name='us-east-1')
                
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='neural'  
        )
        
        # Load the response stream into an AudioSegment
        audio_stream = BytesIO(response['AudioStream'].read())
        audio_segment = AudioSegment.from_mp3(audio_stream)
        
        return audio_segment
    except Exception as e:
        print(f"Error synthesizing speech for text \"{text}\": {e}")
        return AudioSegment.silent(duration=0)  # Return silence in case of error

def generate_audio_from_tuples(sentences, output_filename):
    """
    Generate an audio file from a list of English and Cantonese sentence tuples.
    
    Parameters:
    - sentences: List of tuples [(english, cantonese),...].
    - output_filename: The name of the output mp3 file.
    """
    # Silence for 4 seconds
    silence = AudioSegment.silent(duration=2000)
    
    # Initialize final combined audio
    combined_audio = AudioSegment.empty()
    
    # Voice IDs
    english_voice_id = 'Danielle'  # You can choose another English voice
    cantonese_voice_id = 'Hiujin'  # Adjust to the correct Cantonese voice if available
    
    for english, cantonese in sentences:
        # Synthesize English speech
        english_audio = synthesize_speech(english, english_voice_id, 'en-US')
        
        # Synthesize Cantonese speech
        cantonese_audio = synthesize_speech(cantonese, cantonese_voice_id, 'cmn-CN') # Use correct language code
        
        # Concatenate: English, silence, and Cantonese
        combined_audio += english_audio + silence + cantonese_audio + silence + cantonese_audio +  silence + cantonese_audio + silence
    
    # Export the final audio to an mp3 file
    combined_audio.export(output_filename, format="mp3")
    print(f"Audio file saved as: {output_filename}")
    scp_command = f"scp {output_filename}* chinese.eriktamm.com:/var/www/html/mp3"
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error uploading {output_filename}: {result.stderr}")

import remotechineseclient

# Example Usage
if __name__ == "__main__":
    sentences = remotechineseclient.access_remote_client("getfailedreadingtests",{"days":48})
    generate_audio_from_tuples(sentences, "spokenarticle_news_failed.mp3")
