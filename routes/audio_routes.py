"""Audio-related routes blueprint"""
import os
import json
import subprocess
import textprocessing
import database
import cachemanagement
from flask import Blueprint, request, jsonify, send_file

bp = Blueprint('audio', __name__, url_prefix='')


def get_random_file(directory):
    """Get random file from directory"""
    files = os.listdir(directory)
    if not files:
        return None
    return os.path.join(directory, files[0])  # Placeholder implementation


def pick_random_file(directory, filter_type, extension):
    """Pick random file with filters"""
    # Placeholder implementation - needs actual logic
    files = [f for f in os.listdir(directory) if f.endswith('.' + extension)]
    if not files:
        return None
    return files[0]


def pick_random_artice_file(directory, extension):
    """Pick random article file"""
    # Placeholder implementation - needs actual logic
    files = [f for f in os.listdir(directory) if f.endswith('.' + extension)]
    if not files:
        return None
    return files[0]


def read_audio_time():
    """Read audio time from file"""
    try:
        f = open('/var/www/html/scene/audiotime.txt', "r", encoding='utf-8')
        js = f.read()
        f.close()
        jsonload = json.loads(js)
        thetime = jsonload['totaltime']
        return thetime
    except:
        return 0
    

def write_audio_time(totaltime):
    """Write audio time to file"""
    f = open('/var/www/html/scene/audiotime.txt', "w", encoding='utf-8')
    db = {'totaltime': totaltime}
    f.write(json.dumps(db))
    f.close()


@bp.route('/audioexample', methods=['GET'])
def get_audio():
    # Path to the MP3 file
    mp3_file = get_random_file('/var/www/html/mp3')
    # Return the MP3 file
    return send_file(mp3_file, mimetype='audio/mpeg')


@bp.route('/audioexample2', methods=['GET', 'POST'])
def get_audio2():
    # Path to the MP3 file
    mp3_file = pick_random_file('/var/www/html/mp3', 'total', 'mp3')
    # Return the MP3 file
    hint_file = mp3_file + '.hint.json'
    if os.path.exists('/var/www/html/mp3/' + hint_file):
        f = open('/var/www/html/mp3/' + hint_file, 'r', encoding='utf-8')
        chitext = f.read()
        f.close()        
        chiret = json.loads(chitext)
        chiba = []
        for c in chiret:
            chiba.append(textprocessing.split_text(c))
        chiret = chiba
    else:
        chiret = ['no', 'chinese', 'to', '\n', 'be', 'found', '!', hint_file]
    
    time_file = mp3_file + '.times.json'
    if os.path.exists('/var/www/html/mp3/' + time_file):
        f = open('/var/www/html/mp3/' + time_file, 'r', encoding='utf-8')
        timetext = f.read()
        f.close()
        timetext = json.loads(timetext)            
    else:
        timetext = None
    return jsonify({'result': {'filepath': mp3_file, 'tokens': chiret, 'times': timetext}})


@bp.route('/audioexample3', methods=['GET', 'POST'])
def get_audio3():
    # Path to the MP3 file
    mp3_file = pick_random_artice_file('/var/www/html/mp3', 'mp3')
    # Return the MP3 file
    hint_file = mp3_file + '.hint.json'
    if os.path.exists('/var/www/html/mp3/' + hint_file):
        f = open('/var/www/html/mp3/' + hint_file, 'r', encoding='utf-8')
        chitext = f.read()
        f.close()
        chiret = json.loads(chitext)
    else:
        chiret = ['no', 'chinese', 'to', '\n', 'be', 'found', '!']    
    return jsonify({'result': {'filepath': mp3_file, 'tokens': chiret}})


@bp.route('/remove_audio', methods=['POST'])
def remove_audio():
    # Path to the MP3 file
    mp3_file = request.json['audiofile']
    basename = os.path.basename(mp3_file)
    os.unlink('/var/www/html/mp3/' + mp3_file)
    os.unlink('/opt/watchit/' + basename + ".webm")
    return jsonify({'result': 'ok'})


@bp.route('/addaudiotime', methods=['POST'])
def addaudiotime():
    amount = request.json['amount']
    # try to read added time
    totaltime = read_audio_time()
    totaltime += amount
    write_audio_time(totaltime)
    return jsonify({'result': totaltime})
    

@bp.route('/addoutputexercise', methods=['POST'])
def addoutputexercise():
    english = request.json['english']
    chinesetokens = request.json['chinesetokens']
    if len(chinesetokens) < 2:
        chinesetokens = textprocessing.split_text(chinesetokens[0])
        chinesetokens = json.dumps(chinesetokens)
    mp3name = request.json['mp3name']
    type = request.json['type']
    result = request.json['result']
    milliseconds = request.json['milliseconds']
    whenutcmilliseconds = request.json['whenutcmilliseconds']
    database.add_output_exercise(english, chinesetokens, mp3name, type, result, milliseconds, whenutcmilliseconds)
    return jsonify({'result': 'ok'})


@bp.route('/addlisteningexercise', methods=['POST'])
def addlisteningexercise():
    sentence = request.json['sentence']
    chinesetokens = request.json['tokens']
    if len(chinesetokens) < 2:
        chinesetokens = textprocessing.split_text(chinesetokens[0])
    result = request.json['result']
    database.add_listening_sentence(sentence, chinesetokens, result)
    return jsonify({'result': 'ok'})


@bp.route('/gettotalaudiotime', methods=['POST'])
def gettotalaudiotime():
    total = database.get_total_audio_time()
    return jsonify({'result': total})


@bp.route('/gettotaloutputtime', methods=['POST'])
def gettotaloutputtime():
    total = database.get_total_output_time()
    return jsonify({'result': total})