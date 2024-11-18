#frequencytools.py
import dictionaryclient

def get_frequency(astr):
    dc = dictionaryclient.DictionaryClient()    
    val = dc.get_dictionary_value("frequency",astr)
    if val == None:
        return 0
    else:
        return int(val)
    
def add_frequency(astr):
    dc = dictionaryclient.DictionaryClient()    
    val = dc.get_dictionary_value("frequency",astr)
    val = val['result']
    if val[1] == None:
        dc.set_dictionary_value("frequency",astr,"1")
        return 1
    else:
        dc.set_dictionary_value("frequency",astr,str(int(val[1]) + 1))
        return int(val[1]) + 1
