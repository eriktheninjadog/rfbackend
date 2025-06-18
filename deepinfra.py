#deepinfra.py
from openai import OpenAI
import os
import os.path
import json

#add caching to make it cheaper and faster when debugging!





def make_md5_from_file(file_path):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()




def call_deepinfra_gemini_flash_2_5(systemprompt, text):
    """
    Calls the DeepInfra Gemini Flash 2.5 model with the provided system prompt and text.
    Returns the response from the model.
    """
    apikey = os.getenv("DEEPINFRAKEY")
    client = OpenAI(
        api_key= apikey,
        base_url="https://api.deepinfra.com/v1/openai"
    )
    
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": systemprompt},
            {"role": "user", "content": text}
        ]
    )
    
    return response.choices[0].message.content

def transcribe_audio(file_path):
    transpath = make_md5_from_file(file_path)+".transcache"    
    if os.path.isfile(transpath):
        with open(transpath, "r") as f:
            return json.load(f)
        
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
    with open(transpath, "w") as f:
        f.write(json.dumps(roar))
    return roar




if __name__ == "__main__":
    transcribe_audio("/home/erik/Downloads/narco13.mp3")