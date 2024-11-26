#frequencytools.py
import dictionaryclient


cached_dict = None
changes = 0

def get_frequency(astr):
    if cached_dict == None:
        dc = dictionaryclient.DictionaryClient()
        cached_dict = dc.get_values('frequency')
    if not astr in cached_dict:
        return 0
    else:
        return int( cached_dict[astr])
    
def add_frequency(astr):
    if cached_dict == None:
        dc = dictionaryclient.DictionaryClient()
        cached_dict = dc.get_values('frequency')
    if not astr in cached_dict:
        cached_dict[astr] = "1"
        ret = 1
    else:
        cached_dict[astr] = str(int(cached_dict[astr]) + 1)
        ret = int(cached_dict[astr])
    changes =+ 1
    if changes > 20:
        changes = 0
        dc = dictionaryclient.DictionaryClient()
        dc.set_values('frequency',cached_dict)
    return ret
    
