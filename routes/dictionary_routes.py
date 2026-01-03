"""Dictionary-related routes blueprint"""
import api
import database
import constants
from flask import Blueprint, request, jsonify

bp = Blueprint('dictionary', __name__, url_prefix='')


@bp.route('/dictionarylookup', methods=['POST'])
def dictionarylookup():
    data = request.json
    word = data.get(constants.PARAMETER_SEARCH_WORD)
    result = api.dictionary_lookup(word)
    return jsonify({'result': result})


@bp.route('/reactorlookup', methods=['GET'])
def reactorlookup():
    term = request.args.get('q')
    result = api.dictionary_lookup(term)
    return str(result)


@bp.route('/update_dictionary', methods=['POST'])
def update_dictionary():
    data = request.json
    term = data.get(constants.PARAMETER_TERM)
    jyutping = data.get(constants.PARAMETER_JYUTPING)
    definition = data.get(constants.PARAMETER_DEFINITION)
    database.update_dictionary(term, jyutping, definition)
    return jsonify({'result': 'ok'})


@bp.route('/get_dictionary_value', methods=['POST'])
def get_dictionary_value():
    word = request.json['word']
    language = request.json.get('language', 'cantonese')
    
    if language == 'cantonese':
        result = database.get_cantonese_dictionary(word)
    else:
        result = database.get_dictionary(word)
    
    return jsonify({'result': result})


@bp.route('/set_dictionary_value', methods=['POST'])
def set_dictionary_value():
    word = request.json['word']
    data = request.json['data']
    language = request.json.get('language', 'cantonese')
    
    if language == 'cantonese':
        database.set_cantonese_dictionary(word, data)
    else:
        database.set_dictionary(word, data)
    
    return jsonify({'result': 'ok'})


@bp.route('/download_dictionary', methods=['POST'])
def download_dictionary():
    word = request.json['word']
    result = api.download_dictionary_word(word)
    if result:
        return jsonify({'result': 'success', 'data': result})
    else:
        return jsonify({'result': 'not_found'})


@bp.route('/upload_dictionary', methods=['POST'])
def upload_dictionary():
    entries = request.json['entries']
    for entry in entries:
        word = entry['word']
        definition = entry['definition']
        jyutping = entry.get('jyutping', '')
        database.update_dictionary(word, jyutping, definition)
    
    return jsonify({'result': 'success', 'count': len(entries)})