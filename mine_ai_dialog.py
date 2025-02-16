#mine_ai_dialog.py

import openrouter

import remotechineseclient



def extract_text(data):
    if isinstance(data, dict):
        for value in data.values():
            yield from extract_text(value)
    elif isinstance(data, list):
        for item in data:
            yield from extract_text(item)
    elif isinstance(data, str):
        yield data

# Example usage:
# data = {"key1": "value1", "key2": ["value2", {"key3": "value3"}]}
# text_strings = list(extract_text(data))
# print(text_strings)

import ssml
import time
import subprocess
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
            TextType='ssml'            
        )

        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"MP3 file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred while creating MP3: {e}")

def extract_ssml_content(ssml_text: str) -> str:
    """Extract content including <speak> tags in an SSML string."""
    start_tag = "<speak>"
    end_tag = "</speak>"
    
    start_index = ssml_text.find(start_tag)
    end_index = ssml_text.find(end_tag)
    
    if start_index != -1 and end_index != -1:
        return ssml_text[start_index:end_index + len(end_tag)].strip()
    else:
        return ""

    # Example usage:
    # ssml_text = "<speak>This is a test.</speak> Some other text."
    # extracted_content = extract_ssml_content(ssml_text)
    # print(extracted_content)  # Output: "This is a test."


response = remotechineseclient.access_remote_client_get("llmentries/last_24_hours")
api = openrouter.OpenRouterAPI()
blop = extract_text(response)
result = ""
for b in blop:
    result += b
orgtext = result
print(str(blop))
for i in range(10):
    result = api.open_router_claude_3_5_sonnet("You are a language teaching expert, helping teachers to make their tutoring more efficient","From this lesson transcript, write notes what the student needs to practice on:" + orgtext)
    result = api.open_router_claude_3_5_sonnet("You are a Cantonese coach, All your Cantonese should be spoken correct Cantonese.","Make 40 sentences in Cantonese to a student based upon the notes from this teacher. Return format should be in SSML with each sentence repeated two times and a pause between each sentence. Return all sentences. Do not include jyutping or other pronounciation" + result)
    result = extract_ssml_content(result)

    filename = f"spokenarticle_news{time.time()}.mp3"
    cantonese_text_to_mp3(result, filename)
    scp_command = f"scp {filename}* chinese.eriktamm.com:/var/www/html/mp3"
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)


#result = api.open_router_nova_micro_v1("Extract and organise the chinese from this text mass: " + result)
#remotechineseclient.access_remote_client("make_c1_examples", {"pattern": "use vocabulary, syntax, expressions and grammatics from this text:" +result})
 