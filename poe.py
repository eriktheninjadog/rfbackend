import ssl
import sys
import socket


import asyncio
import contextlib
import json
import warnings
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, cast

import httpx
import httpx_sse


import time
poesocket = None


def create_and_connect_poe_socket():
    context = ssl.create_default_context()    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock = context.wrap_socket(sock, server_hostname='api.poe.com')  
    ssock.connect(('api.poe.com', 443))
    return ssock

def create_query(question):
    query = json.loads("""{
      "role": "bot",
      "content": "What is 6 + 4?",
      "content_type": "text/markdown",
      "timestamp": 0,
      "message_id": "",
      "feedback": [],
      "attachments": []
    }""")
    query['content'] = question
    return query

past_queries = []
lastquerytime = time.time()

def ask_poe_ai_sync(question,bot):

    path = "/bot/"+bot
    hostname = 'api.poe.com'
    flog = open('/var/www/html/api/rfbackend/aisocket-'+str(int(time.time()))+'.log','wb')
    body = """{
  "version": "1.0",
  "type": "query",
  "query": [
    {
      "role": "bot",
      "content": "What is 6 + 4?",
      "content_type": "text/markdown",
      "timestamp": 0,
      "message_id": "",
      "feedback": [],
      "attachments": []
    }
  ],
  "user_id": "",
  "conversation_id": "",
  "message_id": "",
  "metadata": "",
  "api_key": "<missing>",
  "access_key": "<missing>",
  "temperature": 0.7,
  "skip_system_prompt": false,
  "logit_bias": {},
  "stop_sequences": []
}"""

    global poesocket
    global past_queries

    if (time.time()-lastquerytime ) > 3600:
        poesocket = None
        past_queries = []

    bodyasdict = json.loads(body)
    past_queries.append(create_query(question))
    bodyasdict['query'] = past_queries
    body = json.dumps(bodyasdict)
#   "{'version': '1.0', 'type': 'query', 'query': [{'role': 'user', 'content': 'What is 6 + 4?', 'content_type': 'text/markdown', 'timestamp': 0, 'message_id': '', 'feedback': [], 'attachments': []}], 'user_id': '', 'conversation_id': '', 'message_id': '', 'metadata': '', 'api_key': '<missing>', 'access_key': '<missing>', 'temperature': 0.7, 'skip_system_prompt': False, 'logit_bias': {}, 'stop_sequences': []}"    
    if poesocket == None:
        poesocket = create_and_connect_poe_socket()
    ssock = poesocket
    request = f"POST {path} HTTP/1.1\r\n" \
            f"Host: {hostname} \r\n" \
            f"Authorization: Bearer BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk \r\n" \
            f"Accept-Encoding: gzip, deflate, br\r\n" \
            f"User-Agent: python-httpx/0.25.0 \r\n" \
            f"Content-Type: application/json \r\n" \
            f"Accept: text/event-stream \r\n" \
            f"Content-Type: application/json \r\n" \
            f"Cache-Control: no-store \r\n" \
            f"Connection: keep-alive\r\n" \
            f"Content-Length: {len(body)}\r\n\r\n" \
            f"{body}"
    #print(request)
    response = b""
    keepgoing = True
    firstgotten = False
    wholenineyards = ""
    try:
        ssock.sendall(request.encode())
        total = ""
        while keepgoing:
            chunk = ssock.recv(4096*2)
            flog.write(chunk)
            flog.flush()
            if not chunk:
                break
            response += chunk
            print(chunk.decode())
            if not firstgotten:
                print("first chunk")
                firstgotten = True
                athing = chunk.decode()
                parts = athing.split("\r\n\r\n")
                if (len(parts)>1 and len(parts[1])>20):
                    chunkstart = athing.find("\r\n\r\n")
                    athing = parts[1]
                    length = int(athing.split("\r\n")[0],16)
                    start = athing.find("\r\n")
                    wholenineyards += chunk[chunkstart+6+start:chunkstart+start+6+length].decode()
                    print(wholenineyards)
            else:
                #everything start with the length in hex followed by line and data:
                #is the data encoded, is it binary?
                athing = chunk.decode()
                try:
                    length = int(athing.split("\n")[0],16)
                    if (length == 0):
                        keepgoing = False
                        return None 
                    print(str(length))
                    start = athing.find("\r\n")
                #print(chunk[start+1:length+2].decode())
                #print("got package")
                    #print(chunk[start+2:start+2+length].decode().strip())
                    wholenineyards += chunk[start+2:start+2+length].decode().strip()
                except:
                    print("Something went wrong trying to parse int -->" + athing + "<--")
            if (chunk.decode().find("event: done")!=-1):
                keepgoing = False
            else:
                strpackage = chunk.decode()
    except Exception as e:
            print(str(e))
            exit(-1)
    finally:            
            #ssock.close()
            total = ""
            f = open("/var/www/html/api/rfbackend/storage/wholenineyards.txt","w")
            f.write(wholenineyards)
            f.close()
            wholenineyards = wholenineyards.replace("event: text\r\n","")
            wholenineyards = wholenineyards.replace("data: [DONE]","")
            wholenineyards = wholenineyards.replace("data:","\n")
            for i in wholenineyards.split("\n"):
                if (len(i.strip()) > 0):
                    #print("###" + i)
                    try:
                        pop = json.loads(i)
                        if ( 'text' in pop.keys() ):
                            total += pop['text']
                    except:
                        print("Could not json -->" + i + "<--")
            return total
