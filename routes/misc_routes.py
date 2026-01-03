"""Miscellaneous routes blueprint - contains various specialized endpoints"""
import os
import json
import random
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib.parse
import textprocessing
import database
import api
import log
import constants
import newscrawler
import poe
import homecommand
import config
import stockmanager
import dbconfig
import MessageAnnouncer
from threading import Thread
from flask import Blueprint, request, jsonify, Response

bp = Blueprint('misc', __name__, url_prefix='')


@bp.route('/lookupposition', methods=['POST'])
def lookupposition():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    position = data.get(constants.PARAMETER_POSITION)
    ret = api.lookup_position(cwsid, position)
    return jsonify({'result': ret})


@bp.route('/get_cws_vocabulary', methods=['POST'])
def get_cws_vocabulary():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    result = api.get_complete_vocab_from_cws(cwsid)    
    return jsonify({'result': result})


@bp.route("/get_a_problem_text", methods=["POST"])
def get_a_problem_text():
    result = api.get_random_verify()
    return jsonify({'result': result})


@bp.route('/post_random_pleco', methods=['POST'])
def post_random_pleco():
    question = request.form.get('pleco')
    database.update_pleco(question)
    return "OK"


@bp.route('/generate_text', methods=['POST'])
def generate_text():
    text = request.json['text']
    api.create_generative_text(text)
    return "OK"


@bp.route('/simplifycws', methods=['POST'])
def simplifycws():
    cwsid = request.json['cwsid']
    batchprocessing.simplify_cws(cwsid)
    return "OK"


@bp.route('/set_ai_auth', methods=['GET'])
def set_ai_auth():
    args = request.args
    auth_part = args.get('auth_part')
    with open('/var/www/html/api/rfbackend/auth_part.txt', 'w') as f:
        f.write(auth_part)
        print("written auth_part" + auth_part)
    return jsonify({'result': 'ok'})


@bp.route('/set_stored_value', methods=['POST'])
def set_stored_value():
    value = request.json['value']
    storage = request.json['storage']  
    key = request.json['key']  
    api.write_value_to_dictionary_file(storage, key, value)
    return jsonify({'result': 'ok'})


@bp.route('/get_stored_value', methods=['POST'])
def get_stored_value():
    storage = request.json['storage']  
    key = request.json['key']
    value = api.read_value_from_dictionary_file(storage, key)
    print("stored value gotten from server: " + str(value))
    return jsonify({'result': value})


@bp.route('/get_word_list', methods=['POST'])
def get_word_list():
    cwsid = request.json['cwsid']
    cwsret = api.get_word_list_from_cws(cwsid)
    return jsonify({'result': cwsret})
   

@bp.route('/add_look_up', methods=['POST'])
def add_look_up():
    cwsid = request.json['cwsid']
    term = request.json['term']
    database.add_look_up(term, cwsid)
    return jsonify({'result': 'ok'})


@bp.route('/get_look_up_history', methods=['POST'])
def get_look_up_history():
    cwsid = request.json['cwsid']
    lookups = database.lookup_history(cwsid)
    return jsonify({'result': lookups})


@bp.route('/get_classification', methods=['POST'])
def get_classification():
    cwsid = request.json['cwsid']
    cws = api.get_cws_text(cwsid)    
    classdict = textprocessing.get_word_class(cws.orgtext)
    return jsonify({'result': classdict})


@bp.route('/getmemorystory', methods=['POST'])
def getmemorystory():
    try:
        character = request.json['character']
        print(str(character))
        page = requests.get("https://rtega.be/chmn/index.php?c=" + urllib.parse.quote_plus(character) + "&Submit=")
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all(id="chmn")
        print(results[1].text)
        return jsonify({'result': results[1].text})
    except Exception as e:
        print(str(e))
        return jsonify({'result': None})


@bp.route('/publishfile', methods=['POST'])
def publishfile():
    try:
        content = request.json['content']
        filename = request.json['filename']
        f = open('/var/www/html/scene/' + filename, "w", encoding='utf-8')
        f.write(content)
        f.close()
        return jsonify({'result': 'ok'})    
    except Exception as e:
        print(str(e))
        return jsonify({'result': None})


@bp.route('/removefile', methods=['POST'])
def removefile():
    try:
        filename = request.json['filename']
        os.remove('/var/www/html/scene/' + filename)
        return jsonify({'result': 'ok'})    
    except Exception as e:
        print(str(e))
        return jsonify({'result': None})


@bp.route('/grammartest', methods=['POST'])
def grammartest():
    cwsid = request.json['cwsid']
    start = request.json['start']
    end = request.json['end']
    thecws = api.get_cws_text(cwsid)
    thetext = thecws.orgtext[start:end]
    result = poe.ask_poe_ai_sync("Split this text into sentences and explain the grammar of each:" + thetext)
    cws = api.process_chinese("grammartest", "ai", result, 500, cwsid)
    return jsonify({'result': cws})


@bp.route('/testvocabulary', methods=['POST'])
def testvocabulary():
    cwsid = request.json['cwsid']
    start = request.json['start']
    end = request.json['end']
    thecws = api.get_cws_text(cwsid)
    thetext = thecws.orgtext[start:end]
    result = poe.ask_poe_ai_sync("Make a vocabulary test based upon this text:" + thetext)
    cws = api.process_chinese("testvocabulary", "ai", result, 500, cwsid)
    return jsonify({'result': cws})


@bp.route('/testunderstanding', methods=['POST'])
def testunderstanding():
    cwsid = request.json['cwsid']
    start = request.json['start']
    end = request.json['end']
    thecws = api.get_cws_text(cwsid)
    thetext = thecws.orgtext[start:end]
    result = poe.ask_poe_ai_sync("Make a list of question to check my understanding of this text:" + thetext)
    cws = api.process_chinese("testunderstanding", "ai", result, 500, cwsid)
    return jsonify({'result': cws})


@bp.route('/news', methods=['POST'])
def news():
    thenews = newscrawler.gethknews()
    cws = api.process_chinese("news", "ai", thenews, 500, -1)
    return jsonify({'result': cws})


@bp.route('/post_random_ai_response', methods=['POST'])
def post_random_ai_response():
    question = request.form.get('question')
    airesponse = request.form.get('airesponse')
    log.log("post_random_ai_response " + question)
    log.log("post_random_ai_response got response " + airesponse) 
    completeresponsetext = question + "\n\n" + airesponse  
    responsecws = api.process_chinese("", "", completeresponsetext, -1, -1)     
    log.log("found responsecws for question " + str(responsecws))
    ret = api.unanswered_questions()
    for r in ret:
        if r.question == question:
            log.log("found a question" + str(r.id))
            database.answer_ai_response(r.id, responsecws.id)
    return "OK"


@bp.route('/commandstream', methods=['GET'])
def commandstream():
    """Server-sent events endpoint for commands"""
    def generate():
        while True:
            # This would typically read from a queue or database
            # Placeholder implementation
            yield "data: ping\n\n"
    
    return Response(generate(), mimetype='text/plain')


@bp.route('/executehomecommand', methods=['POST'])
def executehomecommand():
    command = request.json['command']
    directory = request.json['directory']
    secret = config.get_config_value('HOMECOMMANDSECRET')
    if command.find(secret) == -1:
        return jsonify({'result': 'error'})
    command = command.replace(secret, '')
    homecommand.run_command_on_remote(command, directory)
    return jsonify({'result': 'ok'})


@bp.route('/stockupdate', methods=['POST'])
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
        f = open('/var/www/html/mp3/stocks.html', 'w')
        f.write(ret)
        f.close()
        stmgr.close()
        return jsonify({'result': 'ok'})
    except Exception as e:
        print(str(e))
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/getfailedreadingtests', methods=['POST'])
def getfailedreadingtests():
    try:
        days = request.json['days']
        result = database.get_failed_reading_tests(days)
        return jsonify({'result': result})
    except Exception as e:
        print(str(e))
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/tokenize_chinese', methods=['POST'])
def tokenize_chinese():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input. "text" parameter is required.'}), 400
    text = data['text']
    text = textprocessing.make_sure_traditional(text)
    tokens = textprocessing.split_text(text)
    return jsonify({'result': tokens})


@bp.route('/videosegment', methods=['POST'])
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


# Add more routes as needed...
# Note: This is a large collection of diverse endpoints that would benefit from 
# further categorization in a real refactoring effort