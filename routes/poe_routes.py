"""POE AI routes blueprint"""
import time
import json
import random
import poeclient
from flask import Blueprint, request, jsonify
from services.cache_service import get_examples_from_cache, pick_random_sentences_from_cache
from utils.poe_helpers import create_poe_example_question, newParsePoe
from utils.json_helpers import extract_json_array
import api
import cachemanagement
import database
import log

bp = Blueprint('poe', __name__, url_prefix='')

# Global robot state
robot = "Claude-3-Opus"


@bp.route('/poefree', methods=['POST'])
def poefree():
    cwsid = request.json['cwsid']
    text = request.json['text']
    bot = request.json['bot']
    clear = request.json['clear']
    global robot
    print("In poe free: robot = " + bot + " clear: " + str(clear))
    print("Robot is " + robot)    
    if bot != robot:
        print("We are switching to" + bot)
        poeclient.change_bot(bot)
        robot = bot
        time.sleep(12)
    result = poeclient.ask_ai(text, robot, clear)
    result = text + "\n\n" + result
    
    cws = api.process_chinese("pf:" + text[:25], "ai", result, 500, cwsid)
    return jsonify({'result': cws})


@bp.route('/poeexamples', methods=['POST'])
def poeexamples():
    global robot
    level = request.json['level']
    number = request.json['number']
    language = request.json['language']
    onlyFailed = request.json['onlyFailed']
        
    if onlyFailed == True:
        if not 'all' in request.json:    
            return get_failed_examples_duplicates(number, False)
        else:
            return get_failed_examples_duplicates(number, True)

    if not 'store' in request.json:
        examples = get_examples_from_cache()
        if examples != None:
           return jsonify({'result': examples}) 

    text = create_poe_example_question(level, number)
    
    if 'question' in request.json:
        text = request.json['question']
    
    bot = "Claude-3-Opus"
    if bot != robot:
        print("In the web api we are switching to Claude")
        poeclient.change_bot(bot)
        robot = bot
        time.sleep(12)
    result = poeclient.ask_ai(text, robot, False)
    with open('/tmp/output.txt', 'w', encoding='utf-8') as f:
        f.write(result)
        f.flush()
    aresult = extract_json_array(result)
    result = newParsePoe(aresult)
    if 'store' in request.json:
        cachemanagement.add_examples_to_cache(result)
    return jsonify({'result': result})


@bp.route('/poeexampleresult', methods=['POST'])
def poeexampleresult():
    print(request.get_json())
    database = []
    try:
        f = open('/var/www/html/scene/examplestest.txt', "r", encoding='utf-8')
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
    database.append({'tokens': tokens, 'chinese': chinese, 'english': english, 'level': level, 'success': success, 'reason': reason, 'time': currentTime})
    f = open('/var/www/html/scene/examplestest.txt', "w", encoding='utf-8')
    f.write(json.dumps(database))
    f.close()
    return jsonify({'result': 'ok'})


def get_failed_examples_duplicates(nr, all):
    """Get failed examples with duplicates handling"""
    if all == False:
        result = database.get_failed_outputs_lately(nr, random.randint(1, 2))
    else:
        result = database.get_failed_outputs_lately(nr, random.randint(1, 2))
    return jsonify({'result': result})