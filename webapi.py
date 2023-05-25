from flask import Flask, jsonify, request, url_for

import api
import log
import constants

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
    cws         = api.process_chinese(title, source, body, type,parentcwsid)
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
    api.create_ai_paragraphs_questions(cwsid,"Explain the meaning of this text using simple sentences in traditional chinese",4,lambda x:len(x)>20)
    api.create_ai_sentences_questions(cwsid,"Explain the grammar of this sentence",5,lambda x:len(x)>6)
    api.create_ai_sentences_questions(cwsid,"Explain the grammar of this text",6,lambda x:len(x)>6)
    return jsonify({'result':'success'})

@app.route('/dictionarylookup',methods=['POST'])
def dictionarylookup():
    data = request.json
    word = data.get(constants.PARAMETER_SEARCH_WORD)
    result = api.dictionary_looup(word)
    return jsonify({'result':result})

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
    fragment = data.get(constants.PARAMETER_TEXT_FRAGMENT)
    ret = api.direct_ai_question(cwsid,"Analyze this text:",fragment,constants.CWS_TYPE_DIRECT_AI_ANALYZE)
    return jsonify({'result':ret})

@app.route('/direct_ai_analyze_grammar',methods=['POST'])
def direct_ai_analyze_grammar():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    fragment = data.get(constants.PARAMETER_TEXT_FRAGMENT)
    ret = api.direct_ai_question(cwsid,"Analyze the grammar of this text:",fragment,constants.CWS_TYPE_DIRECT_AI_ANALYZE_GRAMMAR)
    return jsonify({'result':ret})

@app.route('/direct_ai_summarize',methods=['POST'])
def direct_ai_summarize():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    fragment = data.get(constants.PARAMETER_TEXT_FRAGMENT)
    ret = api.direct_ai_question(cwsid,"Summarize this text using traditional chinese:",fragment,constants.CWS_TYPE_DIRECT_AI_SUMMARIZE)
    return jsonify({'result':ret})

@app.route('/direct_ai_simplify',methods=['POST'])
def direct_ai_simplify():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    fragment = data.get(constants.PARAMETER_TEXT_FRAGMENT)
    ret = api.direct_ai_question(cwsid,"Rewrite this text in traditional chinese using simple words and sentences:",fragment,constants.CWS_TYPE_DIRECT_AI_SIMPLIFY)
    return jsonify({'result':ret})
