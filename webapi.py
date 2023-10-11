import time
import traceback
from flask import Flask, Response, jsonify, request, url_for

import api
import log
import constants
import database
import os
import os.path

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
            def generate_events():
                count = 0
                while count < 3:
                    if count == 0:
                        yield 'event: meta\ndata: {"content_type": "text/markdown", "linkify": true}\n\n'
                    if count == 1:
                        yield 'event: text\ndata: {"text": "I am here"}\n\n'
                    if count == 2:
                        yield 'event: done\ndata: {}\n\n'
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
