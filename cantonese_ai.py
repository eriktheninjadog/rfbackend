#cantonese_ai.py
import requests


def audio_to_srt(audiofile):
    
    url = "https://paid-api.cantonese.ai"

    payload = {
        "api_key": "2",
        "with_timestmap": "true",
        "with_diarization": "true",
        "with_punctuation": "true",
        "with_word_timestamps": "true",
        "with_speaker_labels": "false",
        "with_speaker_timestamps": "true",
        "with_speaker_diarization": "false",
    }
    files=[
    ('data',('audio.wav',open(audiofile,'rb'),'audio/wav'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)
    print(response.json())
    return response.json()['text']


if __name__ == "__main__":
    audiofile = "audio.wav"  # Replace with your audio file path
    srt_output = audio_to_srt('holes_44.mp3')
    print(srt_output)
    