# used to process files in command mode
import api
import constants
import sys
import batchprocessing
import aisocketapi


def asplitfunction(txt):
    maxlen = 10240
    ret = []
    pos = 0
    lastpos = 0
    txtlen = len(txt)
    while pos < txtlen:
        pos += 1
        if (pos - lastpos) > maxlen:
            while (txt[pos] != '。' and pos < txtlen):
                pos += 1
            if (txt[pos] == '。'):
                pos += 1
            ret.append(txt[lastpos:pos])
            print("added " + str(pos))
            lastpos = pos
    ret.append(txt[lastpos:pos])
    print("number of splits " + str(len(ret))) 
    return ret

def split_file_into_chunks(filename):
    text_file = open(filename, "r",encoding="utf-8")
    #read whole file to a string
    data = text_file.read()
    chunks = asplitfunction(data)
    #close file
    text_file.close()
    return chunks

def import_file(bookname,filename,minstart,maxstart):
    print("import file called " + bookname)
    chunks = split_file_into_chunks(filename)
    counter = 0
    for c in chunks:
        print(str(counter))
        if (counter > maxstart):
            exit(-1)
        if (counter >= minstart):
            cws = api.process_chinese(bookname + str(counter),"import",c,constants.CWS_TYPE_IMPORT_TEXT,-1)
            print(str(cws.id))
            batchprocessing.apply_ai_to_cws(cws.id,"Rewrite this using chinese using short sentences, words that an 8 year old child would understand and put a _ before all personal names:")
        counter += 1
#
#
#

def to_file(filename,prefix,question):
    print("to text called")
    chunks = split_file_into_chunks(filename)
    outfile = open( prefix+'_' + filename,"w",encoding="utf-8")
    for c in chunks:
        ret = aisocketapi.ask_ai(question + ":" + c)
        outfile.write(ret)
        outfile.flush()
    outfile.close()

print("command: whatdoto\n")
print("whattodo:\n trad - bookname, filename,minstart,maxstart\n")
print("tofile - filename pre-fix textline\n")
if (sys.argv[1] == "trad"):
    import_file(sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]))
if (sys.argv[1] == "tofile"):
    import_file(sys.argv[2],sys.argv[3],sys.argv[4])

