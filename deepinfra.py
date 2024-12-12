#deepinfra.py
from openai import OpenAI
import os
import json


def transcribe_audio(file_path):    
    apikey = os.getenv("DEEPINFRAKEY")
    client = OpenAI(
        api_key= apikey,
        base_url="https://api.deepinfra.com/v1/openai"
    )

    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
    model="openai/whisper-large-v3",
        file=audio_file,
        response_format="verbose_json",
        language="yue",
        timestamp_granularities="segment"
    )
    roar = []
    for s in transcript.segments:
        ret = {}
        ret['text'] = s.text
        ret['start_time'] = s.start
        ret['end_time'] = s.end
        roar.append(ret)
    print(str(roar))
    return roar




if __name__ == "__main__":
    transcribe_audio("/home/erik/Downloads/try.mp3")