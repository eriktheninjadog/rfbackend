#
# this is the database part of the backend
# note that we will shield the layer above from any database
# so we are no returning sqlAlchemy objects
# Simplification: We don't need books. We don't need
# articles. We will only saved processed texts. A processed text
# has a type.
# it also can be a child (of another text)
# have a title etc
# this means we are... already done :-)
import json
import log

from dataobject import CWS
from dataobject import DictionaryWord
from dataobject import Activity
from dataobject import AIResponse
from dataobject import Fragment

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, MetaData, String, Table, Text, Float, text
from sqlalchemy import inspect

# setup the classes
# I personally find this pretty ugly, so 

engine = create_engine('mysql+pymysql://erik:ninjadogs@localhost/language')
connection = engine.connect()
session = Session(engine)

Base = automap_base()
Base.prepare(autoload_with=engine)
metadata_obj = MetaData()
metadata_obj.reflect(bind=engine)


activity = Base.classes.activity
ai_response = Base.classes.ai_response
cws_row = Base.classes.cws
words = Base.classes.words
ai_reponse = Base.classes.ai_response
fragment = Table('textfragment', metadata_obj, autoload_with=engine)

def add_fragment(afragment):
    try:
        f = fragment.insert().values(
            orgcwsid = afragment.orgcwsid,
            fragmentcwsid = afragment.fragmentcwsid,
            start = afragment.start,
            end = afragment.end,
            type = afragment.type        
            )
        session.execute(f)
        session.commit()
    except: 
        None
    return None

def get_activity(id):
    act = session.query(activity).filter(activity.id == id).first()
    return Activity(act.id,act.type,act.media,act.startTime,act.endTime)

def add_activity(activity):
    activity.insert().values(type=activity.type,media=activity.media,startTime = activity.startTime,endTime = activity.endTime )
    session.commit()

def add_or_update_word(chinese,jyutping, definition):
    if (find_word(chinese) == None):
        words.insert().values(chiword = chinese, canto = jyutping, exp = definition)
    else:
        found = session.query(words).filter(words.chiword == chinese).first()
        found.canto = jyutping
        found.exp = definition
    session.commit()

def find_word(chinese):
    found = session.query(words).filter(words.chiword == chinese).first()
    if found == None:
        return None
    else:
        return DictionaryWord(found.chiword,found.canto,found.exp)

def cws_row_to_dataobject(row):
    return CWS(row.id,row.created,row.orgtext, json.loads(row.cwstext),row.signature,row.metadata,row.title,row.source,row.type,row.parent)

def cws_row_to_dataobject_no_text(row):
    return CWS(row.id,row.created, None,None,row.signature,row.metadata,row.title,row.source,row.type,row.parent)

def get_cws_by_id(id):
    found = session.query(cws_row).filter(cws_row.id == id).first()
    if found == None:
        return None
    else:
        return cws_row_to_dataobject(found)
    
def get_cws_by_signature(signature):
    log.log("get_cws_by_signature("+signature+")")
    found = session.query(cws_row).filter(cws_row.signature == signature).first()
    if found == None:
        log.log("get_cws_by_signature("+signature+") not found" )
        return None
    else:
        return cws_row_to_dataobject(found)

def rowstocwslist(rows):
    ret = []
    for row in rows:
        ret.append( cws_row_to_dataobject_no_text(row) )
    return ret

def get_cws_list_by_type(type):
    condition = (cws_row.type == type)
    foundrows = session.query(cws_row).filter(condition)
    return rowstocwslist(foundrows)
    
def add_cws(cwsobject):
    c = cws_row(
        orgtext = cwsobject.orgtext,
        cwstext = json.dumps(cwsobject.cwstext),
        signature = cwsobject.signature,
        metadata = cwsobject.metadata,
        title = cwsobject.title,
        source = cwsobject.source,
        type = cwsobject.type,
        parent = cwsobject.parent
    )
    session.add(c)
    session.flush()
    session.commit()
    return c.id

def update_cws(cwsobject):
    foundit = session.query(cws_row).filter(cws_row.id== cwsobject.id).first()
    if foundit == None:
        return None
    foundit.orgtext = cwsobject.orgtext
    foundit.cwstext = json.dumps(cwsobject.cwstext)
    foundit.signature = cwsobject.signature
    foundit.metadata = cwsobject.metadata
    foundit.title = cwsobject.title
    foundit.source = cwsobject.source
    foundit.type = cwsobject.type
    foundit.parent = cwsobject.parent
    session.commit()

def add_ai_question(question,type,cwsid,start,end):
    ap = ai_reponse(question=question,
                    type = type,
                    cwsid = cwsid,
                    start = start,
                    end = end
                    )
    session.add(ap)
    session.flush()
    session.commit()
    return ap.id

def answer_ai_response(id,repsonsecwsid):
    foundit = session.query(ai_reponse).filter( ai_reponse.id== id ).first()
    if foundit == None:
        return None
    foundit.responsecwsid = repsonsecwsid
    session.flush()
    session.commit()
    return id

def get_unanswered_questions():
    ret = []
    foundrows = session.query(ai_reponse).filter( ai_reponse.responsecwsid == None )
    for r in foundrows:
        rr = AIResponse(r.id,r.question,None,None,r.cwsid,r.start,r.end,r.type)
        ret.append(rr)
    return ret

def get_responses(cwsid,position):
    ret = []
    foundrows = session.query(ai_reponse).filter( ai_reponse.cwsid== cwsid,ai_reponse.responsecwsid != None, ai_response.start <= position,ai_response.end >= position)
    for r in foundrows:
        rr = AIResponse(r.id,r.question,r.responsecwsid,r.metadata,r.cwsid,r.start,r.end,r.type)
        ret.append(rr)
    return ret

