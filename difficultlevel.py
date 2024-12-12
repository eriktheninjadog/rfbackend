#difficultlevel.py

import json
import openrouter
import remotechineseclient
import textprocessing

def add_list_to_examples(list):   
    try:
        txtlist = ''
        for l in list:
            txtlist += l + '\n'
        api = openrouter.OpenRouterAPI()
        retvalue = api.do_open_opus_questions("Given a list of sentences, return a list with the difficult level according to CEFR. The output format should be json like this: [{\"sentence\":sentence,\"level\":level},...]\n\nHere is the list:"+txtlist)
        retvalue = retvalue[retvalue.find('['):]
        retvalue = retvalue[:retvalue.find(']')+1]
        
        r = json.loads(retvalue)
        for i in r:
            level = i['level']
            sentence = i['sentence']
            if (level == 'C1' or level == 'B2'):            
                remotechineseclient.access_remote_client('add_example_to_cache', {"example": [{"english": sentence, "chinese": textprocessing.split_text(sentence)}]})
    except Exception as e:
        print(str(e))
        return