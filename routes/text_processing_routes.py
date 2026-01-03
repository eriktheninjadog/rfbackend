"""Text processing routes blueprint"""
import api
import log
import constants
import database
import os
import boto3
import pycld2 as cld2
import zhconv
from textwrap import wrap
from flask import Blueprint, request, jsonify

bp = Blueprint('text_processing', __name__, url_prefix='')


@bp.route('/addtext', methods=['POST'])
def addtext():
    print("add text called")
    log.log("/addtext called")
    data = request.json
    log.log("/addtext data gotten")
    title = data.get(constants.PARAMETER_TEXT_TITLE)
    type = constants.CWS_TYPE_IMPORT_TEXT
    body = data.get(constants.PARAMETER_TEXT_BODY)
    parentcwsid = data.get(constants.PARAMETER_PARENT_CWSID)    
    source = data.get(constants.PARAMETER_TEXT_SOURCE)
    log.log(" cld2.detect(body) called ")
    isReliable, textBytesFound, details = cld2.detect(body) 
    print(str(details))
    if details[0][1] == "en":
        os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
        print("Translate To chinese")
        translate = boto3.client(service_name='translate', region_name='ap-southeast-1', use_ssl=True)
        finaltext = ""
        bits = wrap(body, 9000)
        for bit in bits:
            english_text = bit.replace("\n", "_")
            result = translate.translate_text(Text=english_text,
            SourceLanguageCode="en", TargetLanguageCode="zh-TW")
            finaltext = finaltext + result.get('TranslatedText').replace("_", "\n")
        body = finaltext
        print("Translation " + body)        
    cws = api.process_chinese(title, source, body, type, parentcwsid)
    log.log(" add text - text processed ")
    return jsonify({'result': cws})


@bp.route('/getcws', methods=['POST'])
def getcws():
    data = request.json
    cwsid = data.get(constants.PARAMETER_CWSID)
    ret = api.get_cws_text(cwsid)
    return jsonify({'result': ret})


@bp.route('/updatecws', methods=['POST'])
def updatecws():
    cwsid = request.json['cwsid']
    text = request.json['text']
    api.update_cws(cwsid, text)
    return jsonify({'result': 'ok'})


@bp.route('/deletecws', methods=['POST'])
def deletecws():
    cwsid = request.json['cwsid']
    api.deletecwsbyid(cwsid)
    return jsonify({'result': 'ok'})


@bp.route('/changecwsstatus', methods=['POST'])
def changecwsstatus():
    cwsid = request.json['cwsid']
    status = request.json['status']
    api.changecwsstatusbyid(cwsid, status)
    return jsonify({'result': 'ok'})


@bp.route('/getimportedtexts', methods=['POST'])
def getimportedtexts():
    ret = api.get_imported_texts()
    return jsonify({'result': ret})


@bp.route('/get_character_cws', methods=['POST'])
def get_character_cws():
    title = request.json['title']
    cws = database.get_cws_by_title_and_type(title, 800)  
    return jsonify({'result': cws})