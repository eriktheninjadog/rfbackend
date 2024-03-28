#
# we are making mp3s here
#

import requests
import json

import os
import sys
import subprocess
mp3cache = '/home/erik/mp3cache'

def createmp3name(word):
    ret = word.replace(' ','_') + ".mp3"
    ret = ret.replace('\n','')
    ret = ret.replace("'","")
    ret = ret.replace("?","")    
    return ret

def makeamazonmp3(text,voice,engine):
    text = text.replace('\n','')
    filepath = mp3cache + '/' + createmp3name(text)
    if os.path.exists(filepath):
        return
    text = "<speak><break time=\\\"1s\\\"/>" +text + "<break time=\\\"1s\\\"/></speak>"
    output = 'aws polly synthesize-speech --output-format mp3 --voice-id "' + voice + '" --engine ' +engine+' --text-type ssml --text "' + text + '" ' + filepath + ' > out'
    print(output)
    subprocess.run(output,shell=True,capture_output=True,text=True)
    #print(output)

def makemp3(english,chinese):
    print("makemp3 " + english + "  " + chinese)
    makeamazonmp3(english,"Danielle","neural")
    makeamazonmp3(chinese,"Hiujin","neural",)
    

payload = {
    "onlyFailed": True,
    "number": 10,
    "level": "A1",
    "language": "hi",
    "store": False
}


import random

def sendRequest():
    
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
        for i in result:
            english = i['english']
            tok = i['chinese']
            txt = ''
            for t in tok:
                txt = txt + str(t)
            chinese = txt
            makemp3(english,chinese)
            chifilepath = mp3cache + '/' + createmp3name(chinese)   
            engfilepath = mp3cache + '/' + createmp3name(english) 
            totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
            totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
            #totalstr = totalstr + 'file ' + "'" +mp3cache + "/silence.mp3'"+ '\n'
            totalstr = totalstr + 'file ' + "'" +engfilepath + "'"+ '\n'
            #totalstr = totalstr + 'file ' + "'" +mp3cache + "/silence.mp3'"+ '\n'
        f = open(mp3cache + '/' + 'inputfiles.txt','w',encoding='utf-8')
        f.write(totalstr)
        f.close()
        totalstr = 'ffmpeg -f concat -safe 0 -i /home/erik/mp3cache/inputfiles.txt -c copy ' + mp3cache + '/'   + 'total' + str(random.randint(0,100000)) + '.mp3'
        print(totalstr)
        subprocess.run(totalstr,shell=True,capture_output=True,text=True)

        
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)


#makemp3("hi there","我沖涼")
for i in range(30):
    sendRequest()