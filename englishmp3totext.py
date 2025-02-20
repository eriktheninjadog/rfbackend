import boto3
import time
import subprocess
import requests
import json
import tempfile
import os   


def download_json_file(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'r') as file:
        content = json.load(file)

    return content


def transcribe_mp3_to_text(file_uri, job_name, region='ap-southeast-1'):
    transcribe = boto3.client('transcribe', region_name=region)
    
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
    
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Waiting for transcription to complete...")
        time.sleep(10)
    
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        transcript_file_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        
        return transcript_file_uri
    else:
        raise Exception("Transcription job failed")

# Example usage:]
# file_uri = 'https://path-to-your-mp3-file'
# job_name = 'your-transcription-job-name'
# print(transcribe_mp3_to_text(file_uri, job_name))


def scp_file_to_server(local_file_path, remote_file_path, remote_host='chinese.eriktamm.com'):
    scp_command = [
        'scp',
        local_file_path,
        f'{remote_host}:{remote_file_path}'
    ]
    
    try:
        subprocess.run(scp_command, check=True)
        print(f"File {local_file_path} successfully copied to {remote_host}:{remote_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error copying file: {e}")

# Example usage:
# local_file_path = '/path/to/your/local/file.mp3'
# remote_file_path = '/var/www/html/mp3/file.mp3'
# scp_file_to_server(local_file_path, remote_file_path)
def upload_file_to_s3(local_file_path, bucket_name, s3_file_path):
    s3 = boto3.client('s3', region_name='ap-southeast-1')
    
    # Check if the bucket exists
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except boto3.exceptions.botocore.client.ClientError:
        # If the bucket does not exist, create it
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
        )
        print(f"Bucket {bucket_name} created.")
    
    # Upload the file
    try:
        s3.upload_file(local_file_path, bucket_name, s3_file_path)
        print(f"File {local_file_path} successfully uploaded to {bucket_name}/{s3_file_path}")
        file_url = f"https://{bucket_name}.s3.ap-southeast-1.amazonaws.com/{s3_file_path}"
        return file_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

# Example usage:
# local_file_path = '/path/to/your/local/file.mp3'
# bucket_name = 'your-s3-bucket-name'
# s3_file_path = 'path/in/s3/file.mp3'
# print(upload_file_to_s3(local_file_path, bucket_name, s3_file_path))


import voa
import random

def download_upload_transcribe(video_id, job_name, remote_file_path, remote_host='chinese.eriktamm.com'):
    local_file_path = 'tmp.mp3'
    
    # Download the YouTube video as mp3
   # voa.download_youtube_audio_as_mp3("https://www.youtube.com/watch?v=" + video_id, local_file_path)
    
    # Upload the mp3 file to the server
    file_url = upload_file_to_s3("tmp.mp3",'moronic','tmp.mp3')
    #(local_file_path, '/var/www/html/mp3/tmp.mp3')
    
    # Construct the file URI for the uploaded mp3
    #file_uri = f'https://chinese.eriktamm.com/mp3/tmp.mp3'
    
    # Transcribe the mp3 file to text
    transcript_file_uri = transcribe_mp3_to_text(file_url, job_name)
    content = download_json_file(transcript_file_uri)
    return content['results']['transcripts'][0]['transcript']   


import openrouter
def translate_to_cantonese(text):
    api = openrouter.OpenRouterAPI()
    cantonese = api.open_router_deepseek_r1("Translate this text to spoken Cantonese. Make sure that it is colloquial. Do not return any jyuytping. Here is the text: " + text)
    return cantonese

# Example usage:
# video_id = 'your-youtube-video-id'
# job_name = 'your-transcription-job-name'
# remote_file_path = '/var/www/html/mp3/file.mp3'
# print(download_upload_transcribe(video_id, job_name, remote_file_path))
#                    voa.download_youtube_audio_as_mp3("https://www.youtube.com/watch?v="+video_id,"tmp.mp3")

import newscrawler
english = download_upload_transcribe('j3i53Z94ifs', 'test'+str(random.randint(0,10000)), '/var/www/html/mp3/test.mp3')
cantonese = translate_to_cantonese(english)
sml = newscrawler.make_sml_from_chinese_text([],cantonese)
newscrawler.make_and_upload_audio_from_sml(cantonese,sml[1],"ey2ca")