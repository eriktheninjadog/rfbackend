#sentenceexplainer.py
import openrouter

import textprocessing
import json
import boto3
import newscrawler
import time
import subprocess
from pydub import AudioSegment
import os
import ssml


def create_and_upload_files(normal_text,chunk: str, index: int) -> None:
    """Create MP3 and hint files, then upload them."""
    splits = textprocessing.split_text(normal_text)
    filename = f"spokenarticle_sentences{time.time()}_{index}.mp3"
    hint_filename = f"{filename}.hint.json"
    ssml.synthesize_ssml_to_mp3(chunk,filename)
    with open(hint_filename, "w") as f:
        json.dump(splits, f)

    for file in [filename, hint_filename]:
        scp_command = f"scp {file} chinese.eriktamm.com:/var/www/html/mp3"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error uploading {file}: {result.stderr}")


def explain_sentence(sentence):
    result = sentence + '\n\n'
    result += " spoken cantonese\n\n"
    
    spoken_cantonese = openrouter.open_router_chatgpt_4o_mini("You are a cantonese expert. All responses should be in Traditional Chinese only","rewrite this sentence to spoken cantonese using traditional chinese : " + sentence)
    child_spoken_cantonese = openrouter.open_router_chatgpt_4o_mini("You are a cantonese expert. All responses should be in Traditional Chinese only","rewrite this sentence to how a child would say it in Cantonese using traditional chinese : " + sentence)    
    written_picked_words = openrouter.open_router_chatgpt_4o_mini("You are a cantonese expert. All responses should be in Traditional Chinese only","pick out the difficult words from this sentence and explain these using spoken cantonese that a child would understand. Do not include pronounciation. :" + sentence)
    spoken_picked_words = openrouter.open_router_chatgpt_4o_mini("You are a cantonese expert. All responses should be in Traditional Chinese only","pick out the difficult words from this sentence and explain these using spoken cantonese that a child would understand. Do not include pronounciation. :" + spoken_cantonese)

    ret = []
    
    ret.append(spoken_cantonese)
    ret.append(child_spoken_cantonese)
    ret.append(written_picked_words)
    ret.append(spoken_picked_words)
    return ret
 



def shorten_sentences(text):
    sentences = openrouter.do_open_opus_questions("Rewrite this using shorter sentences and return a list of these new sentences in json format: [setntence1,sentence2,...]. Only return the json without any text around it. :\n" +text)
    return json.loads(sentences)

def cantonese_sentences(text):
    sentences = openrouter.do_open_opus_questions("Rewrite this using spoken Cantonese return a list of these new sentences in json format: [setntence1,sentence2,...]. Only return the json without any text around it. :\n" +text)
    return json.loads(sentences)
    
    
def explain_sentences(sentences):
    cleantext = ""
    total = ""
    
    short = shorten_sentences(sentences)        
    for s in short:
        cleantext+= s + '。\n'
        total += s + '。\n'
        total += "<break time=\"0.5s\"/>\n"
    total += '\n\n'
    total += " <break time=\"0.5s\"/>\n"

    for s in short:
        ss = explain_sentence(s)
        cleantext+=ss[0]+'\n'
        cleantext+=ss[1]+'\n'
        cleantext+=ss[2]+'\n'
        cleantext+=ss[3]+'\n'
        total+=ss[0]+'\n'
        total += " <break time=\"0.5s\"/>\n"        
        total+=ss[1]+'\n'
        total += " <break time=\"0.5s\"/>\n"
        total+=ss[2]+'\n'
        total += " <break time=\"0.5s\"/>\n"
        total+=ss[3]+'\n'
        total += " <break time=\"0.5s\"/>\n"
    total += "<break time=\"1.5s\"/>\n"
    
    f = open('tst.txt','w',encoding='utf-8')
    f.write(total)
    f.close()
    
    #f = open('tst.txt','r',encoding='utf-8')
    #total = f.read()
    #f.close()
    
    create_and_upload_files(cleantext,total,0)
    
    
