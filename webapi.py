import subprocess
import time
import re
import traceback
from flask import Flask, Response, jsonify, request, url_for

import api
import log
import constants
import database
import os
import os.path

import asyncio

import json

import boto3
import pycld2 as cld2

import zhconv

from textwrap import wrap

import random
import aisocketapi
import batchprocessing
import textprocessing
import requests
from bs4 import BeautifulSoup
import urllib.parse
import newscrawler


import cachemanagement

import MessageAnnouncer

import random


app = Flask(__name__)


@app.route('/version', methods=['GET','PUT'])
def version():
    return jsonify({'version':'0.1'})

@app.route('/addtext',methods=['POST'])
def addtext():
    print("add text called")
    log.log("/addtext called")
    data = request.json
    log.log("/addtext data gotten")
    title       = data.get(constants.PARAMETER_TEXT_TITLE)
    type        = constants.CWS_TYPE_IMPORT_TEXT
    body        = data.get(constants.PARAMETER_TEXT_BODY)
    parentcwsid = data.get(constants.PARAMETER_PARENT_CWSID)    
    source      = data.get(constants.PARAMETER_TEXT_SOURCE)
    log.log(" cld2.detect(body) called ")
    isReliable, textBytesFound, details = cld2.detect(body) 
    print(str(details))
    if details[0][1] == "en":
        os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
        print("Translate To chinese")
        translate = boto3.client(service_name='translate', region_name='ap-southeas\
t-1', use_ssl=True)
        finaltext = ""
        bits = wrap(body,9000)
        for bit in bits:
            english_text = bit.replace("\n","_")
            result = translate.translate_text(Text=english_text,
            SourceLanguageCode="en", TargetLanguageCode="zh-TW")
            finaltext = finaltext + result.get('TranslatedText').replace("_","\n")
        body = finaltext
        print("Translation " + body)        
    cws  = api.process_chinese(title, source, body, type,parentcwsid)
    log.log(" add text - text processed " )
    #api.create_and_store_all_fragments(cws[0])
    return jsonify({'result':cws})

@app.route('/lookupposition',methods=['POST'])
def lookupposition():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    position = data.get(constants.PARAMETER_POSITION)
    ret = api.lookup_position(cwsid,position)
    return jsonify({'result':ret})

@app.route('/unansweredquestions',methods=['POST'])
def unansweredquestions():
    ret = api.unanswered_questions()
    return jsonify({'result':ret})

@app.route('/getimportedtexts',methods=['POST'])
def getimportedtexts():
    ret = api.get_imported_texts()
    return jsonify({'result':ret})

@app.route('/getcws',methods=['POST'])
def getcws():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    ret = api.get_cws_text(cwsid)
    return jsonify({'result':ret})

@app.route('/answeraiquestion',methods=['POST'])
def answeraiquestion():
    data = request.json    
    aianswer = data.get(constants.PARAMETER_AI_ANSWER)
    questionid = data.get(constants.PARAMETER_QUESTION_ID)   
    print("aianswer:" + aianswer)
    print("questionid:" + str(questionid))
    api.answer_ai_question(questionid,aianswer)
    return jsonify({'result':'ok'})

@app.route('/generatequestions',methods=['POST'])
def generatequestions():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    api.create_ai_paragraphs_questions(cwsid,"Explain the meaning of this text",4,lambda x:len(x)>20)
    #api.create_ai_paragraphs_questions(cwsid,"Ask a few questions to make sure the reader understood this paragraph",8,lambda x:len(x)>30)
    api.create_ai_paragraphs_questions(cwsid,"Ask a few questions and answers (write answers in chinese) to make sure the reader understood this paragraph",8,lambda x:len(x)>30)
    api.create_ai_sentences_questions(cwsid,"Explain the grammar of this sentence",5,lambda x:len(x)>6)
    api.create_ai_parts_questions(cwsid,"Breakdown this text into its parts",7,lambda x:len(x)>4)
    return jsonify({'result':'success'})

@app.route('/dictionarylookup',methods=['POST'])
def dictionarylookup():
    data = request.json
    word = data.get(constants.PARAMETER_SEARCH_WORD)
    result = api.dictionary_lookup(word)
    return jsonify({'result':result})

@app.route('/reactorlookup',methods=['GET'])
def reactorlookup():
    term = request.args.get('q')
    result = api.dictionary_lookup(term)
    return str(result)

@app.route('/get_cws_vocabulary',methods=['POST'])
def get_cws_vocabulary():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    result = api.get_complete_vocab_from_cws(cwsid)    
    return jsonify({'result':result})

@app.route('/direct_ai_analyze',methods=['POST'])
def direct_ai_analyze():
    print('/direct_ai_analyze')
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)    
    ret = api.direct_ai_question(cwsid,"Analyze this text:",p1,p2,constants.CWS_TYPE_DIRECT_AI_ANALYZE)
    return jsonify({'result':ret})

@app.route('/direct_ai_analyze_grammar',methods=['POST'])
def direct_ai_analyze_grammar():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid,"Analyze the grammar of this text:",p1,p2,constants.CWS_TYPE_DIRECT_AI_ANALYZE_GRAMMAR)
    return jsonify({'result':ret})

@app.route('/direct_ai_summarize',methods=['POST'])
def direct_ai_summarize():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid,"Summarize this text using traditional chinese:",p1,p2,constants.CWS_TYPE_DIRECT_AI_SUMMARIZE)
    return jsonify({'result':ret})

@app.route('/direct_ai_simplify',methods=['POST'])
def direct_ai_simplify():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid,"Rewrite this text in traditional chinese using simple words and sentences:",p1,p2,constants.CWS_TYPE_DIRECT_AI_SIMPLIFY)
    return jsonify({'result':ret})

@app.route('/update_dictionary',methods=['POST'])
def update_dictionary():
    data = request.json
    term = data.get(constants.PARAMETER_TERM)
    jyutping = data.get(constants.PARAMETER_JYUTPING)
    definition = data.get(constants.PARAMETER_DEFINITION)
    database.update_dictionary(term,jyutping,definition)
    return jsonify({'result':'ok'})

@app.route('/get_random_ai_question',methods=['GET'])
def get_random_ai_question():
    ret = api.unanswered_questions()
    answer = random.choice(ret)    
    return str(answer.question)

@app.route('/post_random_ai_response',methods=['POST'])
def post_random_ai_response():
    question = request.form.get('question')
    airesponse = request.form.get('airesponse')
    log.log ("post_random_ai_response " + question)
    log.log ("post_random_ai_response got response " + airesponse) 
    completeresponsetext = question + "\n\n" + airesponse  
    responsecws = api.process_chinese("","",completeresponsetext,-1,-1)     
    log.log ("found responsecws for question " + str(responsecws))
    ret = api.unanswered_questions()
    for r in ret:
        if r.question == question:
            log.log("found a question" + str(r.id))
            database.answer_ai_response(r.id,responsecws.id)
    return "OK"

@app.route('/explain_paragraph',methods=['POST'])
def explain_paragraph():
    paragraph = request.json['text']
    cwsid     = request.json['cwsid']
    if (len(paragraph) < 5):
        return "OK"
    log.log("/explain_paragraph CWSID: " + str(cwsid))
    # we want to find the start and end of the text
    thecws = database.get_cws_by_id(cwsid)
    if thecws == None:
        log.log("Couldn't find CWS " + str(cwsid))        
        return "Couldn't find CWS " + str(cwsid)
    
    start = thecws.orgtext.find(paragraph)
    if start == -1:
        log.log("Couldn't find paragrap" + str(cwsid) + paragraph)                
        return "OK"
    database.add_ai_question("Explain the meaning, structure and grammar of this text:"+paragraph.strip(),66,cwsid,
                                start,
                                len(paragraph))
    database.add_ai_question("Write a few questions to check that the reader has understood this text:"+paragraph.strip(),constants.RESPONSE_TYPE_CHECK_QUESTION,cwsid,
                                start,
                                len(paragraph))
    return "OK"


@app.route("/translatechinese",methods=["POST"])
def translatechinese():
    os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
    print("Translate To English")
    translate = boto3.client(service_name='translate', region_name='ap-southeas\
t-1', use_ssl=True)
    finaltext = ""
    chinese_text = request.json['text']
    chinese_text = chinese_text.replace('\n','_')
    bits = wrap(chinese_text,9000)
    for bit in bits:
        english_text = bit
        result = translate.translate_text(Text=chinese_text,
            SourceLanguageCode="zh-TW", TargetLanguageCode="en")
        finaltext = finaltext + result.get('TranslatedText')
    return jsonify({'result':finaltext})

@app.route("/get_a_problem_text",methods=["POST"])
def get_a_problem_text():
    result = api.get_random_verify()
    return jsonify({'result':result})


@app.route('/post_random_pleco',methods=['POST'])
def post_random_pleco():
    question = request.form.get('pleco')
    database.update_pleco(question)
    return "OK"

@app.route('/generate_text',methods=['POST'])
def generate_text():
    text = request.json['text']
    api.create_generative_text(text)
    return "OK"

@app.route('/deletecws',methods=['POST'])
def deletecws():
    cwsid = request.json['cwsid']
    api.deletecwsbyid(cwsid)
    return "OK"

@app.route('/changecwsstatus',methods=['POST'])
def changecwsstatus():
    cwsid = request.json['cwsid']
    status = request.json['status']
    api.changecwsstatusbyid(cwsid,status)
    return "OK"



@app.route('/simplifycws',methods=['POST'])
def simplifycws():
    cwsid = request.json['cwsid']
    batchprocessing.simplify_cws(cwsid)
    return "OK"

@app.route('/direct_ai_question',methods=['POST'])
def direct_ai_question():
    cwsid       = request.json['cwsid']
    question    = request.json['question']    
    start       = request.json['start']
    end         = request.json['end']
    thecws = api.get_cws_text( cwsid )
    thetext = thecws.orgtext[start:end]
    thequestion = question + " : " + thetext
    answer = aisocketapi.ask_ai(thequestion)
    answer = zhconv.convert(answer,'zh-hk')
    cws = api.process_chinese("","ai",thetext+"\n------\n"+answer,500,cwsid)
    database.add_answered_ai_question(thequestion,500,cwsid,start,end,cws.id)
    return jsonify({'result':cws})


@app.route('/direct_ai_questions',methods=['POST'])
def direct_ai_questions():
    cwsid       = request.json['cwsid']
    questions    = request.json['questions']
    start       = request.json['start']
    end         = request.json['end']
    thecws = api.get_cws_text( cwsid )
    thetext = thecws.orgtext[start:end]
    simpcws = batchprocessing.multiple_ai_to_text(thetext,questions)
    return jsonify({'result':simpcws})


@app.route('/set_ai_auth',methods=['GET'])
def set_ai_auth():
    args = request.args
    auth_part = args.get('auth_part')
    with open('/var/www/html/api/rfbackend/auth_part.txt', 'w') as f:
        f.write(auth_part)
        print("written auth_part" + auth_part)
    return jsonify({'result':'ok'})

@app.route('/set_stored_value',methods=['POST'])
def set_stored_value():
    value       = request.json['value']
    storage     = request.json['storage']  
    key         = request.json['key']  
    api.write_value_to_dictionary_file(storage,key,value)
    return jsonify({'result':'ok'})

@app.route('/get_stored_value',methods=['POST'])
def get_stored_value():
    storage     = request.json['storage']  
    key         = request.json['key']
    value       = api.read_value_from_dictionary_file(storage,key)
    return jsonify({'result':value})


@app.route('/ai_simplify_cws',methods=['POST'])
def ai_simplify_cws():
    cwsid = request.json['cwsid']
    simpcws = batchprocessing.simplify_cws(cwsid)
    return jsonify({'result':simpcws})


@app.route('/apply_ai',methods=['POST'])
def apply_ai():
    cwsid = request.json['cwsid']
    aitext = request.json['aitext']
    simpcws = batchprocessing.apply_ai_to_cws(cwsid,aitext)
    return jsonify({'result':simpcws})

@app.route('/ai_summarize_random',methods=['POST'])
def ai_summarize_random():
    txt = aisocketapi.ask_ai("Generate an article of 500 words in traditional Chinese on a random topic. Follow it with  5 multiple choice questions to test the readers understanding.")
    cws  = api.process_chinese(random, "", txt, constants.CWS_TYPE_IMPORT_TEXT,-1)
    return jsonify({'result':cws})

@app.route('/get_word_list',methods=['POST'])
def get_word_list():
    cwsid = request.json['cwsid']
    cwsret = api.get_word_list_from_cws(cwsid)
    return jsonify({'result':cwsret})
   
@app.route('/add_look_up',methods=['POST'])
def add_look_up():
    cwsid = request.json['cwsid']
    term = request.json['term']
    database.add_look_up(term,cwsid)
    return jsonify({'result':'ok'})

@app.route('/get_look_up_history',methods=['POST'])
def get_look_up_history():
    cwsid = request.json['cwsid']
    lookups = database.lookup_history(cwsid)
    return jsonify({'result':lookups})

@app.route('/get_classification',methods=['POST'])
def get_classification():
    cwsid = request.json['cwsid']
    cws = api.get_cws_text( cwsid )    
    classdict = textprocessing.get_word_class(cws.orgtext)
    return jsonify({'result':classdict})

@app.route('/get_character_cws',methods=['POST'])
def get_character_cws():
    title = request.json['title']
    cws = database.get_cws_by_title_and_type(title,800)  
    return jsonify({'result':cws})

@app.route('/updatecws',methods=['POST'])
def updatecws():
    cwsid   = request.json['cwsid']
    text    = request.json['text']
    api.update_cws(cwsid,text)
    return jsonify({'result':'ok'})


@app.route('/getmemorystory',methods=['POST'])
def getmemorystory():
    try:
        character = request.json['character']
        print(str(character))
        page = requests.get("https://rtega.be/chmn/index.php?c=" + urllib.parse.quote_plus(character) +"&Submit=")
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all(id="chmn")
        print(results[1].text)
        return jsonify({'result':results[1].text})
    except Exception as e :
        print(str(e))
        return jsonify({'result':None})
#add something

@app.route('/publishfile',methods=['POST'])
def publishfile():
    try:
        content = request.json['content']
        filename = request.json['filename']
        f = open('/var/www/html/scene/'+filename,"w",encoding='utf-8')
        f.write(content)
        f.close()
        return jsonify({'result':'ok'})    
    except Exception as e :
        print(str(e))
        return jsonify({'result':None})

@app.route('/removefile',methods=['POST'])
def removefile():
    try:
        filename = request.json['filename']
        os.remove('/var/www/html/scene/'+filename)
        return jsonify({'result':'ok'})    
    except Exception as e :
        print(str(e))
        return jsonify({'result':None})
    
import poe
import poeclient

robot = "Claude-3-Opus"

@app.route('/poefree',methods=['POST'])
def poefree():
    cwsid       = request.json['cwsid']
    text        = request.json['text']
    bot         = request.json['bot']
    clear       = request.json['clear']
    global robot
    print("In poe free: robot = " + bot + " clear: " + str(clear))
    print("Robot is " + robot)    
    if bot != robot:
        print("We are switching to" + bot)
        poeclient.change_bot(bot)
        robot = bot
        time.sleep(12)
    result = poeclient.ask_ai(text,robot,clear)
    #result =  poe.ask_poe_ai_sync(text,bot,clear)
    #result = text + "\n\n" + result
    #result = aisocketapi.ask_ai(text,bot,clear)    
    result = text + "\n\n" + result
    
    cws = api.process_chinese("pf:"+text[:25],"ai",result,500,cwsid)
    return jsonify({'result':cws})



def extract_json(text):
    # Regular expression pattern to match JSON
    json_pattern = r'{.*}'    
    # Find all occurrences of the JSON pattern in the text
    json_matches = re.findall(json_pattern, text, re.DOTALL)    
    if json_matches:
        # Extract the first JSON match
        json_string = json_matches[0]        
        try:
            # Parse the JSON string
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError:
            print("Invalid JSON format.")
    else:
        print("No JSON found in the text.")    
    return None


def extract_json_array(text):
    import json
    try:
        # Find the opening bracket of the JSON array
        start_index = text.index('[')
        # Find the closing bracket of the JSON array
        end_index = text.rindex(']') + 1
        # Extract the JSON array substring
        json_array_str = text[start_index:end_index]
        # Parse the JSON array
        json_array = json.loads(json_array_str)
        return json_array
    except (ValueError, json.JSONDecodeError):
        return None

def read_examples_test_database():
    f = open('/var/www/html/scene/examplestest.txt',"r",encoding='utf-8')
    pop = f.read()
    f.close()
    database = json.loads(pop)
    return database

@app.route('/getexampleresult',methods=['POST'])
def getexampleresult():    
    return jsonify({'result':read_examples_test_database()})


def get_failed_examples(nr):
    database = read_examples_test_database()
    failed = []
    for i in database:
        if i['success'] == False:
            failed.append(i)
    uniq = {}
    for i in failed:
        # create a "key"
        akey = ''
        for t in i['tokens']:
            akey = akey + t
        akey = akey + i['english']
        uniq[akey] = i
    returnList = []
    for k in uniq.keys():
        returnList.append(uniq[k])
    if len(returnList)  > nr:
            returnList = random.sample(returnList,nr)
    # create the real list
    truelist = []
    for rl in returnList:
        truelist.append( {'chinese':rl['tokens'],'english':rl['english']} )
    return jsonify({'result':truelist})


def get_failed_examples_duplicates(nr,all):
    
    #testing
    if all == False:
#        if random.randint(0,1) == 1:        
#            result = database.get_failed_outputs(nr)
#        else:
        result = database.get_failed_outputs_lately(nr,random.randint(1,2))
    else:
        result = database.get_failed_outputs_lately(nr,random.randint(1,2))
    return jsonify({'result':result})
    """
    database = read_examples_test_database()
    failed = []
    for i in database:
        if i['success'] == False and i['english'].find('#') == -1:
            failed.append(i)
    # get all ENGLISH of failed
    print("total failed: " + str(len(failed)))    
    failedexamples = {}
    for i in failed:
        #filter out follow up questions, not valid
        if i['english'] not in failedexamples.keys():
            failedexamples[i['english']] = []            

    print("Unique failed english: " + str(len(failedexamples.keys())))    
    #now we will add the tokens
    for i in database:
        eng = i['english']
        if eng in failedexamples.keys():
            #this exist among the failed
            #even though this TOKEN itself might not be failed
            knowntokens = failedexamples[eng]
            known = False
            #look if we already added this token
            for k in knowntokens:
                #The token is among the already collected 
                #set flag
                if k == i['tokens']:
                    known = True
            if not known:
                knowntokens.append(i['tokens'])
                failedexamples['eng'] = knowntokens
    #know I have a dictionary with failed english phrases as key
    #and all known phrases in token format as value
    # lets move through the keys and create the content
    returnList = []
    for k in failedexamples.keys():
        item = failedexamples[k]
        itemlength = len(item)
        english_text = k + ' # ' + str(itemlength)
        chinese_tokens = []
        for i in item:
            for j in i:
                chinese_tokens.append(j)
            chinese_tokens.append('\n')
        returnList.append({'tokens':chinese_tokens,'english':english_text} )    
    if len(returnList)  > nr:
            returnList = random.sample(returnList,nr)
    truelist = []
    for rl in returnList:
        truelist.append( {'chinese':rl['tokens'],'english':rl['english']} )
    return jsonify({'result':truelist})"""


@app.route('/poeexampleresult',methods=['POST'])
def poeexampleresult():
    print(request.get_json())
    database = []
    try:
        f = open('/var/www/html/scene/examplestest.txt',"r",encoding='utf-8')
        pop = f.read()
        f.close()
        database = json.loads(pop)
    except:
        database = []
    chinese = request.json['chinese']
    tokens = request.json['tokens']
    english = request.json['english']
    level = request.json['level']
    success = request.json['success']
    reason = request.json['reason']
    currentTime = request.json['time']
    database.append({'tokens':tokens,'chinese':chinese,'english':english,'level':level,'success':success,'reason':reason,'time':currentTime})
    f = open('/var/www/html/scene/examplestest.txt',"w",encoding='utf-8')
    f.write( json.dumps(database))
    f.close()
    # hi
    return jsonify({'result':'ok'})


def pick_random_sentence_from_cache():
    repos = cachemanagement.read_cache_from_file()
    if len(repos) == 0:
        return None
    repo = random.choice(repos)
    sentence = random.choice(repo)
    return sentence

def pick_random_sentences_from_cache(nr):
    ret = []
    for i in range(nr):
        sentence = pick_random_sentence_from_cache()
        if sentence != None:
            ret.append(sentence)
    return ret
    

def get_examples_from_cache():
    cache = cachemanagement.read_cache_from_file()
    if len(cache) == 0:
        return None
    examples = cache.pop()
    cachemanagement.save_cache_to_file(cache)
    return examples
    
        
import wordlists
@app.route('/poeexamples',methods=['POST'])
def poeexamples():
    global robot
    level = request.json['level']
    number = request.json['number']
    language = request.json['language']
    onlyFailed = request.json['onlyFailed']
        
    if onlyFailed == True:
        if not 'all' in request.json:    
            return get_failed_examples_duplicates(number,False)
        else:
            return get_failed_examples_duplicates(number,True)

    if not 'store' in request.json:
        examples = get_examples_from_cache()
        if examples != None:
           return jsonify({'result':examples}) 

    text = create_poe_example_question(level,number)
    
    if 'question' in request.json:
        text = request.json['question']
    
    bot = "Claude-3-Opus"
    if bot != robot:
        print("In the web api we are switching to Claude")
        poeclient.change_bot(bot)
        robot = bot
        time.sleep(12)
    result = poeclient.ask_ai(text,robot,False)
    with open('/tmp/output.txt','w',encoding='utf-8') as f:
        f.write(result)
        f.flush()
    #aresult = extract_json(result)
    aresult = extract_json_array(result)
    #aresult = json.loads(result)
    result = newParsePoe(aresult)
    if 'store' in request.json:
        cachemanagement.add_examples_to_cache(result)
    return jsonify({'result':result})

def create_proper_cantonese_questions(level,number_of_sentences):
    sentences = pick_random_sentences_from_cache(number_of_sentences)
    print(str(sentences))
    ret = '\n'
    for s in sentences:
        for t in s['chinese']:
            ret = ret + t
        ret = ret + '\n'
    whole = "For each sentence in the list, rewrite it into plain spoken Cantonese.Return these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure. Here is the list: " + ret
    print("Here are the cantonese " + whole)
    return whole

def create_poe_example_question(level,number_of_sentences):
    #text = "Write " + str(number_of_sentences) + " example sentences in English at a " + level + " level of difficulty, along with their Cantonese translation, in a dictionary in JSON format without any other text."
    text = "Create "+ str(number_of_sentences) +" sentences at B2 level. Return these together with translation into common spoken Cantonese (use traditional characters and use Cantonese grammar) in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."
    #text = "Create "+ str(number_of_sentences) +" sentences at A1 level including some the following words: " + wordlists.get_sample_first_wordlist(30)+ ". Return these together with vernacular cantonese translation (use traditional charactters) in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."    
    return text

def is_list(obj):
    return isinstance(obj, list)

def newParsePoe(aresult):
    result = []
    for i in aresult:
        english = i['english']
        chinese = textprocessing.make_sure_traditional(i['chinese'])        
        tok = textprocessing.split_text(chinese)
        result.append( {"chinese":tok,"english":english} )
    return result
        

def parsePoe(aresult):
    if is_list(aresult):
        return newParsePoe(aresult)
    print(" aresult " + str(aresult))
    if 'sentences' in aresult.keys():
        itemarray = aresult['sentences']
    if ('sentence_1' in aresult.keys()):
        #we have something different here
        itemarray = []
        for i in aresult.keys():
            itemarray.append(aresult[i])
    if 'example_sentences' in aresult.keys():
        itemarray = aresult['example_sentences']
    result = []
    #changed
    for item in itemarray:
        print(" item " + str(item))
        chinese = None
        if 'cantonese' in item.keys():
            chinese = item['cantonese']
        if 'chinese' in item.keys():
            chinese = item['chinese']
        tok = textprocessing.split_text(chinese)
        result.append( {"chinese":tok,"english":item['english']} )
    return result


def remove_repeating_sentences(text):
    sentences = text.split('. ')  # Split text into sentences
    unique_sentences = []

    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)

    return '. '.join(unique_sentences)

@app.route('/cleanandtranslate',methods=['POST'])
def cleanandtranslate():
    global robot
    log.log("cleanandtranslate")
    text = request.json['text']
    #first lets clen this up
    poeclient.change_bot('Claude-instant-100k')
    time.sleep(10)
    bettertext = remove_repeating_sentences(text)
    bettertext =  bettertext.replace("\n"," ")
    bettertext =  bettertext.replace("\r"," ")
    log.log("Better text recieved" + bettertext)
    cleantext = poeclient.ask_ai('Clean up this text: ' + bettertext,robot,False)
    log.log("Clean text recieved" + cleantext)
    poeclient.change_bot('GPT-4')
    time.sleep(10)        
    chinesecleantext = poeclient.ask_ai('Translate this text to Traditional Chinese ' + cleantext,robot,False)
    log.log("Chinese Clean text recieved" + chinesecleantext)
    cws = api.process_chinese("messytranslate","ai",chinesecleantext,500,-1)
    return jsonify({'result':'ok'})
    
    
@app.route('/grammartest',methods=['POST'])
def grammartest():
    cwsid       = request.json['cwsid']
    start       = request.json['start']
    end         = request.json['end']
    thecws = api.get_cws_text( cwsid )
    thetext = thecws.orgtext[start:end]
    result = poe.ask_poe_ai_sync("Split this text into sentences and explain the grammar of each:" + thetext)
    cws = api.process_chinese("grammartest","ai",result,500,cwsid)
    return jsonify({'result':cws})

@app.route('/testvocabulary',methods=['POST'])
def testvocabulary():
    cwsid       = request.json['cwsid']
    start       = request.json['start']
    end         = request.json['end']
    thecws = api.get_cws_text( cwsid )
    thetext = thecws.orgtext[start:end]
    result = poe.ask_poe_ai_sync("Make a vocabulary test based upon this text:" + thetext)
    cws = api.process_chinese("testvocabulary","ai",result,500,cwsid)
    return jsonify({'result':cws})

@app.route('/testunderstanding',methods=['POST'])
def testunderstanding():
    cwsid       = request.json['cwsid']
    start       = request.json['start']
    end         = request.json['end']
    thecws = api.get_cws_text( cwsid )
    thetext = thecws.orgtext[start:end]
    result = poe.ask_poe_ai_sync("Make a list of question to check my understanding of this text:" + thetext)
    cws = api.process_chinese("testunderstanding","ai",result,500,cwsid)
    return jsonify({'result':cws})

@app.route('/news',methods=['POST'])
def news():
    thenews  = newscrawler.gethknews()
    cws = api.process_chinese("news","ai",thenews,500,-1)
    return jsonify({'result':cws})

@app.route('/dump', methods=['POST'])
def dump():
    # Print the request method (e.g., GET, POST)
    print(f"Request method: {request.method}")
    # Print the request headers
    print("Request headers:")
    for key, value in request.headers.items():
        print(f"{key}: {value}")
    # Print the request body
    print("Request body:")
    print(request.get_data(as_text=True))

    # Print the request arguments (for GET requests)
    print("Request arguments:")
    for key, value in request.args.items():
        print(f"{key}: {value}")

    return "Request processed"


@app.route('/poebot1',methods=['POST'])
def poebot1():
    try:
        version = request.json['version']
        type = request.json['type']
        print("version " + version)
        print("type " + type )
        if type == "report_error":
            print("ERROR")
            print(str(request.json))
        if type == "query":
            print("we got a query")
            print(str(request.json["query"]))
            query = request.json["query"]
            usermessage = ""
            if (len(query)>0):
                usermessage = query[-1]['content']
                print(usermessage)
            def generate_events():
                count = 0
                while count < 4:
                    if count == 0:
                        yield 'event: meta\ndata: {"content_type": "text/markdown", "linkify": true}\n\n'
                    if count == 1:
                        yield 'event: text\ndata: {"text": "I am here\\n\\n"}\n\n'
                        time.sleep(1)
                    if count == 2:
                        yield 'event: text\ndata: {"text": "I am here again!!!'+usermessage+'"}\n\n'
                    if count == 3:
                        yield 'event: done\ndata: {}\n\n'
                    count += 1
                    time.sleep(1)                
            return Response(generate_events(), mimetype='text/event-stream')
        return jsonify({'result':'ok'})    
    except Exception as e :
        traceback.print_exc() 
        print(str(e))
        return jsonify({'result':None})
    

from flask import send_file


def get_random_file(directory):
    # Get a list of all files in the directory
    file_list = os.listdir(directory)
    
    # Choose a random file from the list
    random_file = random.choice(file_list)
    
    # Return the path to the random file
    return os.path.join(directory, random_file)


def pick_random_file(directory, contains, extension):
    files = [file for file in os.listdir(directory) if file.endswith(extension) and file.find(contains)!=-1]
    if not files:
        return None  # No files with the specified extension found
    random_file = random.choice(files)
    return random_file


def pick_random_artice_file(directory, extension):
    files = [file for file in os.listdir(directory) if (file.endswith(extension) and file.startswith('spokenarticle_'))]
    if not files:
        return None  # No files with the specified extension found
    random_file = random.choice(files)
    return random_file

import shlex

def copymp3fromremote(file):
    script_path = "/usr/local/bin/copymp3fromremote.sh"
    
    # Get parameters from the query string
    
    # Ensure the script is executable
    #os.chmod(script_path, 0o755)
    
    # Construct the command with parameters
    command = script_path + " " + file
    
    # Run the script in the background with parameters
    print(command)
    subprocess.Popen([script_path,file], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL, 
                     shell=False)
    

@app.route('/audioexample', methods=['GET'])
def get_audio():
    # Path to the MP3 file
    mp3_file = get_random_file('/var/www/html/mp3')
    # Return the MP3 file
    return send_file(mp3_file, mimetype='audio/mpeg')


import makemp3

@app.route('/audioexample2', methods=['GET','POST'])
def get_audio2():
    # Path to the MP3 file
    mp3_file = pick_random_file('/var/www/html/mp3','total','mp3')
    # Return the MP3 file
    #return jsonify({'result':None})
    hint_file = mp3_file + '.hint.json'
    if os.path.exists('/var/www/html/mp3/'+hint_file):
        f = open('/var/www/html/mp3/'+hint_file,'r',encoding='utf-8')
        chitext = f.read()
        f.close()        
        chiret = json.loads(chitext)
        chiba = []
        for c in chiret:
            chiba.append(textprocessing.split_text(c))
        chiret = chiba
    else:
        chiret = ['no','chinese','to','\n','be','found','!',hint_file]
    
    time_file = mp3_file + '.times.json'
    if os.path.exists('/var/www/html/mp3/'+time_file):
        f = open('/var/www/html/mp3/'+time_file,'r',encoding='utf-8')
        timetext = f.read()
        f.close()
        timetext = json.loads(timetext)            
    else:
        timetext = None
    return jsonify({'result':{'filepath':mp3_file,'tokens':chiret,'times':timetext}})


@app.route('/audioexample3', methods=['GET','POST'])
def get_audio3():
    # Path to the MP3 file
    mp3_file = pick_random_artice_file('/var/www/html/mp3','mp3')
    # Return the MP3 file
    #return jsonify({'result':None})
    hint_file = mp3_file + '.hint.json'
    if os.path.exists('/var/www/html/mp3/'+hint_file):
        f = open('/var/www/html/mp3/'+hint_file,'r',encoding='utf-8')
        chitext = f.read()
        f.close()
        chiret = json.loads(chitext)
    else:
        chiret = ['no','chinese','to','\n','be','found','!']    
    return jsonify({'result':{'filepath':mp3_file,'tokens':chiret}})

@app.route('/remove_audio', methods=['POST'])
def remove_audio():
    # Path to the MP3 file
    mp3_file = request.json['audiofile']
    # Return the MP3 file
    #return jsonify({'result':None})
    basename = os.path.basename(mp3_file)
    os.unlink('/var/www/html/mp3/'+mp3_file)
    os.unlink('/opt/watchit/'+basename + ".webm")
    return jsonify({'result':'ok'})

def read_audio_time():
    try:
        f = open('/var/www/html/scene/audiotime.txt',"r",encoding='utf-8')
        js = f.read()
        f.close()
        jsonload = json.loads(js)
        thetime = jsonload['totaltime']
        return thetime
    except:
        return 0
    
def write_audio_time(totaltime):
    f = open('/var/www/html/scene/audiotime.txt',"w",encoding='utf-8')
    db = {'totaltime':totaltime}
    f.write(json.dumps(db))
    f.close()
    
@app.route('/addaudiotime', methods=['POST'])
def addaudiotime():
    amount       = request.json['amount']
    #try to read added time
    totaltime = read_audio_time()
    totaltime += amount
    write_audio_time(totaltime)
    return jsonify({'result':totaltime})
    
@app.route('/addoutputexercise', methods=['POST'])
def addoutputexercise():
    english               = request.json['english']
    chinesetokens         = request.json['chinesetokens']
    if len(chinesetokens) < 2:
        chinesetokens = textprocessing.split_text(chinesetokens[0])
        chinesetokens = json.dumps(chinesetokens)
    mp3name         = request.json['mp3name']
    type = request.json['type']
    result = request.json['result']
    milliseconds = request.json['milliseconds']
    whenutcmilliseconds = request.json['whenutcmilliseconds']
    database.add_output_exercise(english,chinesetokens,mp3name,type,result,milliseconds,whenutcmilliseconds)
    return jsonify({'result':'ok'})

@app.route('/addlisteningexercise', methods=['POST'])
def addlisteningexercise():
    sentence               = request.jsincomingtxton['sentence']
    chinesetokens         = request.json['tokens']
    if len(chinesetokens) < 2:
        chinesetokens = textprocessing.split_text(chinesetokens[0])
    result = request.json['result']
    database.add_listening_sentence(sentence,chinesetokens,result)
    return jsonify({'result':'ok'})

@app.route('/gettotalaudiotime', methods=['POST'])
def gettotalaudiotime():
    total = database.get_total_audio_time()
    return jsonify({'result':total})

@app.route('/gettotaloutputtime', methods=['POST'])
def gettotaloutputtime():
    total = database.get_total_output_time()
    return jsonify({'result':total})


@app.route('/add_example_to_cache', methods=['POST'])
def add_example_to_cache():
    example = request.json['example']
    cachemanagement.add_example_to_cache(example)
    return jsonify({'result':'ok'})


@app.route('/add_examples_to_cache', methods=['POST'])
def add_examples_to_cache():
    examples = request.json['examples']
    cachemanagement.add_examples_to_cache(examples)
    return jsonify({'result':'ok'})

import openrouter
@app.route('/gooutrouter', methods=['POST'])
def gooutrouter():
    question = request.json['question']
    result = openrouter.do_open_opus_questions(question)
    return jsonify({'result':result})

import mp3helper

@app.route('/getspokenarticles',methods=['POST'])
def getspokenarticles():
    files = [file for file in os.listdir('/var/www/html/mp3') if file.endswith('mp3')]    
    files = sorted(files, key=lambda f: os.path.getctime(os.path.join('/var/www/html/mp3', f)))
    timefiles = []
    for f in files:
        timefiles.append('/var/www/html/mp3/'+f)
    files.append(mp3helper.format_duration(mp3helper.get_total_mp3_duration(timefiles)))
    return jsonify({'result':files})
    
    
def get_next_spoken_article(mp3_file):
    print("called next spoken carticle " + mp3_file)
    files = [file for file in os.listdir('/var/www/html/mp3') if file.endswith('mp3')]    
    files = sorted(files, key=lambda f: os.path.getctime(os.path.join('/var/www/html/mp3', f)))
    nrfiles = len(files)
    idx = -1
    for i in range(0,nrfiles):
        print(files[i])
        if files[i].find(mp3_file) != -1:
            idx = i
    if idx != -1:
        return files[idx+1]
    else:
        return files[random.randint(0,nrfiles-1)]
    
    
import mp3helper
    
@app.route('/getspokenarticle',methods=['POST'])
def getspokenarticle():    
    # Path to the MP3 file
    mp3_file = request.json['mp3file']
    # Return the MP3 file
    #return jsonify({'result':None})
    srt_file_path = None    
    basename = os.path.basename(mp3_file)
    if request.json['next'] == True:
        mp3_file = get_next_spoken_article(mp3_file)
                
    hint_file = mp3_file + '.hint.json'
    if os.path.exists('/var/www/html/mp3/'+hint_file):
        f = open('/var/www/html/mp3/'+hint_file,'r',encoding='utf-8')
        chitext = f.read()
        f.close()
        chiret = json.loads(chitext)
    else:
        srtfile = basename.replace(".mp3",".srt")
        fullsrtfile = '/opt/watchit/' + srtfile
        if os.path.exists(fullsrtfile):
            f = open(fullsrtfile,'r',encoding='utf-8')
            chitext = f.read()
            chiret = textprocessing.split_text(chitext)
            print("loaded srt file " + fullsrtfile)
            srt_file_path = fullsrtfile
        else:
            fullsrtfile = '/var/www/html/mp3/' + basename.replace(".mp3",".srt")
            print("full srt file " + fullsrtfile)
            if os.path.exists(fullsrtfile):
                f = open(fullsrtfile,'r',encoding='utf-8')
                chitext = f.read()
                chiret = textprocessing.split_text(chitext)
                print("loaded srt file " + fullsrtfile)
                srt_file_path = fullsrtfile
            else:
                chiret = ['no','chinese','to','\n','be','found','!']    
    allhint_file = mp3_file + '.allhint.json'        
    if os.path.exists('/var/www/html/mp3/'+allhint_file):
        f = open('/var/www/html/mp3/'+allhint_file,'r',encoding='utf-8')
        allchitext = f.read()
        f.close()
        allchiret = json.loads(allchitext)
    else:
        allchiret = None
    print(srt_file_path)
    return jsonify({'result':{'filepath':mp3_file,'tokens':chiret,'extendedtokens':allchiret,'srtpath':srt_file_path}})

import random


@app.route('/makemp3fromtext', methods=['POST'])
def makemp3fromtext():
    print("makemp3fromtext called")
    try:
        mp3cache = '/var/www/html/mp3'
        incomingtxt = request.json['text']
                
        # now lets simplify it
        incomingtxt = openrouter.do_open_opus_questions("Simplify this to commonly spoken Cantonese that a young child can understand:" + incomingtxt)
        
        chosennumber = str(random.randint(0,100000))
        filepath = mp3cache + '/' + 'spokenarticle_'+chosennumber + '.mp3'
        incoming = []
        for i in incomingtxt.split('\n'):
            incoming.append(i)        
        f = open(filepath+'.hint','w',encoding='utf-8')
        f.write(json.dumps(incoming))
        f.close()
        
        #
        text = "<speak>" + incomingtxt + "</speak>"
        text = text.replace("\n","<break time=\\\"1s\\\"/>")
        print(filepath)
        output = 'aws polly synthesize-speech --output-format mp3 --voice-id "Hiujin" --engine neural --text-type ssml --text "' + text + '" ' + filepath + ' > out'
        print(output)
                
        f = open(mp3cache+'/makemp3.sh','w',encoding='utf-8')
        f.write(output)
        f.close()    

        #subprocess.run(output,shell=True,capture_output=True,text=True)
    except Exception as e:        
        return jsonify({'result':str(e)})    
    return jsonify({'result':'done'})


def replace_chinese_with_links(text):
    # Define a regular expression pattern to match Chinese characters
    pattern = r'[\u4e00-\u9fff\u0021\u003f\u002e\u002c\u002c\uff0c]+'

    def replace_function(match):
        chinese_text = match.group()
        encoded_chinese = urllib.parse.quote(chinese_text)
        return f'<a href="http://chinese.eriktamm.com/api/makeexamples?chinese={encoded_chinese}">{chinese_text}</a>'    
    return re.sub(pattern, replace_function, text)


@app.route('/getexplainationpage', methods=['GET'])
def getexplainationpage():
    sentence = request.args['sentence']
    ret = openrouter.do_open_opus_questions('Explain this cantonese sentence using English:' + sentence)
    ret = ret + openrouter.do_open_opus_questions('Rewrite this to spoken Cantonese:' + sentence)
    baloba = ret.replace('\n','<br/>')  
    baloba = replace_chinese_with_links(baloba)  
    return '<html><head/><body>' + baloba + '</body></html>'


@app.route('/simplevocab', methods=['GET'])
def simplevocab():
    api = openrouter.OpenRouterAPI()
    sentence = request.args['sentence']
    processor = 'studylater'
    stack = stringstack.PersistentStack('/var/www/html/scene/' + processor + '.stack')    
    stack.push(sentence)        
    ret = api.open_router_nova_micro_v1("List the vocab in this sentence with English and pronounciation in jyutping:" + sentence)
    return ret

from datetime import datetime 

@app.route('/makeexamples', methods=['GET'])
def makeexamples():
    chinese = request.args['chinese']
    aiquestion = 'Create 3 sentences in B2 level Cantonese containing this chunk: ' + chinese + ". Return these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."
    ret = openrouter.do_open_opus_questions('Explain this cantonese sentence using English:' + aiquestion)
    print("makeexamples"  + ret)
    parsedret = json.loads(ret)
    
    cachedresult = []
    htmlout = '<html><head/><body>'
    for r in parsedret:
        english = r['english']
        chinese = r['chinese']
        # lets make tokens out of chinese
        tradchinese = textprocessing.make_sure_traditional(chinese)
        htmlout = htmlout + english + '---' + tradchinese + '<br/>'

        chinesetokens = textprocessing.split_text(tradchinese)
        cachedresult.append({'chinese':chinesetokens,'english':english})
        database.add_output_exercise(english,str(chinesetokens).replace("'",'"'),"nomp3",2,1,0,int(datetime.now().timestamp() * 1000))
    cachemanagement.add_examples_to_cache(cachedresult)
    htmlout = htmlout + '</body></html'
    return htmlout


announcer = MessageAnnouncer.MessageAnnouncer()


@app.route('/ping')
def ping():
    datavalue = request.args.get('data')
    msg = MessageAnnouncer.format_sse(data= datavalue )
    announcer.announce(msg=msg)
    return {}, 200


@app.route('/commandstream', methods=['GET'])
def commandstream():

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return Response(stream(), mimetype='text/event-stream')

import audioimport

@app.route('/import_mp3', methods=['POST'])
def import_mp3():   
    audioimport.add_processed_mp3(request.json['filepath'],request.json['jsoncontent'],'')
    return {}, 200


@app.route('/explode_mp3', methods=['GET'])
def explode_mp3():   
    audioimport.explode_file(request.args.get('filename'))
    return {}, 200


import stringstack

@app.route('/add_background_work', methods=['POST'])
def add_background_work():
    processor   = request.json['processor']
    workstring  = request.json['workstring']
    stack = stringstack.PersistentStack('/var/www/html/scene/' + processor + '.stack')    
    stack.push(workstring)
    return {}, 200


@app.route('/get_background_work', methods=['POST'])
def get_background_work():
    processor   = request.json['processor']
    stack = stringstack.PersistentStack('/var/www/html/scene/' + processor + '.stack')    
    if stack.size() == 0:        
        return jsonify({'result':None})
    else:
        astr = stack.pop()
        return jsonify({'result':astr})


import stringstack

@app.route('/add_interest_to_stack', methods=['POST'])
def add_interest_to_stack():
    processor   = request.json['processor']
    workstring  = request.json['workstring']
    stack = stringstack.PersistentStack('/var/www/html/scene/' + processor + '.stack')    
    stack.push(workstring)
    return {}, 200


@app.route('/get_interest_from_stack', methods=['POST'])
def get_interest_from_stack():
    processor   = request.json['processor']
    stack = stringstack.PersistentStack('/var/www/html/scene/' + processor + '.stack')    
    if stack.size() == 0:        
        return jsonify({'result':None})
    else:
        astr = stack.pop()
        return jsonify({'result':astr})


@app.route('/peek_interest_from_stack', methods=['POST'])
def peek_interest_from_stack():
    processor   = request.json['processor']
    stack = stringstack.PersistentStack('/var/www/html/scene/' + processor + '.stack')    
    if stack.size() == 0:        
        return jsonify({'result':None})
    else:
        astr = stack.peek()
        return jsonify({'result':astr})
    

@app.route('/explain_sentence_free', methods=['POST'])
def explain_sentence_free():
    try:        
        sentence   = request.json['sentence']
        api = openrouter.OpenRouterAPI()
        result = api.open_router_meta_llama_3_2_3b_free("Explain the words and grammar of this sentence: " + sentence)        
        return jsonify({'result':result})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})



def long_running_adding_subtitle_chunk(sentence):
    # Task logic here
    tradchinese = textprocessing.make_sure_traditional(sentence)        
    chinesetokens = textprocessing.split_text(tradchinese)
    chsize = cachemanagement.add_example_to_cache({'chinese':chinesetokens,'english':sentence} )
    print('/add_subtitle_chunk' + sentence + "  tokens " + str(chinesetokens) + "\n" + str(chsize))
    pass


@app.route('/add_subtitle_chunk', methods=['POST'])
def add_subtitle_chunk():
    sentence   = request.json['sentence']
    long_running_adding_subtitle_chunk(sentence)
    return jsonify({'result':'ok'})


@app.route('/explain_sentence_cheap', methods=['POST'])
def explain_sentence_cheap():
    try:        
        sentence   = request.json['sentence']
        aiapi = openrouter.OpenRouterAPI()
        # keep trying this
        result = aiapi.open_router_mistral_7b_instruct("Translate this sentence and return the answer in this json-format: {\"translation\":english translation,\"words\":[[word1,definition in english],[word2,definition in english]] }. Only return the json." + sentence)
        end = result.find('}')
        result = result[:end+1]
        start = result.find('{')
        result = result[start:]
        result = result.replace('\n','')
        dop = json.loads(result)
        translation = dop['translation']
        soundlookup = {}
        for c in sentence:
            cchar = ''+c
            aresult = api.dictionary_lookup(cchar)
            soundlookup[cchar] = aresult
        splt = textprocessing.split_text(sentence)
        dop['soundlookup'] = soundlookup
        result = json.dumps(dop)
        cachemanagement.add_example_to_cache({'english':translation,'chinese':splt})
        return jsonify({'result':result})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})


import persistentdict

@app.route('/set_dictionary_value', methods=['POST'])
def set_dictionary_value():
    try:
        dictname   = request.json['dictionary']
        keyvalue = request.json['key']
        value = request.json['value']
        d = persistentdict.PersistentDict(dictname)
        d[keyvalue] = value
        return jsonify({'result':'ok'})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})

 
@app.route('/download_dictionary', methods=['POST'])
def download_dictionary():
    try:
        dictname   = request.json['dictionary']
        d = persistentdict.PersistentDict(dictname)
        return jsonify({'result':d.get_raw_data()})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})


@app.route('/explain_sentence', methods=['POST'])
def explain_sentence():
    try:
        sentence = request.json['sentence']
        api = openrouter.OpenRouterAPI()
        explain = api.open_router_qwen("你是粵語專家，分析文本。","解釋呢句嘅意思、詞彙同語法：" + sentence)
        result = textprocessing.split_text(explain)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})
    
    
@app.route('/ai_anything', methods=['POST'])
def ai_anything():
    try:
        question = request.json['question']
        api = openrouter.OpenRouterAPI()
        question_in_chinese = api.open_router_qwen("你是粵語專家。","Translate this to traditional Chinese:" + question)
        explain = api.open_router_qwen("你是粵語專家。",question_in_chinese)
        result = textprocessing.split_text(explain)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})


@app.route('/ai_perplexity', methods=['POST'])
def ai_perplexity():
    try:
        question = request.json['question']
        api = openrouter.OpenRouterAPI()       
        sonar_resply = api.open_router_perplexity_sonar_pro(question)        
        text = api.open_router_claude_3_5_sonnet("You are a cantonese expert, helping with translating written english to spoken Cantonese. Only respond using Cantonese written with Traditional Chinese. No Jyutping","Translate this text to spoken Cantonese spoken daily in Hong Kong:\n   " + sonar_resply)    
        result = textprocessing.split_text(text)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})



@app.route('/text2mp3', methods=['POST'])
def text2mp3():
    try:
        text = request.json['text']
        file_path = "/var/www/html/mp3/spokenarticl_news"+ str(random.randint(1000,2000))+".mp3"
        os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
        
        # Setup AWS session
        session = boto3.Session(region_name='us-east-1')
        polly_client = session.client('polly')
        
        # Handle long text by splitting into chunks (Polly has a limit)
        max_chars = 3000  # AWS Polly character limit per request
        chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
        
        # Process each chunk and combine the audio
        with open(file_path, 'wb') as outfile:
            for chunk in chunks:
                response = polly_client.synthesize_speech(  
                    Text=chunk,
                    OutputFormat='mp3',
                    VoiceId='Hiujin',
                    Engine='neural',
                    TextType='text'            
                )
                outfile.write(response['AudioStream'].read())
                
        # Save the text tokens for reference
        with open(file_path+".hint.json", 'w', encoding='utf-8') as file:
                jsonpart = textprocessing.split_text(text)
                file.write(json.dumps(jsonpart))    
        
        return jsonify({'result': file_path})
                
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})

@app.route('/text2mp3_small', methods=['POST'])
def text2mp3_small():
    try:
        text = request.json['text']
        file_path = "/var/www/html/mp3/spokenarticl_news"+ str(random.randint(1000,2000))+".mp3"
        os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
        session = boto3.Session(region_name='us-east-1')
        polly_client = session.client('polly')
        response = polly_client.synthesize_speech(  
                    Text=text,
                    OutputFormat='mp3',
                    VoiceId='Hiujin',
                    Engine='neural',
                    TextType='text'            
                )
        with open(file_path, 'wb') as file:
                file.write(response['AudioStream'].read())    
        with open(file_path+".hint.json", 'w', encoding='utf-8') as file:
                jsonpart = textprocessing.split_text(text)
                file.write(json.dumps(jsonpart))    
        return jsonify({'result':text})
                
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})


@app.route('/upload_dictionary', methods=['POST'])
def upload_dictionary():
    try:
        dictname   = request.json['dictionary']
        values = request.json['values']
        d = persistentdict.PersistentDict(dictname)
        for i in values.keys():
            d[i] = values[i]
        return jsonify({'result':'ok'})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})

@app.route('/get_dictionary_value', methods=['POST'])
def get_dictionary_value():
    try:
        dictname   = request.json['dictionary']
        keyvalue = request.json['key']
        d = persistentdict.PersistentDict(dictname)
        if keyvalue in d:
            return jsonify({'result':[keyvalue,d[keyvalue]]})
        else:
            return jsonify({'result':[keyvalue,None]})
    except Exception as e:
        return jsonify({'result':None,"reason":str(e)})


@app.route('/make_examples_from_chunk', methods=['GET'])
def make_examples_from_chunk():
    chunk = request.args.get('chunk')
    api=openrouter.OpenRouterAPI()
    result = api.open_router_claude_3_5_sonnet("You are a Cantonese expert teaching foreigners.",
    "Create 3 sentences in B2 level Cantonese containing this chunk: " + chunk+ " \nReturn these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure.")
    parsedret = json.loads(result)
    cachedresult = []
    for r in parsedret:
        english = r['english']
        chinese = r['chinese']
        # lets make tokens out of chinese
        tradchinese = textprocessing.make_sure_traditional(chinese)        
        chinesetokens = textprocessing.split_text(tradchinese)
        cachedresult.append({'chinese':chinesetokens,'english':english})
        database.add_output_exercise(english,str(chinesetokens).replace("'",'"'),"nomp3",2,1,0,int(datetime.now().timestamp() * 1000))
    cachemanagement.add_examples_to_cache(cachedresult)
    return jsonify({'result':'ok'})



@app.route('/make_grammar_examples', methods=['POST'])
def make_grammar_examples():
    grammar_pattern = request.json['grammar_pattern']
    api=openrouter.OpenRouterAPI()
    result = api.open_router_claude_3_5_sonnet("You are a Cantonese language expert.",
    "Create 10 sentences in C1 level Cantonese with this meta-structure: " + grammar_pattern + " \nReturn these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure.")
    i = result.find("[")
    result = result[i:]
    i = result.find("]")
    result = result[:i+1]
    print(result)

    parsedret = json.loads(result)
    cachedresult = []
    for r in parsedret:
        if "english" in r and "chinese" in r:
            english = r['english']
            chinese = r['chinese']
            # lets make tokens out of chinese
            print(english)
            print(chinese)
            tradchinese = textprocessing.make_sure_traditional(chinese)        
            chinesetokens = textprocessing.split_text(tradchinese)
            cachedresult.append({'chinese':chinesetokens,'english':english})
            database.add_output_exercise(english,str(chinesetokens).replace("'",'"'),"nomp3",2,1,0,int(datetime.now().timestamp() * 1000))
    cachemanagement.add_examples_to_cache(cachedresult)
    return jsonify({'result':'ok'})

#PersistentDict

import texttoaudio



def make_long_time_b1_examples(pattern):
    api=openrouter.OpenRouterAPI()
    result = api.open_router_deepseek_r1(
    "Create 20 sentences in B1 level spoken Cantonese " + pattern + " \nReturn these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure.")
    i = result.find("[")
    result = result[i:]
    i = result.find("]")
    result = result[:i+1]
    print(result)
    txt = '<speak>'
    parsedret = json.loads(result)
    tuples = []
    hinttxt = ''
    for r in parsedret:
        if "english" in r and "chinese" in r:
            english = r['english']
            chinese = r['chinese']
            # lets make tokens out of chinese
            tradchinese = textprocessing.make_sure_traditional(chinese)
            tuples.append((english,tradchinese))
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( tradchinese ))
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( english ))
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( tradchinese ))            
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( tradchinese ))
            hinttxt += tradchinese + "\n"
    txt+='</speak>'
    hinttxt+='\n'
    print(str(tuples))
    file_path = "/var/www/html/mp3/spokenarticl_news_c1_"+ str(random.randint(1000,2000))+".mp3"
    #failedsentences_to_mp3.generate_audio_from_tuples(tuples,file_path,scp=False)
    print("All done: "+ txt)


def make_long_time_c1_examples(pattern):
    api=openrouter.OpenRouterAPI()
    result = api.open_router_deepseek_r1(
    "Create 15 sentences in C1 level spoken Cantonese " + pattern + " \nReturn these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure.")
    i = result.find("[")
    result = result[i:]
    i = result.find("]")
    result = result[:i+1]
    print(result)
    txt = '<speak>'
    parsedret = json.loads(result)
    tuples = []
    hinttxt = ''
    for r in parsedret:
        if "english" in r and "chinese" in r:
            english = r['english']
            chinese = r['chinese']
            # lets make tokens out of chinese
            tradchinese = textprocessing.make_sure_traditional(chinese)
            tuples.append((english,tradchinese))
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( tradchinese ))
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( english ))
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( tradchinese ))            
            txt+= texttoaudio.surround_text_with_short_pause(texttoaudio.surround_text_with_short_pause( tradchinese ))
            hinttxt += tradchinese + "\n"
    txt+='</speak>'
    hinttxt+='\n'
    print(str(tuples))
    file_path = "/var/www/html/mp3/spokenarticl_news_c1_"+ str(random.randint(1000,2000))+".mp3"
    #failedsentences_to_mp3.generate_audio_from_tuples(tuples,file_path,scp=False)
    print("All done: "+ txt)
    
      
from threading import Thread

@app.route('/make_c1_examples', methods=['POST'])
def make_c1_examples():
    pattern = request.json['pattern']
    Thread(target=make_long_time_c1_examples, args=(pattern,)).start()
    return jsonify({"status": "Task started"}), 202
    return jsonify({'result':'ok'})


import homecommand
import config
@app.route('/executehomecommand', methods=['POST'])
def executehomecommand():
    command   = request.json['command']
    directory = request.json['directory']
    secret = config.get_config_value('HOMECOMMANDSECRET')
    if command.find(secret) == -1:
        return jsonify({'result':'error'})
    command = command.replace(secret,'')
    homecommand.run_command_on_remote(command,directory);
    return jsonify({'result':'ok'})



import stockmanager
import dbconfig
import os
@app.route('/stockupdate', methods=['POST'])
def stockupdate():
    try:
        
        stockblock = request.json['stockblock']
        stmgr = stockmanager.StockManager(
            "localhost",
            "erik",
            dbconfig.get_db_password(),
            "language"
        )
        stmgr.parse_block(stockblock)
        bop = stmgr.get_latest_stock_prices()
        
        ret = '<html><head/><body><table>'
        for stock in bop:
            ret += '<tr><td>' + stock[0] + '</td><td>' + str(stock[1]) + '</td><td>' + str(stock[2]) + '</td><td>' + str(stock[3]) + '</td></tr>'
        ret += '</table><br/><br/>'
        
        bop = stmgr.get_stocks_with_rating_change()
        
        ret += '<table>'
        for stock in bop:
            ret += '<tr><td>' + stock[0] + '</td><td>' + stock[1] + '</td><td>' + stock[2] + '</td><td></tr>'
        ret += '</table></body></html>'
        
        print(ret)
        f = open('/var/www/html/mp3/stocks.html','w')
        f.write(ret)
        f.close()
        stmgr.close()
        return jsonify({'result':'ok'})
    except Exception as e:
        print(str(e))
        return jsonify({'result':None,"reason":str(e)})


@app.route('/getfailedreadingtests', methods=['POST'])
def getfailedreadingtests():
    try:
        days   = request.json['days']
        result = database.get_failed_reading_tests(days)
        return jsonify({'result':result})
    except Exception as e:
        print(str(e))
        return jsonify({'result':None,"reason":str(e)})

import base64

import subprocess

def convert_webm_to_mp3(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-codec:a', 'libmp3lame', output_file]
    subprocess.run(command, check=True)

@app.route('/tokenize_chinese', methods=['POST'])
def tokenize_chinese():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input. "text" parameter is required.'}), 400
    text = data['text']
    text = textprocessing.make_sure_traditional(text)
    tokens = textprocessing.split_text(text)
    return jsonify({'result': tokens})

@app.route('/ask_nova', methods=['POST'])
def ask_nova():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input. "text" parameter is required.'}), 400
    text = data['text']
    api=openrouter.OpenRouterAPI()
    reply = api.open_router_nova_micro_v1(text)
    text = textprocessing.make_sure_traditional(reply)
    tokens = textprocessing.split_text(text)
    return jsonify({'result': tokens})




@app.route('/videosegment', methods=['POST'])
def videosegment():
    try:
        data = request.json
        url = data.get('url')
        binary_data = data.get('data')
        timestamp = data.get('timestamp')
        
        if not all([url, binary_data, timestamp]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Create directory if it doesn't exist
        video_dir = '/var/www/html/video_segments'
        os.makedirs(video_dir, exist_ok=True)
        
        # Generate a unique filename
        filename = f"{timestamp}_{os.path.basename(url).replace('/', '_')}"
        filepath = os.path.join(video_dir, filename)
        
        # Convert array back to binary and save
        with open(filepath, 'wb') as f:
            f.write(bytes(binary_data))
        
        return jsonify({'result': 'Video segment saved successfully', 'filepath': filepath}), 200
    
    except Exception as e:
        print(f"Error processing video segment: {str(e)}")
        return jsonify({'error': str(e)}), 500


import coach.teaching_agent

def read_bearer_key() -> str:
    try:
        with open('/var/www/html/api/rfbackend/routerkey.txt', 'r') as f:
            return f.readline().strip()
    except FileNotFoundError:
        raise Exception("API key file not found")


agent = coach.teaching_agent.TeachingAgent(api_key=read_bearer_key())

@app.route('/coach/start_session', methods=['POST'])
def start_session():
    data = request.json
    student_name = data.get('student_name')

    # Set student name
    if not agent.student_state.name and student_name:
        agent.student_state.name = student_name
        agent._add_system_message(f"學生名字是 {student_name}。")

    return jsonify({"message": "Session started", "student_name": agent.student_state.name})

@app.route('/coach/input', methods=['POST'])
def user_input():
    data = request.json
    student_input = data.get('input')

    # Process user input
    if student_input:
        try:
            response = agent.handle_input(student_input)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "No input provided"}), 400




## here comes my magic bot
sessions = {}

#I want to add the following
class SessionManager:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = deque(maxlen=20)
        self.model = "anthropic/claude-sonnet-4"
        self.context_limit = 1024*100  # in tokens
        self.system_prompt = """
        You are "CantoTutor," a friendly, patient, and highly adaptive Cantonese tutor. Your primary goal is to personalize the learning experience for each user. You will assess their proficiency and tailor the lesson's difficulty accordingly. You must adhere to the following interaction model.

--- ONBOARDING & SESSION START ---

Your first priority is to determine the user's level.

Check for a Learning Snapshot: If the user begins by pasting a "Learning Snapshot" from a previous session, acknowledge it and use that data to set the lesson's difficulty, skipping the calibration phase.

Example: "Welcome back! Thanks for the snapshot. I see we were working on the difference between 咗 (zo2) and 過 (gwo3). Let's pick up from there."
Initiate Calibration Phase (For new users): If no snapshot is provided, you must initiate a brief calibration to assess their level.

Explain the process: "Welcome to CantoTutor! I'm here to help you improve your Cantonese. To find the perfect starting point for you, I'm going to ask you to translate just a few sentences, from easy to more difficult. Don't worry about getting them perfect, this just helps me tailor our lesson. Ready to start?"
Conduct Calibration: Present 2-3 English sentences, one by one, with increasing difficulty. During this phase, do not give detailed feedback. Just acknowledge their attempt ("Thanks!", "Okay, got it.") and move to the next sentence.
Start with (Easy): "I am very busy today."
Then (Medium): "I forgot to bring my umbrella, so I got soaked in the rain."
Then (Challenging): "Despite the unforeseen circumstances, the event was a remarkable success."
Assess and Confirm: After they've attempted the calibration sentences, make a gentle assessment and confirm with the user.
Example: "Great, thank you! It looks like you have a solid grasp of basic sentence structures, so we can focus on more complex ideas and natural phrasing. Does that sound good to you?"
--- CORE INTERACTION LOOP ---

Once the level is set, begin the main lesson.

Present a Challenge: Provide an English sentence that is appropriate for the user's assessed level.

Dynamically Adjust: Continuously monitor the user's performance.

If they answer easily, make the next sentence slightly more complex (e.g., more subordinate clauses, more idiomatic English).
If they struggle significantly, simplify the next sentence to target the specific concept they're having trouble with.
Provide Structured Feedback: You must use the following Markdown format for your reply.

Feedback on Your Translation
(Acknowledge their effort and point out what they did well first.)

Correction
(If there are errors, provide the corrected version. If perfect, state that.)

Your version: [User's translation with 漢字 (jyutping)]
Corrected version: [Corrected translation with 漢字 (jyutping)]
More Natural Version
(Provide a more native-speaker version.)

Option 1: [Natural Cantonese sentence with 漢字 (jyutping)]
Explanation
(Explain the "why" behind corrections, focusing on grammar, vocabulary, and natural phrasing.)

Follow-up Practice
(Based on performance, create a new, relevant English sentence.)
Now, try translating this: [New English sentence]
--- SESSION END & SUMMARY ---

When the user wants to end the session (e.g., "I have to go"), initiate the summary.

Generate a Learning Snapshot: Provide a structured summary in a JSON code block for the user to save for the next session.
Here is a sample:
{
  "student_level_estimate": "Intermediate (Working on complex sentences)",
  "key_learnings": ["Learned to use '好唔好 (hou2 m4 hou2)' for decisions.", "Practiced the 'so...that' structure using '到... (dou3...)'."],
  "areas_for_review": ["Distinction between '咗 (zo2)' and '過 (gwo3)'.", "Correct measure words for objects."],
  "suggestion_for_next_session": "Start with sentences that use measure words to build confidence in that area."
}


📚 Your Learning Snapshot
Here is a summary of our session. Copy this and paste it at the start of our next lesson so I can tailor it for you!


{
  "student_level_estimate": "Intermediate (Working on complex sentences)",
  "key_learnings": ["Learned to use '好唔好 (hou2 m4 hou2)' for decisions.", "Practiced the 'so...that' structure using '到... (dou3...)'."],
  "areas_for_review": ["Distinction between '咗 (zo2)' and '過 (gwo3)'.", "Correct measure words for objects."],
  "suggestion_for_next_session": "Start with sentences that use measure words to build confidence in that area."
}
--- CRUCIAL RULES ---

Always Use Jyutping: Every piece of Cantonese text must be followed by its Jyutping romanization in parentheses.
Maintain Persona: Always be encouraging, patient, and adaptive.
Be Flexible: If the user asks a question, pause the loop to answer it before proceeding.
Try to use the feedback from last lesson even if it is not in proper json format.

"""
        self._init_conversation()
        
    def _init_conversation(self):
        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        self._trim_context()
    
    def _trim_context(self):
        current_length = sum(len(msg["content"].split()) for msg in self.messages)
        while current_length > self.context_limit * 0.75:  # Approximate token count
            if len(self.messages) > 1:
                removed = self.messages.popleft()
                if removed["role"] == "system":
                    self.messages.appendleft(removed)  # Keep system prompt
                    removed = self.messages.popleft()
                current_length -= len(removed["content"].split())
            else:
                break
    
    def update_model(self, new_model):
        self.model = new_model
    
    def update_system_prompt(self, new_prompt):
        self.system_prompt = new_prompt
        self.messages[0]["content"] = new_prompt

from flask import Flask, request, jsonify, render_template_string
import uuid
from collections import deque


@app.route('/aiclient')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLM Chat</title>
        <style>
            #chat { height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; }
            .message { margin: 5px 0; padding: 5px; background: #f0f0f0; }
            #input { width: 70%; }
        </style>
    </head>
    <body>
        <h1>LLM Chat</h1>
        <div id="chat"></div>
        <input type="text" id="input" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
        
        <div>
            <label>Model: 
            <select id="model" onchange="updateModel(this.value)">
                <option value="qwen/qwen-plus">qwen/qwen-plus</option>
                <option value="meta-llama/llama-3-70b-instruct">Llama 3 70B</option>
                <option value="google/palm-2">PaLM 2</option>
                <option value="openchat/openchat-7b">OpenChat 7B</option>
            </select>
            </label>
            
            <label>System Prompt: 
            <textarea id="system_prompt" onchange="updateSystemPrompt(this.value)" 
                      style="width: 300px; height: 100px;">You are a helpful assistant.</textarea>
            </label>
        </div>

        <script>
            let sessionId = null;
            
            function createSession() {
                fetch('https://chinese.eriktamm.com/api/session', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => sessionId = data.session_id);
            }
            
            function sendMessage() {
                const input = document.getElementById('input');
                const chat = document.getElementById('chat');
                
                chat.innerHTML += `<div class="message"><b>You:</b> ${input.value}</div>`;
                
                fetch('https://chinese.eriktamm.com/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: input.value
                    })
                })
                .then(r => r.json())
                .then(data => {
                    chat.innerHTML += `<div class="message"><b>Assistant:</b> ${data.response}</div>`;
                    chat.scrollTop = chat.scrollHeight;
                    input.value = '';
                });
            }
            
            function updateModel(model) {
                fetch('https://chinese.eriktamm.com/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        model: model
                    })
                });
            }
            
            function updateSystemPrompt(prompt) {
                fetch('https://chinese.eriktamm.com/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        system_prompt: prompt
                    })
                });
            }
            
            // Initialize session on page load
            window.onload = createSession;
        </script>
    </body>
    </html>
    ''')

@app.route('/session', methods=['POST'])
def create_session():
    if not sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = SessionManager(session_id)
        return jsonify({"session_id": session_id})
    else:
        return jsonify({"session_id": next(iter(sessions))})
    
def is_chinese(character):
    code_point = ord(character)
    # Check if the character's code point is in the range of Chinese characters
    return '\u4E00' <= character <= '\u9FFF'


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session = sessions.get(data['session_id'])
    
    if not session:
        return jsonify({"error": "Invalid session"}), 404
    
    session.add_message("user", data['message'])
    
    # Call OpenRouter API
    headers = {
        "Authorization": read_bearer_key(),
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": session.model,
        "messages": list(session.messages),
        "temperature": 0.7
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=payload)
    
    if response.status_code == 200:
        ai_message = response.json()['choices'][0]['message']['content']
        session.add_message("assistant", ai_message)
        for c in ai_message:
            if (is_chinese(c)):
                myinputmethod.update_input_method_prio(c)

        database.add_entry(prompt="prompt",system_prompt=session.system_prompt,reply=ai_message)
        return jsonify({"response": ai_message})
    else:
       print(f"API call failed with status code {response.status_code}")
       print(response.text)
       print(headers)
       print(payload)
    
    return jsonify({"error": "API call failed"}), 500




@app.route('/config', methods=['POST'])
def update_config():
    data = request.json
    session = sessions.get(data['session_id'])
    
    if not session:
        return jsonify({"error": "Invalid session"}), 404
    
    if 'model' in data:
        session.update_model(data['model'])
    if 'system_prompt' in data:
        session.update_system_prompt(data['system_prompt'])
    
    return jsonify({"status": "updated"})



import activity_time_tracker

# Flask route to get accumulated time for an activity
@app.route('/get_time', methods=['GET'])
def get_time():
    activity_name = request.args.get('activity_name')

    if not activity_name:
        return jsonify({"error": "Activity name is required"}), 400

    accumulated_time = activity_time_tracker.get_accumulated_time(activity_name)
    total_accumulated_time = activity_time_tracker.get_accumulated_time(activity_name,all_activity=True)

    return jsonify({
        "activity_name": activity_name,
        "accumulated_time": int(accumulated_time),
        "total_accumulated_time":int(total_accumulated_time)
    }), 200


@app.route('/add_time', methods=['POST'])
def add_time():
    data = request.get_json()
    activity_name = data.get('activity_name')
    milliseconds_to_add = data.get('milliseconds_to_add')

    if not activity_name or not isinstance(milliseconds_to_add, int) or milliseconds_to_add < 0:
        return jsonify({"error": "Invalid input"}), 400

    success = activity_time_tracker.add_time_to_activity(activity_name, milliseconds_to_add)

    if success:
        return jsonify({"message": "Time added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add time"}), 500


@app.route('/remove_time', methods=['GET','POST'])
def remove_time():    
    success = activity_time_tracker.remove_time()    
    if success:
        return jsonify({"message": "Time added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add time"}), 500


@app.route('/getwritingtime', methods=['GET'])
def get_writing_time():
    try:
        total_time = activity_time_tracker.get_total_accumulated_time('writing')
        daily_time = activity_time_tracker.get_accumulated_time('writing')
        return jsonify({
            "totalTime": total_time,
            "dailyTime": daily_time
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/llmentries', methods=['POST'])
def add_entry():
    """Add a new entry to the llm_interaction_log table."""
    data = request.json
    prompt = data.get('prompt')
    system_prompt = data.get('system_prompt')
    reply = data.get('reply')

    if not all([prompt, reply]):
        return jsonify({"error": "Prompt and reply are required fields."}), 400

    database.add_entry(prompt=prompt,system_prompt=system_prompt,reply=reply)
    return jsonify({"result": "Time added successfully"}), 200


@app.route('/llmentries', methods=['GET'])
def get_all_entries():
    """Retrieve all entries from the llm_interaction_log table."""
    try:
        result = database.get_all_entries()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/llmentries/last_24_hours', methods=['GET'])
def get_entries_last_24_hours():
    """Retrieve entries added within the last 24 hours."""
    try:
        result = database.get_entries_last_24_hours()
        return jsonify({"result":result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/coachfeedback', methods=['GET'])
def coachfeedback():
    txtmass = ""
    result = database.get_entries_last_24_hours()
    for r in result:
        txtmass += str(r) + "\n"
    api = openrouter.OpenRouterAPI()
    result = api.open_router_claude_3_5_sonnet("You are a language teaching expert, helping teachers to make their tutoring more efficient","From this lesson transcript, write notes what the student needs to practice on:" + txtmass)
    return jsonify({"result":result}), 200
  

@app.route('/make_lesson_vocabulary', methods=['GET'])
def make_lesson_vocabulary():
    txtmass = ""
    result = database.get_entries_from_last_n_days(7)
    for r in result:
        txtmass += str(r) + "\n"
    api = openrouter.OpenRouterAPI()
    result = api.open_router_meta_llama_3_3_70b("Extract the Cantonese vocabulary from this text,put one term on each line :" + txtmass)
    make_long_time_b1_examples(result)
    return jsonify({"result":result}), 200



  
import myinputmethod
import requests
import json
import cnn

@app.route('/jyutpingdict', methods=['GET'])
def jyutpingdict():
    jdict = myinputmethod.get_jyutping_dict()
    return jsonify({"result":jdict}), 200
   
@app.route('/update_jyutping_dict_prio', methods=['GET'])
def update_jyutping_dict_prio():
    characters = request.args.get('characters')
    for c in characters:        
        myinputmethod.update_input_method_prio(c)
    return jsonify({"result":'ok'}), 200


@app.route('/add_jyutping', methods=['GET'])
def add_jyutping():
    character = request.args.get('character')
    jyutping = request.args.get('jyutping')
    myinputmethod.add_character_to_input_method(character, jyutping)
    return jsonify({'message': 'Character added successfully'}), 200
 
#add_character_to_input_method


# Dictionary to store activity goals
activity_goals = {}

# Load existing goals from file if available
def load_goals():
    global activity_goals
    try:
        with open('/var/www/html/scene/activity_goals.json', 'r') as f:
            activity_goals = json.load(f)
    except FileNotFoundError:
        activity_goals = {}

# Save goals to file
def save_goals():
    with open('/var/www/html/scene/activity_goals.json', 'w') as f:
        json.dump(activity_goals, f)

# Load goals at startup
load_goals()

@app.route('/studygoals/set', methods=['POST'])
def set_study_goal():
    data = request.json
    activity = data.get('activity')
    hours = data.get('hours')
    if not activity or not isinstance(hours, (int, float)):
        return jsonify({'error': 'Invalid input'}), 400
    activity_goals[activity] = hours
    save_goals()
    return jsonify({'result': 'Goal set successfully'}), 200

@app.route('/studygoals/get', methods=['GET'])
def get_study_goal():
    activity = request.args.get('activity')
    if not activity:
        return jsonify({'error': 'Activity parameter is required'}), 400
    hours = activity_goals.get(activity)
    if hours is None:
        return jsonify({'error': 'Activity not found'}), 404
    return jsonify({'activity': activity, 'hours': hours}), 200
    
def extract_json_array_from_string(text):
    """
    Extract a JSON array from a string by finding everything between the first '[' and the last ']'
    
    Args:
        text (str): The string containing a JSON array
        
    Returns:
        list: The parsed JSON array or None if parsing fails
    """
    try:
        # Find the first '[' character
        start_index = text.find('[')
        if start_index == -1:
            return None
            
        # Find the last ']' character
        end_index = text.rfind(']')
        if end_index == -1:
            return None
            
        # Extract the JSON array substring
        json_array_str = text[start_index:end_index + 1]
        
        # Parse the JSON array
        json_array = json.loads(json_array_str)
        return json_array
    except json.JSONDecodeError:
        return None
    

    
@app.route('/extract_chinese_sentences', methods=['POST'])
def extract_chinese_sentences():
    api = openrouter.OpenRouterAPI()
    data = request.json
    page = data.get('page')
    result = api.open_router_nova_micro_v1("extract all chinese sentences from this page and return them in a list together with their translations in json format (e.g. [{\"chinese\": \"你好\", \"translation\": \"hello\"}]):\n\n"+page)
    return jsonify({'sentences': result}), 200



def append_to_json_array(new_items, filepath):
    """
    Appends new items to a JSON array stored in a file.
    If the file doesn't exist, creates a new array with the items.
    
    Args:
        new_items: Array of items to append
        filepath: Path to the JSON file
        
    Returns:
        The combined array (existing items + new items)
    """
    existing_items = []
    
    # Try to read existing file
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            existing_items = json.loads(file.read())
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or isn't valid JSON, start with empty array
        existing_items = []
    
    # Combine arrays
    combined_items = existing_items + new_items
    
    # Write back to file
    flatten_objects = flatten_structure(combined_items)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(flatten_objects, file, ensure_ascii=False)
    return flatten_objects


def flatten_structure(obj):
    """
    Recursively flattens a nested structure of arrays and dictionaries into a list of dictionaries.
    
    Args:
        obj: An object that can be either a dictionary, a list/array, or a leaf value
        
    Returns:
        list: A flat list containing all leaf dictionaries found in the structure
    """
    result = []
    
    # Base case: if obj is a dictionary and doesn't contain lists or dicts, it's a leaf
    if isinstance(obj, dict):
        # Check if this dict contains any nested dicts or lists
        has_nested = any(isinstance(v, (dict, list)) for v in obj.values())
        
        if not has_nested:
            # This is a leaf dictionary
            return [obj]
        else:
            # Process each value in the dictionary
            for value in obj.values():
                result.extend(flatten_structure(value))
    
    # If obj is a list, process each element
    elif isinstance(obj, list):
        for item in obj:
            result.extend(flatten_structure(item))
    
    # If obj is anything else (leaf value that's not a dict), return empty list
    return result

word_order_filepath = "/var/www/html/mp3/wordorder.json"
@app.route('/add_word_orders', methods=['POST'])
def add_word_orders():
    try:
        data = request.json
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text parameter is required'}), 400        
        #word_orders = textprocessing.extract_word_orders(text)
        api = openrouter.OpenRouterAPI()
        result = api.open_router_nova_micro_v1("Extract Cantonese word order rules from this text, make a list of them with a name and the structure and return in json format:\n\n"+text)
        newArray = extract_json_array_from_string(result)
        newNewArray = append_to_json_array(newArray,word_order_filepath) 
        return jsonify({'result': newNewArray})
    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500


#hi ninja

@app.route('/word_orders', methods=['GET'])
def word_orders():
    try:
        newNewArray = append_to_json_array([],word_order_filepath) 
        return jsonify({'result': newNewArray})
    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/get_webm_files', methods=['GET'])
def get_webm_files():
    try:
        directory = request.args.get('directory',   '/opt/watchit/')  # Default directory if none provided
        
        # Get all files with .webm extension
        webm_files = [file for file in os.listdir(directory) if file.endswith('.webm')]
        
        # Get file creation time and sort files by it
        webm_files_with_time = [(file, os.path.getctime(os.path.join(directory, file))) for file in webm_files]
        webm_files_with_time.sort(key=lambda x: x[1], reverse=True)  # Sort from newest to oldest
        
        # Remove the extension from filenames and keep only the sorted filenames
        filenames_without_extension = [os.path.splitext(file[0])[0] for file in webm_files_with_time]
        
        return jsonify({'result': filenames_without_extension})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_webm_files_old', methods=['GET'])
def get_webm_files_old():
    try:
        directory = request.args.get('directory',   '/opt/watchit/')  # Default directory if none provided
        
        # Get all files with .webm extension
        webm_files = [file for file in os.listdir(directory) if file.endswith('.webm')]
        
        # Remove the extension from filenames
        
        filenames_without_extension = [os.path.splitext(file)[0] for file in webm_files]
        
        return jsonify({'result': filenames_without_extension})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate_cloze', methods=['POST'])
def generate_cloze():
    api = openrouter.OpenRouterAPI()
    data = request.json
    thetext = data.get('text')
    thetext = thetext.replace('\""','@')
    if len(thetext) > 50000:
        thetext = thetext[:50000]
    
    result = api.open_router_claude_3_7_sonnet("You are a cantonese expert that is creating learning material for foreigners learning Cantonese.","""Generate a JSON-formatted cloze test based on the following text. The JSON should include:

    A title (e.g., the text's original title or a derived name).

    instructions explaining the task (e.g., 'Fill in the blanks with the correct words from the text').

    The text with blanks replaced by placeholders like [BLANK_1], [BLANK_2], etc. There will be maximum one blank per sentence.

    An answers array containing the correct words in order.

    Example format:

    {
    'title': 'Title of the Text',
    'instructions': 'Fill in the blanks with the correct words from the text.',
    'text': 'Text with [BLANK_1], [BLANK_2], ...',
    'answers': ['word1', 'word2', ...]
    }

    Process the input text and return the JSON structure only - no text around it. Ensure the text retains its original structure (line breaks, formatting) and the answers match the blanks in order. Here is the input:""" + thetext)
    result = result.replace('json','')
    result = result.replace('```','')
    start = result.find('{')
    end = result.rfind('}')
    if start == -1 or end == -1:
        return jsonify({'error': 'Invalid JSON format returned from the API'}), 400
    result = result[start:end+1]
    return jsonify({'result': result}), 200

@app.route('/ask_claude', methods=['POST'])
def ask_claude():
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'Question parameter is required'}), 400
        
        api = openrouter.OpenRouterAPI()
        result = api.open_router_claude_3_7_sonnet("You are a helpful assistant.", question)
        
        return jsonify({'result': result}), 200
    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/adventure', methods=['GET'])
def adventure():
    try:
        directory = '/var/www/html/adventures'  # Define the directory path where JSON files are stored
        
        # Get list of all JSON files in the directory
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        
        if not json_files:
            return jsonify({'error': 'No adventure JSON files found'}), 404
        
        # Pick a random JSON file
        random_file = random.choice(json_files)
        file_path = os.path.join(directory, random_file)
        
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            adventure_data = json.load(f)
        
        return jsonify({'result': adventure_data, 'filename': random_file}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/flashcard', methods=['GET'])
def flashcard():
    try:
        directory = '/var/www/html/flashcards'  # Define the directory path where JSON files are stored
        
        # Get list of all JSON files in the directory
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        
        if not json_files:
            return jsonify({'error': 'No adventure JSON files found'}), 404
        
        # Pick a random JSON file
        random_file = random.choice(json_files)
        file_path = os.path.join(directory, random_file)
        
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            adventure_data = json.load(f)
        
        return jsonify({'result': adventure_data, 'filename': random_file}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import flashcardgenerate

@app.route('/flashcard_from_text', methods=['POST'])
def flashcard_from_text():
    try:        
        directory = '/var/www/html/flashcards'  # Define the directory path where JSON files are stored        
        data = request.json
        text = data.get('text')
        returnflash = flashcardgenerate.get_server_flashcard_from_text(text)
        return jsonify({'result': returnflash}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/flashcard_from_list', methods=['POST'])
def flashcard_from_list():
    try:        
        directory = '/var/www/html/flashcards'  # Define the directory path where JSON files are stored        
        data = request.json
        wordlist = data.get('wordlist')
        returnflash = flashcardgenerate.get_server_flashcard_from_list(wordlist)
        return jsonify({'result': returnflash}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# hi there

import sys
@app.route('/install_package', methods=['POST'])
def install_package():
    try:
        data = request.json
        package = data.get('package')        
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return jsonify({'result': 'ok'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/audioadventure', methods=['GET'])
def audioadventure():
    try:
        directory = '/var/www/html/audioadventures'  # Define the directory path where JSON files are stored
        
        # Get list of all JSON files in the directory
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        
        if not json_files:
            return jsonify({'error': 'No adventure JSON files found'}), 404
        
        # Pick a random JSON file
        random_file = random.choice(json_files)
        file_path = os.path.join(directory, random_file)
        
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            adventure_data = json.load(f)
        
        return jsonify({'result': adventure_data, 'filename': random_file}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/managelist', methods=['POST'])
def managelist():
    try:
        data = request.json
        name = data.get('name')
        command = data.get('command')
        word = data.get('word', None)
        
        # Validate inputs
        if not name or not command:
            return jsonify({'error': 'Name and command parameters are required'}), 400
        
        # Create directory if it doesn't exist
        os.makedirs('/opt/wordlists', exist_ok=True)
        
        file_path = f'/opt/wordlists/{name}.json'
        
        if command == 'get':
            # Get the list contents
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    word_list = json.load(f)
                return jsonify({'result': word_list}), 200
            else:
                return jsonify({'result': []}), 200
                
        elif command == 'addto':
            # Add a word to the list
            if not word:
                return jsonify({'error': 'Word parameter is required for addto command'}), 400
                
            word_list = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    word_list = json.load(f)
                    
            if word not in word_list:
                word_list.append(word)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(word_list, f, ensure_ascii=False)
                
            return jsonify({'result': 'Word added successfully'}), 200
            
        elif command == 'delete':
            # Delete the list
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({'result': 'List deleted successfully'}), 200
            else:
                return jsonify({'error': 'List does not exist'}), 404
        elif command == 'deleteWord':
            # Delete the list
            word_list = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    word_list = json.load(f)
            if word in word_list:
                word_list.remove(word)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(word_list, f, ensure_ascii=False) 
                return jsonify({'result': 'Word deleted successfully'}), 200
            else:
                return jsonify({'error': 'Word does not exist'}), 404                
        else:
            return jsonify({'error': 'Invalid command. Use get, addto, or delete'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
import rthknews
@app.route('/random_cnn_article', methods=['GET'])
def random_cnn_article():
    try:
        
        articles = rthknews.get_rthk_tokenized_news()
        article = random.choice(articles)

        return jsonify({'result': article}), 200
        
    except Exception as e:
        print(f"Error fetching CNN article: {str(e)}")
        return jsonify({'error': str(e)}), 500

class SimpleQueue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        """Add an item to the end of the queue"""
        self.items.append(item)
    
    def dequeue(self):
        """Remove and return the item at the front of the queue"""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def peek(self):
        """Return the item at the front of the queue without removing it"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Return the number of items in the queue"""
        return len(self.items)
    
    def clear(self):
        """Remove all items from the queue"""
        self.items = []

@app.route('/queue/create', methods=['POST'])
def create_queue():
    """Create a new queue and return its ID"""
    queue_id = str(uuid.uuid4())
    sessions[queue_id] = SimpleQueue()
    return jsonify({"queue_id": queue_id})

@app.route('/queue/enqueue', methods=['POST'])
def queue_enqueue():
    """Add an item to a queue"""
    data = request.json
    queue_id = data.get('queue_id')
    item = data.get('item')
    
    if not queue_id or not item or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID or item"}), 400
    
    sessions[queue_id].enqueue(item)
    return jsonify({"status": "Item added to queue"})

@app.route('/queue/dequeue', methods=['POST'])
def queue_dequeue():
    """Remove and return the first item from a queue"""
    data = request.json
    queue_id = data.get('queue_id')
    
    if not queue_id or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID"}), 400
    
    item = sessions[queue_id].dequeue()
    if item is None:
        return jsonify({"error": "Queue is empty"}), 404
    
    return jsonify({"item": item})

@app.route('/queue/peek', methods=['POST'])
def queue_peek():
    """Return the first item from a queue without removing it"""
    data = request.json
    queue_id = data.get('queue_id')
    
    if not queue_id or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID"}), 400
    
    item = sessions[queue_id].peek()
    if item is None:
        return jsonify({"error": "Queue is empty"}), 404
    
    return jsonify({"item": item})

@app.route('/queue/size', methods=['POST'])
def queue_size():
    """Return the number of items in a queue"""
    data = request.json
    queue_id = data.get('queue_id')
    
    if not queue_id or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID"}), 400
    
    size = sessions[queue_id].size()
    return jsonify({"size": size})


global_message = SimpleQueue()

#all messages are in json and this format:
#{
   #messageid:id
   #type:id
   #sender:id
   #data - a type dependent structure
#}

"""
function postMessage(messageId, type, sender, data) {
    return fetch('/message/post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            messageid: messageId,
            type: type,
            sender: sender,
            data: data
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .catch(error => {
        console.error('Error posting message:', error);
        throw error;
    });
}
"""
#
#
#
#

@app.route('/feed_back_prompt', methods=['POST'])
def feed_back_prompt():
    prompttemplate = "write a llm prompt based upon learning data that can be used to drive a language learning discussion. Try to cover both grammarm vocab and set expressions. The language is Cantonese and the discussion should be in Cantonese as well."
    data = request.json
    # Read the feedback data from file
    try:
        with open('/var/www/html/mp3/feedback.txt', 'r', encoding='utf-8') as f:
            feedback_data = f.read()
            print(feedback_data)
        # Delete the file after reading
        os.remove('/var/www/html/mp3/feedback.txt')
        api = openrouter.OpenRouterAPI()
        prompt = prompttemplate + "\n\nHere's the recent feedback data:\n" + feedback_data
        result = api.open_router_claude_4_0_sonnet("You are a language learning system design expert, specializing in Cantonese.", prompt)
        print(result)
        systemprompt = api.open_router_nova_lite_v1("Write a system prompt suitable for this prompt:" + result )
        #systemprompt = "You are a cantonese language teaching expert."
        print(systemprompt)
        return jsonify({"result": {"system_prompt":systemprompt,"prompt":result}}), 200
    except FileNotFoundError:
        return jsonify({"error": "Feedback data not found"}), 404
    except Exception as e:
        print(f"Error processing feedback: {str(e)}")
        return jsonify({"error": str(e)}), 500

def handle_feedback(message):
    """Handle feedback messages"""
    # Log the feedback message to a file
    with open('/var/www/html/mp3/feedback.txt', 'a', encoding='utf-8') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {json.dumps(message, ensure_ascii=False)}\n")
    
    # Here you can process the feedback message as needed
    print(f"Feedback received: {message}")

global_message_listeners = {}
global_message_listeners['feedback'] = handle_feedback
        

@app.route('/message/post', methods=['POST'])
def post_message():
    """Add a message to the global message queue"""
    try:
        data = request.json
        if data['type'] in global_message_listeners:
            global_message_listeners[data['type']](data['data'])
            return jsonify({"status": "Message queued successfully"}), 200
        # Validate required fields
        required_fields = ['messageid', 'type', 'sender', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add message to the global queue
        global_message.enqueue(json.dumps(data))
        
        return jsonify({"status": "Message queued successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

import time

import srtdb_search




import os

with open('/var/www/html/api/rfbackend/routerkey.txt', 'r') as f:
    os.environ['OPENROUTER_API_KEY'] = f.readline().strip()


def handle_job(job_data):
    """Process a job"""
    print(f"Processing job: {job_data}")
    time.sleep(5)  # Simulate a long-running job
    if job_data['type'] == 'simple_srt_search':
        print("doing a simple search over srt " + str(job_data['keywords']))
        returned_list = srtdb_search.search_srt_files(keywords=job_data['keywords'])
        print(str(returned_list))
        global_message.enqueue(json.dumps({"type": "job_completed", "data": job_data, "result": returned_list}))
        return

    if job_data['type'] == 'pattern_srt_search':
        print("doing a simple search over srt " + str(job_data['keywords']) + ' ' + job_data['pattern'])
        pattern = job_data['pattern']
        returned_list = srtdb_search.search_srt_files(keywords=job_data['keywords'],pattern=pattern)
        print(str(returned_list))
        global_message.enqueue(json.dumps({"type": "job_completed", "data": job_data, "result": returned_list}))
        return

    global_message.enqueue(json.dumps({"type": "job_completed", "data": job_data, "result": "unknown command"}))
    print(f"Job completed: {job_data}")
    

@app.route('/jobs/add', methods=['POST'])
def jobs_add():
    try:
        data = request.json['jobdata']
        scheduler.add_job( args=[data], func=handle_job,trigger='date',id=str(random.randint(0,1000)) )
        return jsonify({"status": "job place"}, 200)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


import regex

def longest_chinese_substring(s):
    # Match only sequences of valid Chinese characters (Unicode general category "Lo")
    chinese_segments = regex.findall(r'[\p{Lo}]+', s)
    
    # If no Chinese characters found, return an empty string
    if not chinese_segments:
        return ""
    
    # Find the longest segment
    longest_segment = max(chinese_segments, key=len)
    
    return longest_segment

@app.route('/get_search_term', methods=['POST'])
def get_search_term():
    try:
        pattern = request.json['pattern']
        msg = """
    Given a string in Cantonese describing a grammatical pattern or fixed expression with variable components such as ellipses ..., placeholders like [X], or other markers, split the string into segments separated by variable parts. Then, extract the longest contiguous fixed substring from these segments. If there are multiple fixed parts, choose the one with the most characters. 
    Reply with only the chosen substring, nothing more.
    Here is the string describing the grammar pattern: """+ pattern +"""
    """
        system_msg = "You are a language processing expert,helping analysing and preprosessing language tasks"
        #openpapi = openrouter.OpenRouterAPI()
        #presearch = openpapi.open_router_qwen_turbo(system_msg,msg)
        #print("We got a keyword " + presearch)
        
        presearch = longest_chinese_substring(pattern)
        
        return jsonify({"result":presearch  }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stream')
def stream():
    def event_stream():
        empty_count = 0
        while True:
            # Wait for a message to be available in the global queue
            message = global_message.dequeue()
            
            # If we got a message, yield it in SSE format
            if message:
                yield f"data: {message}\n\n"
            else:
            # No message available yet, wait a bit before checking again
                time.sleep(0.5)
                empty_count += 1
                if empty_count > 60:  # If no messages for a while, ping
                    empty_count = 0                    
                    yield "data: {\"type\":\"ping\"}\n\n"

    # 3. Return a streaming response with the correct mimetype
    return Response(event_stream(), mimetype='text/event-stream')



