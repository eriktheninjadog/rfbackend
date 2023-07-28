
import aisocketapi
import api
import constants

def batchprocess_text(all_of_it,splitfunction,processfunction):
    # Open a file: file
    total = ''
    splitparts = splitfunction(all_of_it)
    for i in splitparts:
        newt = processfunction(i)
        total = total + newt
    return total

def splitfunction(txt):
    maxlen = 1024*2
    ret = []
    pos = 0
    lastpos = 0
    while pos < len(txt):
        pos += 1
        if (pos - lastpos) > maxlen:
            while (txt[pos] == separator):
                pos += 1
            ret.append(txt[lastpos:pos])
            lastpos = pos
    return ret

def simplifyfunction(txt):
    return aisocketapi.ask_ai('Rewrite this in chinese using only simple words:' + txt)

def simplify_cws(id):
    thecws = api.get_cws_text(id)
    orgtext = thecws.orgtext
    simpletext = batchprocess_text(orgtext,splitfunction,simplifyfunction)
    newcws = api.process_chinese(thecws.title + ' simplified ','ai',simpletext,constants.CWS_TYPE_IMPORT_TEXT,id) 
    return newcws