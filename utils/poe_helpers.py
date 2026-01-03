"""POE AI service utilities"""
import textprocessing
from utils.json_helpers import is_list


def create_proper_cantonese_questions(level, number_of_sentences, sentences):
    """Create questions for Cantonese translation"""
    print(str(sentences))
    ret = '\n'
    for s in sentences:
        for t in s['chinese']:
            ret = ret + t
        ret = ret + '\n'
    whole = "For each sentence in the list, rewrite it into plain spoken Cantonese.Return these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure. Here is the list: " + ret
    print("Here are the cantonese " + whole)
    return whole


def create_poe_example_question(level, number_of_sentences):
    """Create example question for POE AI"""
    text = "Create "+ str(number_of_sentences) +" sentences at B2 level. Return these together with translation into common spoken Cantonese (use traditional characters and use Cantonese grammar) in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."
    return text


def newParsePoe(aresult):
    """Parse POE AI results (new format)"""
    result = []
    for i in aresult:
        english = i['english']
        chinese = textprocessing.make_sure_traditional(i['chinese'])        
        tok = textprocessing.split_text(chinese)
        result.append( {"chinese":tok,"english":english} )
    return result
        

def parsePoe(aresult):
    """Parse POE AI results (legacy format)"""
    if is_list(aresult):
        return newParsePoe(aresult)
    print(" aresult " + str(aresult))
    if 'sentences' in aresult.keys():
        itemarray = aresult['sentences']
    if ('sentence_1' in aresult.keys()):
        #we have something different here
        itemarray = []
        for i in aresult.keys():
            itemarray.append(aresult[i])
    if 'example_sentences' in aresult.keys():
        itemarray = aresult['example_sentences']
    result = []
    #changed
    for item in itemarray:
        print(" item " + str(item))
        chinese = None
        if 'cantonese' in item.keys():
            chinese = item['cantonese']
        if 'chinese' in item.keys():
            chinese = item['chinese']
        tok = textprocessing.split_text(chinese)
        result.append( {"chinese":tok,"english":item['english']} )
    return result