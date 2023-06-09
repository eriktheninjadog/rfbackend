from collections import namedtuple


Article = namedtuple('Article',['title','body'])
Activity = namedtuple('Activity',['id','type','media','startTime','endTime'])
DictionaryWord = namedtuple('DictionaryWord',['chineseword','jyutping','definition'])
CWS = namedtuple('CWS',['id','created','orgtext','cwstext','signature','metadata','title','source','type','parent'])
AIResponse = namedtuple('AIResponse',['id','question','responsecwsid','metadata','cwsid','start','end','type'])
Fragment = namedtuple('Fragment',['orgcwsid','fragmentcwsid','start','end','type'])
