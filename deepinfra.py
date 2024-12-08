#deepinfra.py
from openai import OpenAI
import os


def transcribe_audio(file_path):    
    client = OpenAI(
        api_key= os.getenv("DEEPINFRAKEY") 
        base_url="https://api.deepinfra.com/v1/openai",
    )

    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
    model="openai/whisper-large-v3",
        file=audio_file,
        response_format="verbose_json",
        language="yue",
        timestamp_granularities="segment"
    )
    print(str(transcript))
