#
# we are making mp3s here
#

import requests
import json

import os
import sys
import subprocess
mp3cache = '/home/erik/mp3cache'

def createmp3name(word,slow):
    if slow == False:
        ret = word.replace(' ','_') + ".mp3"
    else:
        ret = word.replace(' ','_') + "slow.mp3"        
    ret = ret.replace('\n','')
    ret = ret.replace("'","")
    ret = ret.replace("?","")    
    return ret



def makeamazonmp3(text,voice,engine,slow):
    text = text.replace('\n','')
    filepath = mp3cache + '/' + createmp3name(text,slow)
    if os.path.exists(filepath):
        return
    if slow == False:
        text = "<speak><break time=\\\"1s\\\"/>" +text + "<break time=\\\"1s\\\"/></speak>"
    else:
        text = "<speak><break time=\\\"1s\\\"/><prosody rate=\\\"50%\\\">" +text + "</prosody><break time=\\\"1s\\\"/></speak>"  
    output = 'aws polly synthesize-speech --output-format mp3 --voice-id "' + voice + '" --engine ' +engine+' --text-type ssml --text "' + text + '" ' + filepath + ' > out'
    print(output)
    subprocess.run(output,shell=True,capture_output=True,text=True)
    #print(output)



def makeamazon_gap_mp3(list_of_tokens,voice,engine):
    
    filepath = mp3cache + '/gap_' + createmp3name("gaptokens_"+str(random.randint(0,10000)))
    
    if os.path.exists(filepath):
        return
    text = "<speak>"
    
    for tokens in list_of_tokens:
        if len(tokens) > 5:
            random_removed = random.randint(0,len(tokens)-1)
            
            # lets create the removed audio
            brokensentence = "<break time=\\\"1s\\\"/>"
            
            for i in range(random_removed):
                brokensentence = brokensentence + tokens[i]
            brokensentence = brokensentence + "<break time=\\\"1s\\\"/>"
            
            for i in range(random_removed+1,len(tokens)):
                brokensentence = brokensentence + tokens[i]    
            brokensentence = brokensentence + "<break time=\\\"1s\\\"/>"
            text = text + brokensentence + brokensentence
            text = text + "<break time=\\\"1s\\\"/>"
            text = text + tokens[random_removed]
            text = text + "<break time=\\\"1s\\\"/>"
            text = text + tokens[random_removed]
            clearsentence = ''
            for i in tokens:
                clearsentence = clearsentence + i
            text = text + "<break time=\\\"1s\\\"/>"
            text = text + clearsentence
    text = text + "</speak>"
    
    output = 'aws polly synthesize-speech --output-format mp3 --voice-id "' + voice + '" --engine ' +engine+' --text-type ssml --text "' + text + '" ' + filepath + ' > out'
    print(output)
    subprocess.run(output,shell=True,capture_output=True,text=True)
    #print(output)

def make_gap_file():
    url = "https://chinese.eriktamm.com/api/poeexamples"
    # Send the JSON request
    totalstr = ''
    response = requests.post(url, json=payload)
    # Check the response status code
    if response.status_code == 200:
        response_data = response.json()
        # Process the response data as needed
        print(response_data)    
        allofthem = []
        result = response_data['result']
        for i in result:
            tok = i['chinese']
            allofthem.append(tok)
        makeamazon_gap_mp3(allofthem,"Hiujin","neural")


def makemp3(english,chinese):
    print("makemp3 " + english + "  " + chinese)
    makeamazonmp3(english,"Danielle","neural",False)
    makeamazonmp3(chinese,"Hiujin","neural",False)
    makeamazonmp3(chinese,"Hiujin","neural",True)
    

payload = {
    "onlyFailed": True,
    "number": 20,
    "level": "A1",
    "language": "hi",
    "store": False,
    "all":True
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
        hinttext = ''
        for i in result:
            english = i['english']
            tok = i['chinese']
            txt = ''
            for t in tok:
                txt = txt + str(t)
            chinese = txt
            hinttext =  hinttext + chinese + "\n"
            makemp3(english,chinese)
            chifilepath = mp3cache + '/' + createmp3name(chinese,False)
            engfilepath = mp3cache + '/' + createmp3name(english,False) 
            totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
            totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
        f = open(mp3cache + '/' + 'inputfiles.txt','w',encoding='utf-8')
        f.write(totalstr)
        f.close()
        chosennumber = str(random.randint(0,100000))
        totalstr = 'ffmpeg -f concat -safe 0 -i /home/erik/mp3cache/inputfiles.txt -c copy ' + mp3cache + '/'   + 'total' + chosennumber + '.mp3'
        f = open(mp3cache + '/'   + 'total' + chosennumber + '.mp3.hint','w',encoding='utf-8')
        f.write(hinttext)
        f.close()
        print(totalstr)
        subprocess.run(totalstr,shell=True,capture_output=True,text=True)        
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)



def textOnlySendRequest():
    url = "https://chinese.eriktamm.com/api/poeexamples"
    # Send the JSON request
    totalstr = ''
    response = requests.post(url, json=payload)
    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        response_data = response.json()
        # Process the response data as needed
        result = response_data['result']
        for i in result:
            english = i['english']
            tok = i['chinese']
            txt = ''
            for t in tok:
                txt = txt + str(t)
            chinese = txt
            print(chinese+"...")
            print(chinese+"...")

def reverseSendRequest():
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
            chifilepath = mp3cache + '/' + createmp3name(chinese,False)
            chislowfilepath = mp3cache + '/' + createmp3name(chinese,True)
            engfilepath = mp3cache + '/' + createmp3name(english,False) 
            totalstr = totalstr + 'file ' + "'" +engfilepath + "'" + '\n'            
            totalstr = totalstr + 'file ' + "'" +chislowfilepath + "'" + '\n'
            totalstr = totalstr + 'file ' + "'" +chifilepath + "'" + '\n'
        f = open(mp3cache + '/' + 'inputfiles.txt','w',encoding='utf-8')
        f.write(totalstr)
        f.close()
        totalstr = 'ffmpeg -f concat -safe 0 -i /home/erik/mp3cache/inputfiles.txt -c copy ' + mp3cache + '/'   + 'reverse_' + str(random.randint(0,100000)) + '.mp3'
        print(totalstr)
        subprocess.run(totalstr,shell=True,capture_output=True,text=True)        
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)


import openrouter
import wordlists
def create_dialogue():
    
    p1 = random.choice( wordlists.roles)
    p2 =random.choice(  wordlists.roles)
    topic = random.choice( wordlists.topics)
    
    url = "https://chinese.eriktamm.com/api/gooutrouter"
    payload ={
        "question":"Create a dialogue in spoken Cantonese between " + p1 + " and " +p2  + " discussing "+ topic +". Reply only with traditional chinese characters"
    }
    # Send the JSON request
    totalstr = ''
    response = requests.post(url, json=payload)
    response = response.json()
    response = response['result'] 
    text = "<speak>" + response + "</speak>"
    text = text.replace("\n","<break time=\\\"1s\\\"/>")
    chosennumber = str(random.randint(0,100000))
    filepath = mp3cache + '/' + 'story_'+chosennumber + '.mp3'
    print(filepath)
    output = 'aws polly synthesize-speech --output-format mp3 --voice-id "Hiujin" --engine neural --text-type ssml --text "' + text + '" ' + filepath + ' > out'
    print(output)
    subprocess.run(output,shell=True,capture_output=True,text=True)
    f = open(filepath+'.hint','w',encoding='utf-8')
    f.write(response)
    f.close()
    
    
    
def make_voice_article(text):
    # simplifify text
    url = "https://chinese.eriktamm.com/api/gooutrouter"
    payload ={
        "question":"Simplify this text to A1 level and make it more like spoken cantonese:"+text
        }
    response = requests.post(url, json=payload)
    response = response.json()
    response = response['result']
    print(response)
    text = "<speak>" + response + "</speak>"
    text = text.replace("\n","<break time=\\\"1s\\\"/>")
    chosennumber = str(random.randint(0,100000))
    filepath = mp3cache + '/' + 'spokenarticle_'+chosennumber + '.mp3'
    print(filepath)    
    output = 'aws polly synthesize-speech --output-format mp3 --voice-id "Hiujin" --engine neural --text-type ssml --text "' + text + '" ' + filepath + ' > out'
    print(output)
    subprocess.run(output,shell=True,capture_output=True,text=True)
    f = open(filepath+'.hint','w',encoding='utf-8')
    f.write(response)
    f.close()
    output = "scp " + filepath + "* chinese.eriktamm.com:/var/www/html/mp3"   
    subprocess.run(output,shell=True,capture_output=True,text=True)
    
    

#makemp3("hi there","我沖涼")
if __name__ == "__main__":
    #for i in range(50):
    #    create_dialogue()
    #for i in range(50):
    #    reverseSendRequest()    
    make_voice_article(
        """廣東省佛山市應急管理局表示，一艘船擦碰佛山九江大橋防撞墩後，在擔杆洲尾水域搶灘不成功沉沒，船上共有11名船員，其中7人獲救，4人失聯，當局正在搜救，事故原因正在調查中。

專家初步鑒定，九江大橋主體結構未見明顯受損，但橋樑防撞墩有擦痕，需對橋樑安全做進一步鑒定。

事發在昨晚，佛山、江門兩地公安及省、市海事部門派出300多人次搜救失聯人員。事發水域暫時封航。九江大橋來回方向今早6時至明早6時實施交通管制，海事部門亦實施通航管制，除應急搶險船艇外，其他船舶禁止駛入九江大橋上下游3公里水域，來往的船隻要注意繞道而行。"""
        
        
    )
    #for i in range(50):
    #     sendRequest()
         
    #for i in range(20):         
    #     textOnlySendRequest()
    