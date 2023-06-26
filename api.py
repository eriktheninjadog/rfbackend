from settings import settings
from dataobject import CWS
from dataobject import Fragment

import random
import textprocessing
import textsignature
import database
import articlecrawler
import json
import log
import constants
import requests


cachedir = '/tmp/'

from joblib import Memory
memory = Memory(cachedir, verbose=0)

def doopenapirequest(txt):
    url = "https://api.writesonic.com/v2/business/content/chatsonic?engine=premium"
    payload = {
        "enable_google_results": "true",
        "enable_memory": False,
        "input_text": txt
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": "2912a2d7-15a6-483a-9d43-5c66e34aa273"
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print(response.json())
    return  data['message']


#
def direct_ai_question(cwsid,question,p1,p2,type):
    cws = database.get_cws_by_id(cwsid)
    # now get the starting and end point of a fragment
    start = p1
    end = p2
    if (p2 < p1):
        start = p2
        end = p1
    # ok lets go 
    log.log('From here ' + cws.orgtext)
    
    fragment = cws.orgtext[start:end]
    response = doopenapirequest(question + ":" + fragment)
    # and the full response
    totalresponse = question + ":" + fragment + "\n" + response
    responsecws = process_chinese(question,"",totalresponse,type,cwsid)
    database.add_ai_question(question,type,cwsid,start,end)
    database.answer_ai_response(cwsid,responsecws.id)
    return responsecws

# step 1. Input chinese.
# This will create a cws and return it. it will set source and title

def process_chinese(title, source, text, type,parentid):
    # 
    # Try to find a cws
    text = textprocessing.make_sure_traditional(text)
    signature = textsignature.generate_signature(text)
    found = database.get_cws_by_signature(signature)
    if found != None:
        return found
    else:
        cwstext = textprocessing.split_text(text)
        cws = CWS(-1,None,text,cwstext,signature,"",title,source,type,parentid)
        id = database.add_cws(cws)
        return database.get_cws_by_id(id)

@memory.cache   
def get_cws_text(id):
    return database.get_cws_by_id(id)
    
def get_article(url):
    art = articlecrawler.getarticle(url)
    return process_chinese(art.title,url,art.title+"\n"+art.body,constants.CWS_TYPE_IMPORT_ARTICLE,-1)

def throw_away_CWS_from_article(art):
    splitted = textprocessing.split_text(art.title+"\n"+art.body)
    return CWS(-1,None,None,splitted,None,"",art.title,"reddit",constants.CWS_TYPE_THROWAWAY,-1)

# we do not save homes
def get_rthk_home():
    art = articlecrawler.getrthkhome()
    return throw_away_CWS_from_article(art)

def get_reddit_home():
    art = articlecrawler.getreddithome()
    return throw_away_CWS_from_article(art)

def get_reddit_home():
    art = articlecrawler.getreddithome()
    return throw_away_CWS_from_article(art)

def is_valid_part(part):
    ppart = part.strip()
    if (len(ppart.strip()) < 2):
        return False 
    return True

def create_api_question_on_cws(question,cwsid,segmentfunction,type,restriction):
    stored_cws = database.get_cws_by_id(cwsid)
    text_to_split = stored_cws.orgtext
    parts = segmentfunction(text_to_split)
    partsheadtails = textprocessing.find_start_end_of_parts(text_to_split,parts)
    for i in range(len(parts)):
            if is_valid_part(parts[i]) and restriction(parts[i].strip()):
                database.add_ai_question(question+":"+parts[i].strip(),type,cwsid,
                                partsheadtails[i][0],
                                partsheadtails[i][1])

#add
def create_and_store_fragments(cwsid,segmentfunction,type):
    stored_cws = database.get_cws_by_id(cwsid)
    text_to_split = stored_cws.orgtext
    parts = segmentfunction(text_to_split)
    partsheadtails = textprocessing.find_start_end_of_parts(text_to_split,parts)
    for i in range(len(parts)):
        p = parts[i].strip()
        if (len(p) > 2):
            fragmentcwsid = process_chinese('', '', p, constants.CWS_TYPE_FRAGMENT,cwsid)
            f = Fragment(cwsid,fragmentcwsid[0],partsheadtails[i][0],
                                partsheadtails[i][1],
                                type
                                )
            database.add_fragment(f)
    None

def create_and_store_all_fragments(cwsid):
    create_and_store_fragments(cwsid,textprocessing.split_text_parts,constants.FRAGMENT_TYPE_PART)
    create_and_store_fragments(cwsid,textprocessing.split_text_sentences,constants.FRAGMENT_TYPE_SENTENCE)
    create_and_store_fragments(cwsid,textprocessing.split_text_paragraphs,constants.FRAGMENT_TYPE_PARAGRAPH)

def create_ai_parts_questions(cwsid,question,type,restriction):
    create_api_question_on_cws(question,cwsid,textprocessing.split_text_parts,type,restriction)

def create_ai_sentences_questions(cwsid,question,type,restriction):
    create_api_question_on_cws(question,cwsid,textprocessing.split_text_sentences,type,restriction)

def create_ai_paragraphs_questions(cwsid,question,type,restriction):
    create_api_question_on_cws(question,cwsid,textprocessing.split_text_paragraphs,type,restriction)

def answer_ai_question(question_id,answer):
    cws = process_chinese("response", "response", answer, constants.CWS_TYPE_AI_RESPONSE,question_id)    
    database.answer_ai_response(question_id,cws.id)

#
# The position is in the real text, not in CWS
# This will return the following{
#   word: whatever word is hit with jyutping and definotion
#   responses: [
#       array with ai_response objects that has:
#       cwsid same as cwsid, responsecwsid is not null
#   ]
# }
#
# 

@memory.cache 
def lookup_position(cwsid,position):
    log.log("lookup_position("+str(cwsid)+","+ str(position)+")")
    #
    # so lets go for the cws
    #
    ret = []
    cws = database.get_cws_by_id(cwsid)
    log.log("get cws returned:" +str (cws))
    
    if (position > len(cws.orgtext)):
        return None
    if (position < 0):
        return None
    
    wordtext = ''
    # I will look up the character first
    achar = cws.orgtext[position]
    cd = database.find_word(''+achar)
    if cd != None:
        wordtext = wordtext + cd.chineseword + '\n' + cd.jyutping + '\n' + cd.definition + '\n'

    # first we find the word
    partlimits =  textprocessing.find_start_end_of_parts(cws.orgtext,cws.cwstext)
    foundword = -1
    for i in range(len(partlimits)):
        if position >= partlimits[i][0] and position <= partlimits[i][1]:
            foundword = i
    if foundword != -1:
        word = cws.cwstext[foundword]
        log.log("Looking up word " + word)
        cd = database.find_word(word)
        log.log("Found in dictionary: "+ str(cd))
        if (cd != None):
            wordtext = wordtext + '\n' + cd.chineseword + '\n' + cd.jyutping + '\n' + cd.definition + '\n'
    else:
        log.log("Couldnt find word")
    acwsret = process_chinese('lookup', 'lookup:' + str(position), wordtext, 1,cwsid)
    hits = database.get_responses(cwsid,position)
    ret.append(acwsret)
    for h in hits:
        log.log(' here is the response object:' +  str(h))
        if h.responsecwsid != None:
            storedcws = get_cws_text(h.responsecwsid)
            ret.append(storedcws)
        #responsecwsid = h[]
    return ret

@memory.cache 
def get_wordlist_from_cws(id):
    cws = database.get_cws_by_id(id)
    if cws == None:
        return []
    rawlist = cws.cwstext
    return list(set(rawlist))

@memory.cache 
def get_complete_vocab_from_cws(id):
    ret = []
    wl = get_wordlist_from_cws(id)
    for l in wl:
        look = database.find_word(l)
        if look != None:
            ret.append([look.chineseword,look.jyutping,look.definition])
        else:
            ret.append([l,None,None])
    return ret

def unanswered_questions():
    return database.get_unanswered_questions()

def get_imported_texts():
    return database.get_cws_list_by_type(constants.CWS_TYPE_IMPORT_TEXT)

@memory.cache
def dictionary_lookup(word):
    return database.find_word(word)

#changed to numbered
def create_verify_challenge(text):
    fulltext = "Create a numbered list of questions to check that the reader understands this text:"+text.strip()
    if database.has_question(fulltext) == False:
        database.add_ai_question(fulltext,constants.RESPONSE_TYPE_CHECK_QUESTION,-1,0,0)

#changed to numbered
def create_generative_text(fulltext):
     if database.has_question(fulltext) == False:
        database.add_ai_question(fulltext,constants.RESPONSE_TYPE_GENERATE_TEXT,-1,0,0)

def get_random_verify():
    examples = database.get_ai_response_of_type(constants.RESPONSE_TYPE_CHECK_QUESTION)
    pickedelement = random.choice(examples)
    cws = database.get_cws_by_id(pickedelement.responsecwsid)
    return cws