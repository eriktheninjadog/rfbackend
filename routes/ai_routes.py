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
    """Analyze grammar using AI"""
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid, "Analyze the grammar of this text:", p1, p2, constants.CWS_TYPE_DIRECT_AI_ANALYZE_GRAMMAR)
    return jsonify({'result': ret})


@bp.route('/direct_ai_summarize', methods=['POST'])
def direct_ai_summarize():
    """Summarize text using AI"""
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid, "Summarize this text using traditional chinese:", p1, p2, constants.CWS_TYPE_DIRECT_AI_SUMMARIZE)
    return jsonify({'result': ret})


@bp.route('/direct_ai_simplify', methods=['POST'])
def direct_ai_simplify():
    """Simplify text using AI"""
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    p1 = data.get(constants.PARAMETER_POINT1)
    p2 = data.get(constants.PARAMETER_POINT2)
    ret = api.direct_ai_question(cwsid, "Rewrite this text in traditional chinese using simple words and sentences:", p1, p2, constants.CWS_TYPE_DIRECT_AI_SIMPLIFY)
    return jsonify({'result': ret})


@bp.route('/direct_ai_question', methods=['POST'])
def direct_ai_question():
    """Direct AI question on text segment"""
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
    """Multiple AI questions on text segment"""
    cwsid = request.json['cwsid']
    questions = request.json['questions']
    start = request.json['start']
    end = request.json['end']
    thecws = api.get_cws_text(cwsid)
    thetext = thecws.orgtext[start:end]
    simpcws = batchprocessing.multiple_ai_to_text(thetext, questions)
    return jsonify({'result': simpcws})


@bp.route('/ai_simplify_cws', methods=['POST'])
def ai_simplify_cws():
    """Simplify CWS text using AI"""
    cwsid = request.json['cwsid']
    simpcws = batchprocessing.simplify_cws(cwsid)
    return jsonify({'result': simpcws})


@bp.route('/apply_ai', methods=['POST'])
def apply_ai():
    """Apply AI processing to CWS text"""
    cwsid = request.json['cwsid']
    aitext = request.json['aitext']
    simpcws = batchprocessing.apply_ai_to_cws(cwsid, aitext)
    return jsonify({'result': simpcws})


@bp.route('/ai_summarize_random', methods=['POST'])
def ai_summarize_random():
    """Generate random article with AI"""
    txt = aisocketapi.ask_ai("Generate an article of 500 words in traditional Chinese on a random topic. Follow it with 5 multiple choice questions to test the readers understanding.")
    cws = api.process_chinese(random, "", txt, constants.CWS_TYPE_IMPORT_TEXT, -1)
    return jsonify({'result': cws})


@bp.route('/explain_paragraph', methods=['POST'])
def explain_paragraph():
    """Explain paragraph meaning and grammar"""
    paragraph = request.json['text']
    cwsid = request.json['cwsid']
    if len(paragraph) < 5:
        return jsonify({'result': 'OK'})
    
    # Find the start and end of the text
    thecws = database.get_cws_by_id(cwsid)
    if thecws is None:
        return jsonify({'error': f'Couldn\'t find CWS {cwsid}'}), 404
    
    start = thecws.orgtext.find(paragraph)
    if start == -1:
        return jsonify({'result': 'OK'})
    
    database.add_ai_question(f"Explain the meaning, structure and grammar of this text:{paragraph.strip()}", 
                           66, cwsid, start, len(paragraph))
    database.add_ai_question(f"Write a few questions to check that the reader has understood this text:{paragraph.strip()}", 
                           constants.RESPONSE_TYPE_CHECK_QUESTION, cwsid, start, len(paragraph))
    return jsonify({'result': 'OK'})


@bp.route('/explain_sentence_free', methods=['POST'])
def explain_sentence_free():
    """Explain sentence using free AI model"""
    try:        
        sentence = request.json['sentence']
        import openrouter
        api = openrouter.OpenRouterAPI()
        result = api.open_router_meta_llama_3_2_3b_free(f"Explain the words and grammar of this sentence: {sentence}")        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/explain_sentence_cheap', methods=['POST'])
def explain_sentence_cheap():
    """Explain sentence using cheap AI model"""
    try:        
        sentence = request.json['sentence']
        import openrouter
        aiapi = openrouter.OpenRouterAPI()
        result = aiapi.open_router_mistral_7b_instruct(f"Translate this sentence and return the answer in this json-format: {{\"translation\":english translation,\"words\":[[word1,definition in english],[word2,definition in english]] }}. Only return the json. {sentence}")
        end = result.find('}')
        result = result[:end+1]
        start = result.find('{')
        result = result[start:]
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/explain_sentence', methods=['POST'])
def explain_sentence():
    """Explain sentence using main AI model"""
    try:
        sentence = request.json['sentence']
        import openrouter
        import textprocessing
        api = openrouter.OpenRouterAPI()
        explain = api.open_router_qwen("你是粵語專家，分析文本。", f"解釋呢句嘅意思、詞彙同語法：{sentence}")
        result = textprocessing.split_text(explain)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/ai_anything', methods=['POST'])
def ai_anything():
    """Ask AI anything in Chinese"""
    try:
        question = request.json['question']
        import openrouter
        import textprocessing
        api = openrouter.OpenRouterAPI()
        question_in_chinese = api.open_router_qwen("你是粵語專家。", f"Translate this to traditional Chinese: {question}")
        explain = api.open_router_qwen("你是粵語專家。", question_in_chinese)
        result = textprocessing.split_text(explain)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})

