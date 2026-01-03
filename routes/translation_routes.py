"""Translation routes blueprint"""
import os
import boto3
from textwrap import wrap
from flask import Blueprint, request, jsonify
from utils.text_helpers import remove_repeating_sentences
import poeclient
import time
import log
import api

bp = Blueprint('translation', __name__, url_prefix='')


@bp.route("/translatechinese", methods=["POST"])
def translatechinese():
    os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
    print("Translate To English")
    translate = boto3.client(service_name='translate', region_name='ap-southeast-1', use_ssl=True)
    finaltext = ""
    chinese_text = request.json['text']
    chinese_text = chinese_text.replace('\n', '_')
    bits = wrap(chinese_text, 9000)
    for bit in bits:
        english_text = bit
        result = translate.translate_text(Text=chinese_text,
            SourceLanguageCode="zh-TW", TargetLanguageCode="en")
        finaltext = finaltext + result.get('TranslatedText')
    return jsonify({'result': finaltext})


@bp.route('/cleanandtranslate', methods=['POST'])
def cleanandtranslate():
    robot = "Claude-instant-100k"
    log.log("cleanandtranslate")
    text = request.json['text']
    # first lets clean this up
    poeclient.change_bot('Claude-instant-100k')
    time.sleep(10)
    bettertext = remove_repeating_sentences(text)
    bettertext = bettertext.replace("\n", " ")
    bettertext = bettertext.replace("\r", " ")
    log.log("Better text recieved" + bettertext)
    cleantext = poeclient.ask_ai('Clean up this text: ' + bettertext, robot, False)
    log.log("Clean text recieved" + cleantext)
    poeclient.change_bot('GPT-4')
    time.sleep(10)        
    chinesecleantext = poeclient.ask_ai('Translate this text to Traditional Chinese ' + cleantext, robot, False)
    log.log("Chinese Clean text recieved" + chinesecleantext)
    cws = api.process_chinese("messytranslate", "ai", chinesecleantext, 500, -1)
    return jsonify({'result': 'ok'})