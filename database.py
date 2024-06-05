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

import mysql.connector

import json

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

import urllib.parse


cachedir = '/tmp/'

from joblib import Memory
memory = Memory(cachedir, verbose=0)



from pymemcache.client import base
# setup the classes
# I personally find this pretty ugly, so 

engine = create_engine('mysql://erik:ninjadogs@localhost/language',pool_recycle=60 * 5, pool_pre_ping=True)
connection = engine.connect()
session = Session(engine)

Base = automap_base()
Base.prepare(autoload_with=engine)
metadata_obj = MetaData()
metadata_obj.reflect(bind=engine)

client = base.Client(('localhost', 11211))

activity = Base.classes.activity
ai_response = Base.classes.ai_response
cws_row = Base.classes.cws
words = Base.classes.words
ai_reponse = Base.classes.ai_response
#fragment = Table('textfragment', metadata_obj, autoload_with=engine)
fragment = Base.classes.textfragment


def put_cached(key,pyobject):
    str = json.dumps(pyobject)
    client.set(key,str)

def get_cached(key):
    str = client.get(key)
    if str == None:
        return None
    return json.loads(str)

def store_cws_in_cache(key,cws):
    put_cached('cachedcws'+str(key),json.dumps(cws))

def get_cws_from_cache(key):
    retArray = get_cached('cachedcws'+str(key))
    if (retArray==None):
        return None
    return CWS(retArray[0],retArray[1],retArray[2],
               retArray[3],retArray[4],retArray[5],
               retArray[6],retArray[7],retArray[8],
               retArray[9])

def add_fragment(afragment):
    c = fragment(
            orgcwsid = afragment.orgcwsid,
            #fragmentcwsid = afragment.fragmentcwsid,
            start = afragment.start,
            end = afragment.end,
            type = afragment.type        
    )
    session.add(c)
    session.flush()
    session.commit()
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

def find_word(chineseword):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "select chiword,canto,exp from words where chiword like '" + chineseword+ "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    ret = []
    for (chiword,canto,exp) in myresult:
        ret.append( DictionaryWord(chiword,canto,exp) )
    mycursor.close()
    mydb.close()
    if len(ret) == 0:
        return None
    else:
        return ret[0]

def cws_row_to_dataobject(row):
    return CWS(row.id,row.created,row.orgtext, json.loads(row.cwstext),row.signature,row.metadata,row.title,row.source,row.type,row.parent)

def cws_row_to_dataobject_no_text(row):
    return CWS(row.id,row.created, None,None,row.signature,row.metadata,row.title,row.source,row.type,row.parent)

def get_connection():
    mydb = mysql.connector.connect(                                                  
        host="localhost",                                                            
        user="erik",                                                                 
        password="ninjadogs",                                                        
        database='language'                                                          
    )
    return mydb

def add_look_up(term,cwsid):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO lookuphistory (cwsid, term) VALUES (%s, %s)'
    val = (cwsid,term)
    mycursor.execute(sql,val)
    mydb.commit()
    mycursor.close()
    mydb.close()
    
def lookup_history(cwsid):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    if (cwsid != -1):
        sql = 'select term from lookuphistory where cwsid = ' + str(cwsid)
    else:
        sql = 'select distinct term from lookuphistory'
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    for term in myresult:
        ret.append(term[0])
    mycursor.close()
    mydb.close()
    return ret
    
                                                                                
def update_dictionary(chineseword,jyutping,definition):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "delete from words where chiword like '" + chineseword+ "'"
    mycursor.execute(sql)
    mydb.commit()
    sql = 'INSERT INTO words (chiword, canto, exp) VALUES (%s, %s, %s)'
    log.log(sql)    
    val = (chineseword,jyutping,definition)
    log.log(str(val))
    mycursor.execute(sql,val)
    mydb.commit()
    mycursor.close()
    mydb.close()
    
def get_cws_by_id(id):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,created,orgtext,cwstext,signature,metadata,title,source,type,parent FROM cws WHERE id = " + str(id)
    mycursor.execute(sql)
    print(sql)                                                            
    myresult = mycursor.fetchall() 
    for (id,created,orgtext,cwstext,signature,metadata,title,source,type,parent) in myresult:
        ret.append( CWS(id,created,orgtext,json.loads(cwstext),signature,metadata,title,source,type,parent))
    mycursor.close()
    mydb.close()
    if (len(ret)>0):
        return ret[0]
    else:
        return None
    

def get_cws_by_title_and_type(title,type):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,created,orgtext,cwstext,signature,metadata,title,source,type,parent FROM cws WHERE type = " + str(type) +" and title like '" +  title + "'"
    mycursor.execute(sql)
    print(sql)                                                            
    myresult = mycursor.fetchall() 
    for (id,created,orgtext,cwstext,signature,metadata,title,source,type,parent) in myresult:
        ret.append( CWS(id,created,orgtext,json.loads(cwstext),signature,metadata,title,source,type,parent))
    mycursor.close()
    mydb.close()
    if (len(ret)>0):
        return ret[0]
    else:
        return None
    
def update_cws_text(id,text,cwstext,signature):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "UPDATE cws set orgtext = %s, cwstext = %s , signature = %s where id = " + str(id)
    val = (text, json.dumps(cwstext),signature)
    mycursor.execute(sql, val)
    mydb.commit()
    None
    
def get_cws_by_signature(signature):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,created,orgtext,cwstext,signature,metadata,title,source,type,parent FROM cws WHERE signature like '" + signature + "'"
    mycursor.execute(sql)    
    myresult = mycursor.fetchall() 
    for (id,created,orgtext,cwstext,signature,metadata,title,source,type,parent) in myresult:
        ret.append( CWS(id,created,orgtext, json.loads(cwstext),signature,metadata,title,source,type,parent))
    mycursor.close()
    mydb.close()
    if (len(ret)>0):
        return ret[0]
    else:
        return None

def rowstocwslist(rows):
    ret = []
    for row in rows:
        ret.append( cws_row_to_dataobject_no_text(row) )
    return ret
                                                                                
def get_cws_list_by_type(type):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,title FROM cws WHERE type = " + str(type)
    mycursor.execute(sql)                                                            
    myresult = mycursor.fetchall() 
    for (id,title) in myresult:
        ret.append( CWS(id,None,None,None,None,None,title,None,type,-1))
    mycursor.close()
    mydb.close()
    return ret

def get_cws_list_by_status(status):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,title FROM cws WHERE status = " + str(status) + " ORDER BY id DESC"
    mycursor.execute(sql)                                                            
    myresult = mycursor.fetchall() 
    for (id,title) in myresult:
        ret.append( CWS(id,None,None,None,None,None,title,None,None,-1))
    mycursor.close()
    mydb.close()
    return ret



def update_cws_status(cwsid,status):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "UPDATE cws set status = "+str(status)+" WHERE id = " + str(cwsid)
    mycursor.execute(sql)
    mydb.commit()                                                            
    mycursor.close()
    mydb.close()
    return cwsid
    

    
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

def add_answered_ai_question(question,type,cwsid,start,end,responsecwsid):
    ap = ai_reponse(question=question,
                    type = type,
                    cwsid = cwsid,
                    start = start,
                    end = end,
                    responsecwsid = responsecwsid
                    )
    session.add(ap)
    session.flush()
    session.commit()
    return ap.id


def answer_ai_response(id,repsonsecwsid):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "update ai_response set responsecwsid = " + str(repsonsecwsid) + " WHERE id = " + str(id)
    print(sql)
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()


def delete_cws_by_id(cwsid):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "delete from cws where id = " + str(cwsid)
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()


    
def get_unanswered_questions():
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,question,responsecwsid,metadata,cwsid,start,end,type FROM ai_response WHERE responsecwsid is null"
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    for (id,question,responsecwsid,metadata,cwsid,type,start,end) in myresult:
        ret.append( AIResponse(id,question,responsecwsid,metadata,cwsid,start,end,type))
    mycursor.close()
    mydb.close()
    return ret 

def get_responses(cwsid,position):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,question,responsecwsid,metadata,cwsid,type,start,end FROM ai_response WHERE cwsid = " + str(cwsid) + " and start <= " + str(position) + ' and end>= ' + str(position)
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    for (id,question,responsecwsid,metadata,cwsid,type,start,end) in myresult:
        ret.append( AIResponse(id,question,responsecwsid,metadata,cwsid,start,end,type))
    mycursor.close()
    mydb.close()
    return ret 


def get_responses_of_type(type):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,question,responsecwsid,metadata,cwsid,type,start,end FROM ai_response WHERE type = " + str(type)
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    for (id,question,responsecwsid,metadata,cwsid,type,start,end) in myresult:
        ret.append( AIResponse(id,question,responsecwsid,metadata,cwsid,start,end,type))
    mycursor.close()
    mydb.close()
    return ret 


def delete_responses_of_type(type):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "delete FROM ai_response WHERE type = " + str(type)
    mycursor.execute(sql)
    mycursor.close()
    mydb.close()
    return ret 


def has_question(fulltext):
    ret = False
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id FROM ai_response WHERE question like '" + fulltext.replace("'","''") + "'"    
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    for (id) in myresult:
        ret = True
    mycursor.close()
    mydb.close()    
    return ret

def get_ai_response_of_type(type):
    ret = []
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "SELECT id,question,responsecwsid,metadata,cwsid,start,end,type FROM ai_response WHERE type = " + str(type)    
    mycursor.execute(sql)
    myresult = mycursor.fetchall() 
    for (id,question,responsecwsid,metadata,cwsid,type,start,end) in myresult:
        ret.append( AIResponse(id,question,responsecwsid,metadata,cwsid,start,end,type))
    mycursor.close()
    mydb.close()
    return ret


def update_pleco(pleco):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "delete from pleco where pleco like '" + pleco+ "'"
    mycursor.execute(sql)
    mydb.commit()
    sql = "INSERT INTO pleco (pleco) VALUES ('"+ pleco +"')"
    log.log(sql)    
    val = (pleco)
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()
    
    
def escape_sql_string(string):
    if string is None:
        return 'NULL'
    
    # Escape single quotes by replacing them with two single quotes
    string = string.replace("'", "''")
    
    # Wrap the string with single quotes
    return string
    
def add_listening_sentence(sentence,tokens,result):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "insert into listen_sentence(listen_at,sentence,tokens,result) values (UTC_TIMESTAMP(),'"+escape_sql_string(sentence)+"','"+escape_sql_string(tokens)+"',"+str(result)+")"
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()


def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "insert into output_exercise(english,chinesetokens,mp3name,type,result,milliseconds,whenutcmilliseconds) values ('"+escape_sql_string(english)+"','"+escape_sql_string(chinesetokens)+"','" +escape_sql_string(mp3name) +"',"+str(type)+","+str(result)+","+str(milliseconds)+","+str(whenutcmilliseconds)+")"
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()
        

def get_total_audio_time():
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "select sum(milliseconds) as total from output_exercise where mp3name like 'mp3'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (id) in myresult:
        total = id
        
    sql = "select sum(milliseconds) as total from output_exercise where mp3name like 'mp3' and whenutcmilliseconds > (unix_timestamp(TIMESTAMP(CAST(CURDATE() AS CHAR), '00:00:00'))*1000)"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (id) in myresult:
        totalshort = id
    
    mycursor.close()
    mydb.close()
    return [total,totalshort]


def get_total_output_time():
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    sql = "select sum(milliseconds) as total from output_exercise where milliseconds < 180000 and type = 2 "
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (id) in myresult:
        total = id
    sql = "select sum(milliseconds) as total from output_exercise where milliseconds < 180000  and type = 2 and whenutcmilliseconds > (unix_timestamp(TIMESTAMP(CAST(CURDATE() AS CHAR), '00:00:00'))*1000)"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (id) in myresult:
        totalshort = id

    mycursor.close()
    mydb.close()
    return [total,totalshort]


def get_failed_outputs(nr):
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    result = []
    sql = "select distinct(chinesetokens),english from output_exercise where type = 2 and result = 1 order by rand() limit " + str(nr)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (chinesetokens,english) in myresult:
        result.append({"english":english,"chinese": json.loads(chinesetokens) })
    mycursor.close()
    mydb.close()
    return result


def get_failed_outputs_highfail_prio(nr):
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    result = []
    sql = "select chinesetokens,english from output_exercise where type = 2 and result = 1 order by rand() limit " + str(nr)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (chinesetokens,english) in myresult:
        result.append({"english":english,"chinese": json.loads(chinesetokens) })
    mycursor.close()
    mydb.close()
    return result

def get_failed_outputs_highfail_timed(nr):
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    result = []
    sql = "select chinesetokens,english from output_exercise where type = 2 and result = 1 order by rand() limit " + str(nr)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (chinesetokens,english) in myresult:
        result.append({"english":english,"chinese": json.loads(chinesetokens) })
    mycursor.close()
    mydb.close()
    return result


def get_failed_outputs_lately(nr,days):
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    result = []    
    sql = "select distinct(chinesetokens),english from output_exercise where type = 2 and whenutcmilliseconds > (UNIX_TIMESTAMP(CURRENT_TIMESTAMP())-("+str(24*days)+"*60*60))*1000 order by rand() limit " + str(nr)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (chinesetokens,english) in myresult:
        result.append({"english":english,"chinese": json.loads(chinesetokens) })
    mycursor.close()
    mydb.close()
    return result




def get_outputs(nr):
    # def add_output_exercise(english,chinesetokens,mp3name,type, result,milliseconds,whenutcmilliseconds):
    mydb = get_connection()
    mycursor = mydb.cursor()
    result = []
    sql = "select distinct(chinesetokens),english from output_exercise where type = 2 order by rand() limit " + str(nr)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for (chinesetokens,english) in myresult:
        result.append({"english":english,"chinese": json.loads(chinesetokens) })
    mycursor.close()
    mydb.close()
    return result
