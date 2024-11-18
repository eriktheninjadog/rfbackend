#importdisneysubs.py
import textprocessing
import requests
import json
import boto3


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
            #TextType='ssml'            
        )

        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"MP3 file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred while creating MP3: {e}")


def clean_subtextline(line):
    parts = line.split('\t')
    realparts = []
    for p in parts:
        if len(p.strip()) > 0:
            realparts.append( p.strip() )
    return [realparts[1],realparts[2]]


f = open('/home/erik/Downloads/import.txt')
all = f.readlines()
f.close()

b = all[1].split('\t')
kok = []
for p in all[1:]:
    o = clean_subtextline(p)
    english = o[1]
    chinese = textprocessing.split_text(o[0])
    kok.append({"chinese":chinese,"english":english})

url = 'https://chinese.eriktamm.com/api/add_examples_to_cache'

# Define the JSON payload for the request
payload = {
    "examples":kok
}

# Convert the payload to JSON format
json_payload = json.dumps(payload)

# Set the headers to indicate that the request is sending JSON data
headers = {'Content-Type': 'application/json'}

# Send the POST request with the JSON payload
response = requests.post(url, data=json_payload, headers=headers)
print(str(response))
