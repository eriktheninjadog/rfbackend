"""Dictionary-related routes blueprint"""
import api
import database
import constants
import persistentdict
import json
import openrouter
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


@bp.route('/set_dictionary_value', methods=['POST'])
def set_dictionary_value():
    """Set value in persistent dictionary"""
    try:
        dictname = request.json['dictionary']
        keyvalue = request.json['key']
        value = request.json['value']
        d = persistentdict.PersistentDict(dictname)
        d[keyvalue] = value
        return jsonify({'result': 'ok'})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/download_dictionary', methods=['POST'])
def download_dictionary():
    """Download entire dictionary data"""
    try:
        dictname = request.json['dictionary']
        d = persistentdict.PersistentDict(dictname)
        return jsonify({'result': d.get_raw_data()})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/upload_dictionary', methods=['POST'])
def upload_dictionary():
    """Upload dictionary data"""
    try:
        dictname = request.json['dictionary']
        values = request.json['values']
        d = persistentdict.PersistentDict(dictname)
        for i in values.keys():
            d[i] = values[i]
        return jsonify({'result': 'ok'})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})


@bp.route('/get_dictionary_value', methods=['POST'])
def get_dictionary_value():
    """Get value from persistent dictionary"""
    try:
        dictname = request.json['dictionary']
        keyvalue = request.json['key']
        d = persistentdict.PersistentDict(dictname)
        if keyvalue in d:
            return jsonify({'result': [keyvalue, d[keyvalue]]})
        else:
            return jsonify({'result': [keyvalue, None]})
    except Exception as e:
        return jsonify({'result': None, "reason": str(e)})
