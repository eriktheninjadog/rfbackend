#
# this is the database part of the backend
# note that we will shield the layer above from any database
# so we are no returning sqlAlchemy objects
#

from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, MetaData, String, Table, Text, Float, text
from sqlalchemy import inspect


# setup the classes
# I personally find this pretty ugly, so 

engine = create_engine('mysql+pymysql://erik:ninjadogs@localhost/language')
connection = engine.connect()
metadata = MetaData()
Base = automap_base()
Base.prepare(autoload_with=engine)

session = Session(engine)

activity = Base.classes.activity
book = Base.classes.book
bookpage = Base.classes.bookpage
article = Base.classes.article
ai_response = Base.classes.ai_response
cws_row = Base.classes.cws
words = Base.classes.words
insp = inspect(engine) 

def get_all_books():
    ret = []
    records = session.query(book).all()
    for record in records:
        ret.append([record.id,record.title,record.numberofpages,record.comment])
    return ret

def get_book_page(abookid,apagenr):
    page = session.query(bookpage).filter(bookpage.bookid == abookid,bookpage.pagenr==apagenr).first()
    if page == None:
        return None
    else:
        return [page.bookid,page.pagenr,page.pagetext]

def add_book_page(abookid,apagenr,atext):
    bookpage.insert().values(bookid = abookid,pagenr = apagenr, pagetext = atext)
    session.commit()

def get_activity(id):
    act = session.query(activity).filter(activity.id == id).first()
    return [act.id,act.type,act.media,act.startTime,act.endTime]


def add_activity(atype,amedia,astartTime,aendTime):
    activity.insert().values(type=atype,media=amedia,startTime = astartTime,endTime = aendTime )
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
        return [found.chiword,found.canto,found.exp]

def get_cws_by_id(id):
    found = session.query(cws_row).filter(cws_row.id == id).first()
    if found == None:
        return None
    else:
        return [found.id,found.orgtext,found.cwstext,found.metadata,found.title,found.source]

def get_cws_by_signature(signature):
    found = session.query(cws_row).filter(cws_row.signature == signature).first()
    if found == None:
        return None
    else:
        return [found.id,found.orgtext,found.cwstext,found.metadata,found.title,found.source]

def add_cws(aorgtext,acwstext,asignature,ametadata,atitle,asource):
    cws_row.insert().values(
        orgtext = aorgtext,
        cwstext = acwstext,
        signature = asignature,
        metadata = ametadata,
        title = atitle,
        source = asource
    )
    session.commit()



#print(get_all_books())
#print(get_book_page(6,10))