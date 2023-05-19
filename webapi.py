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

@app.route('/version', methods=['GET'])
def version():
    return jsonify({'version':'0.1'})

@app.route('/version', methods=['POST'])
def pversion():
    return jsonify({'version':'0.1'})

@app.route('/add_text',method=['POST'])
def add_text():
    print("add text called")
    log.log("/add_text called")
    data = request.json()
    title       = data.get(PARAMETER_TEXT_TITLE)
    type        = data.get(PARAMETER_TEXT_TYPE)    
    body        = data.get(PARAMETER_TEXT_BODY)
    parentcwsid = data.get(PARAMETER_PARENT_CWSID)    
    source      = data.get(PARAMETER_TEXT_SOURCE)
    cws         = api.process_chinese(title, source, body, type,parentcwsid)
    return jsonify({'result':cws})

    #