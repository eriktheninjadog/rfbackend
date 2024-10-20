#storycreator.py
# This is a module that creates a story out of the most diffult words that we failed in todays test and makes a mp3 from it


import requests
import random
import openrouter
import boto3
import textprocessing
import time
import json
import subprocess

payload = {
    "onlyFailed": True,
    "number": 40,
    "level": "A1",
    "language": "hi",
    "store": False,
    "all":True
}


def cantonese_text_to_mp3(text: str, output_file: str) -> None:
    """Convert a string of text to an MP3 file using AWS Polly."""
    session = boto3.Session(region_name='us-east-1')
    polly_client = session.client('polly')

    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Hiujin',
            Engine='neural'
        )

        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"MP3 file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred while creating MP3: {e}")




def make_stories():
    url = "https://chinese.eriktamm.com/api/poeexamples"
    # Send the JSON request
    totalstr = ''
    response = requests.post(url, json=payload)
    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        response_data = response.json()
        # Process the response data as needed
        print(response_data)
        result = response_data['result']
        hinttext = ''
        hints=[]
        text = ''
        totalseconds = 0
        random.shuffle(result)
        timesignatures = []
        for i in result:
            #english = i['english']
            tok = i['chinese']
            txt = ''
            for t in tok:
                txt = txt + str(t)
            chinese = txt
            if chinese not in hints:
                hints.append(chinese)
                text = text + txt
        # great now we hve the text

        story = openrouter.do_open_opus_questions("Pick out the 20 most difficult words in this text and create a 500 word story in spoken Cantonese suitable for a 6 year old child that contains most of them. Start with the words and a explanation of the meaning suitable for a 6 year old in Cantonese but do not include pronounciation. Here is the text\n" + text)         
        splits = textprocessing.split_text(story)
        filename = f"spokenarticle_story{time.time()}_{0}.mp3"

        cantonese_text_to_mp3(story,filename)
        hint_filename = filename + ".hint.json"
        with open(hint_filename, "w") as f:
            json.dump(splits, f)
        scp_command = f"scp "+ filename +"* chinese.eriktamm.com:/var/www/html/mp3"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)        
        return story

        """ 
            
            makemp3(english,chinese)
            chifilepath = mp3cache + '/' + createmp3name(chinese,False)
            engfilepath = mp3cache + '/' + createmp3name(english,False)
            engduration = get_mp3_duration(engfilepath)
            duration = get_mp3_duration(chifilepath) + engduration
            timesignatures.append([tok,english,totalseconds,duration,engduration])
            totalseconds += duration
            #totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
            #totalstr = totalstr + 'file ' + "'" +engfilepath + "'" + '\n'
            totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
            totalstr = totalstr + 'file ' + "'" + engfilepath + "'" + '\n' 
        f = open(mp3cache + '/' + 'inputfiles.txt','w',encoding='utf-8')
        f.write(totalstr)
        f.close()
        chosennumber = str(random.randint(0,100000))
        filebasepath = mp3cache + '/'   + 'total' + chosennumber 
        totalstr = 'ffmpeg -f concat -safe 0 -i /home/erik/mp3cache/inputfiles.txt -c copy ' + filebasepath + '.mp3'
        
        f = open(filebasepath + '.mp3.hint.json','w',encoding='utf-8')
        f.write(json.dumps(hinttext))
        f.close()
        
        f = open(filebasepath + '.mp3.times.json','w',encoding='utf-8')
        f.write(json.dumps(timesignatures))
        f.close()
        
        print(totalstr)
        subprocess.run(totalstr,shell=True,capture_output=True,text=True)
        scpcommand = "scp " + filebasepath + "* chinese.eriktamm.com:/var/www/html/mp3"   
        subprocess.run(scpcommand,shell=True,capture_output=True,text=True)

        return True
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)
        return False
        """
        
for i in range(10):
    make_stories()