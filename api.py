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

# step 1. Input chinese.
# This will create a cws and return it. it will set source and title

def process_chinese(title, source, text, type,parentid):
    # 
    # Try to find a cws
    signature = textsignature.generate_signature(text)
    found = database.get_cws_by_signature(signature)
    if found != None:
        return found
    else:
        cwstext = textprocessing.split_text(text)
        cws = CWS(-1,None,text,cwstext,signature,"",title,source,type,parentid)
        id = database.add_cws(cws)
        return database.get_cws_by_id(id)

def get_article(url):
    art = articlecrawler.getarticle(url)
    return process_chinese(art.title,url,art.title+"\n"+art.body,2,-1)

def throw_away_CWS_from_article(art):
    splitted = textprocessing.split_text(art.title+"\n"+art.body)
    return CWS(-1,None,None,splitted,None,"",art.title,"reddit",-1,-1)

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
