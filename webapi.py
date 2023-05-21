from flask import Flask, jsonify, request, url_for

import api
import log

app = Flask(__name__)

PARAMETER_TEXT_BODY     = 'text'
PARAMETER_TEXT_TITLE    = 'title'
PARAMETER_TEXT_TYPE     = 'type'
PARAMETER_TEXT_SOURCE   = 'source'
PARAMETER_CWSID         = 'cwsid'
PARAMETER_PARENT_CWSID  = 'parentcwsid'
PARAMETER_POSITION      = 'position'
PARAMETER_AI_ANSWER     = 'aianswer'
PARAMETER_QUESTION_ID   = 'questionid'



@app.route('/version', methods=['GET','PUT'])
def version():
    return jsonify({'version':'0.1'})

@app.route('/addtext',methods=['POST'])
def addtext():
    print("add text called")
    log.log("/addtext called")
    data = request.json
    log.log("/addtext data gotten")
    title       = data.get(PARAMETER_TEXT_TITLE)
    type        = data.get(PARAMETER_TEXT_TYPE)    
    body        = data.get(PARAMETER_TEXT_BODY)
    parentcwsid = data.get(PARAMETER_PARENT_CWSID)    
    source      = data.get(PARAMETER_TEXT_SOURCE)
    cws         = api.process_chinese(title, source, body, type,parentcwsid)
    return jsonify({'result':cws})


@app.route('/lookupposition',methods=['POST'])
def lookupposition():
    data = request.json
    cwsid = data.get(PARAMETER_CWSID)
    position = data.get(PARAMETER_POSITION)
    ret = api.lookup_position(cwsid,position)
    return jsonify({'result':ret})



@app.route('/unansweredquestions',methods=['POST'])
def unansweredquestions():
    ret = api.unanswered_questions()
    return jsonify({'result':ret})


@app.route('/answeraiquestion',methods=['POST'])
def answeraiquestion():
    data = request.json
    aianswer = data.get(PARAMETER_AI_ANSWER)
    questionid = data.get(PARAMETER_QUESTION_ID)   
    print("aianswer:" + aianswer)
    print("questionid:" + questionid)
    api.answer_ai_question(questionid,aianswer)
    return jsonify({'result':'ok'})

@app.route('/generatequestions',methods=['POST'])
def generatequestions():
    data = request.json
    cwsid = data.get(PARAMETER_CWSID)
    api.create_ai_paragraphs_questions(cwsid,"Explain the meaning and structure of this text",4,lambda x:len(x)>20)
    api.create_ai_sentences_questions(cwsid,"Explain the grammar of this sentence",5,lambda x:len(x)>6)
    api.create_ai_sentences_questions(cwsid,"Explain the grammar of this text",6,lambda x:len(x)>6)
    return jsonify({'result':'success'})