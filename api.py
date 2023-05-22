#
# this is the main api.
# web access lies above this
# only dataobjects or simple ids are passed between these
#
from settings import settings
from dataobject import CWS
import textprocessing
import textsignature
import database
import articlecrawler
import json
import log
import constants

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
def lookup_position(cwsid,position):
    log.log("lookup_position("+str(cwsid)+","+ str(position)+")")
    #
    # so lets go for the cws
    #
    ret = []
    cws = database.get_cws_by_id(cwsid)
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
        log("Couldnt find word")
    acwsret = process_chinese('lookup', 'lookup:' + str(position), wordtext, 1,cwsid)
    hits = database.get_responses(cwsid,position)
    ret.append(acwsret)
    for h in hits:
        ret.append(h)
    return ret

def unanswered_questions():
    return database.get_unanswered_questions()

def get_imported_texts():
    return database.get_cws_list_by_type(constants.CWS_TYPE_IMPORT_TEXT)