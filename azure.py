import requests
import time



def get_token(subscription_key, region):
    token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(token_url, headers=headers)
    return response.text

def transcribe_audio(audio_file_path, token, region):
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    # Parameters for Cantonese
    params = {
        'language': 'zh-HK'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'audio/wav'  # Adjust based on your audio format
    }
    
    with open(audio_file_path, 'rb') as audio_file:
        response = requests.post(url, headers=headers, params=params, data=audio_file)
    
    return response.json()

# Usage
subscription_key = "CSJWILfHgPWX0jEspPs9n2kjBr0PEYW3zsHuCuz9qzm7tOf7z2WoJQQJ99BBAC3pKaRXJ3w3AAAYACOG3BqO"
region = "eastasia"  # e.g., "eastus"
audio_file_path = "/home/erik/Downloads/news.wav"

# Get token
token = get_token(subscription_key, region)

# Transcribe
result = transcribe_audio(audio_file_path, token, region)
print(result)
