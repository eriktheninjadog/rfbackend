"""AI-related routes blueprint"""
import random
import api
import database
import constants
import aisocketapi
import batchprocessing
import zhconv
from flask import Blueprint, request, jsonify

bp = Blueprint('ai', __name__, url_prefix='')


@bp.route('/generatequestions', methods=['POST'])
def generatequestions():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    api.create_ai_paragraphs_questions(cwsid, "Explain the meaning of this text", 4, lambda x: len(x) > 20)
    api.create_ai_paragraphs_questions(cwsid, "Ask a few questions and answers (write answers in chinese) to make sure the reader understood this paragraph", 8, lambda x: len(x) > 30)
    api.create_ai_sentences_questions(cwsid, "Explain the grammar of this sentence", 5, lambda x: len(x) > 6)
    api.create_ai_parts_questions(cwsid, "Breakdown this text into its parts", 7, lambda x: len(x) > 4)
    return jsonify({'result': 'success'})


@bp.route('/answeraiquestion', methods=['POST'])
def answeraiquestion():
    data = request.json    
    aianswer = data.get(constants.PARAMETER_AI_ANSWER)
    questionid = data.get(constants.PARAMETER_QUESTION_ID)   
    print("aianswer:" + aianswer)
    print("questionid:" + str(questionid))
    api.answer_ai_question(questionid, aianswer)
    return jsonify({'result': 'ok'})


@bp.route('/unansweredquestions', methods=['POST'])
def unansweredquestions():
    ret = api.unanswered_questions()
    return jsonify({'result': ret})


@bp.route('/direct_ai_analyze', methods=['POST'])
def direct_ai_analyze():
    print('/direct_ai_analyze')
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)    
    ret = api.direct_ai_question(cwsid, "Analyze this text:", p1, p2, constants.CWS_TYPE_DIRECT_AI_ANALYZE)
    return jsonify({'result': ret})


@bp.route('/direct_ai_analyze_grammar', methods=['POST'])
def direct_ai_analyze_grammar():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid, "Analyze the grammar of this text:", p1, p2, constants.CWS_TYPE_DIRECT_AI_ANALYZE_GRAMMAR)
    return jsonify({'result': ret})


@bp.route('/direct_ai_summarize', methods=['POST'])
def direct_ai_summarize():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid, "Summarize this text using traditional chinese:", p1, p2, constants.CWS_TYPE_DIRECT_AI_SUMMARIZE)
    return jsonify({'result': ret})


@bp.route('/direct_ai_simplify', methods=['POST'])
def direct_ai_simplify():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid, "Rewrite this text in traditional chinese using simple words and sentences:", p1, p2, constants.CWS_TYPE_DIRECT_AI_SIMPLIFY)
    return jsonify({'result': ret})


@bp.route('/direct_ai_question', methods=['POST'])
def direct_ai_question():
    cwsid = request.json['cwsid']
    question = request.json['question']    
    start = request.json['start']
    end = request.json['end']
    thecws = api.get_cws_text(cwsid)
    thetext = thecws.orgtext[start:end]
    thequestion = question + " : " + thetext
    answer = aisocketapi.ask_ai(thequestion)
    answer = zhconv.convert(answer, 'zh-hk')
    cws = api.process_chinese("", "ai", thetext + "\n------\n" + answer, 500, cwsid)
    database.add_answered_ai_question(thequestion, 500, cwsid, start, end, cws.id)
    return jsonify({'result': cws})


@bp.route('/direct_ai_questions', methods=['POST'])
def direct_ai_questions():
    cwsid = request.json['cwsid']
    questions = request.json['questions']
    start = request.json['start']
    end = request.json['end']
    thecws = api.get_cws_text(cwsid)
    thetext = thecws.orgtext[start:end]
    simpcws = batchprocessing.multiple_ai_to_text(thetext, questions)
    return jsonify({'result': simpcws})


@bp.route('/get_random_ai_question', methods=['GET'])
def get_random_ai_question():
    ret = api.unanswered_questions()
    answer = random.choice(ret)    
    return str(answer.question)


@bp.route('/ai_simplify_cws', methods=['POST'])
def ai_simplify_cws():
    cwsid = request.json['cwsid']
    simpcws = batchprocessing.simplify_cws(cwsid)
    return jsonify({'result': simpcws})


@bp.route('/apply_ai', methods=['POST'])
def apply_ai():
    cwsid = request.json['cwsid']
    aitext = request.json['aitext']
    simpcws = batchprocessing.apply_ai_to_cws(cwsid, aitext)
    return jsonify({'result': simpcws})


@bp.route('/ai_summarize_random', methods=['POST'])
def ai_summarize_random():
    txt = aisocketapi.ask_ai("Generate an article of 500 words in traditional Chinese on a random topic. Follow it with  5 multiple choice questions to test the readers understanding.")
    cws = api.process_chinese(random, "", txt, constants.CWS_TYPE_IMPORT_TEXT, -1)
    return jsonify({'result': cws})


@bp.route('/explain_paragraph', methods=['POST'])
def explain_paragraph():
    paragraph = request.json['text']
    cwsid = request.json['cwsid']
    if len(paragraph) < 5:
        return "OK"
    # we want to find the start and end of the text
    thecws = database.get_cws_by_id(cwsid)
    if thecws == None:
        return "Couldn't find CWS " + str(cwsid)
    
    start = thecws.orgtext.find(paragraph)
    if start == -1:               
        return "OK"
    database.add_ai_question("Explain the meaning, structure and grammar of this text:" + paragraph.strip(), 66, cwsid,
                                start,
                                len(paragraph))
    database.add_ai_question("Write a few questions to check that the reader has understood this text:" + paragraph.strip(), constants.RESPONSE_TYPE_CHECK_QUESTION, cwsid,
                                start,
                                len(paragraph))
    return "OK"