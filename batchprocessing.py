import aisocketapi
import api
import constants

def batchprocess_text(all_of_it,splitfunction,processfunction):
    # Open a file: file
    total = ''
    print(" batchprocess text - length of text: " + str(len(all_of_it)))
    splitparts = splitfunction(all_of_it)
    for i in splitparts:
        print("batchprocess_text processing one part")
        newt = processfunction(i)
        print("batchprocess_text processing one part processed !")        
        total = total + newt
    return total

def splitfunction(txt):
    maxlen = 1024
    ret = []
    pos = 0
    lastpos = 0
    txtlen = len(txt)
    print(splitfunction)
    while pos < txtlen:
        pos += 1
        if (pos - lastpos) > maxlen:
            while (txt[pos] != '。' and pos < txtlen):
                pos += 1
            if (txt[pos] == '。'):
                pos += 1
            ret.append(txt[lastpos:pos])
            lastpos = pos
    ret.append(txt[lastpos:pos])
    print("number of splits " + str(len(ret))) 
    return ret

def ai_function_factory(ai_string):
    def ai_f(txt):
        return aisocketapi.ask_ai(ai_string + txt)
    return ai_f

def simplifyfunction(txt):
    return aisocketapi.ask_ai('Rewrite this in chinese using only simple words and short sentences using active voice:' + txt)

def simplify_cws(id):
    thecws = api.get_cws_text(id)
    print("simplify_cws gotten thecws "+ str(thecws.id))
    orgtext = thecws.orgtext
    simpletext = batchprocess_text(orgtext,splitfunction,simplifyfunction)
    newcws = api.process_chinese(thecws.title + ' simplified ','ai',simpletext,constants.CWS_TYPE_IMPORT_TEXT,id) 
    return newcws

def apply_ai_to_cws(id,aitext):
    thecws = api.get_cws_text(id)
    orgtext = thecws.orgtext
    simpletext = batchprocess_text(orgtext,splitfunction,ai_function_factory( aitext))
    newcws = api.process_chinese( thecws.title + ' ai ' + aitext,simpletext,constants.CWS_TYPE_IMPORT_TEXT,id) 
    return newcws
