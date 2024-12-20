import textprocessing
import frequencytools
import requests
import difficultlevel
import ssml
import openrouter
import json


mp3cachedirectory = '/home/erik/mp3cache'


def add_sentence_to_translated( sentence):
    try:
        url = f"https://chinese.eriktamm.com/api/add_background_work"
        call = {
            "processor":"sentencetranslator",
            "workstring": sentence
        }
        response = requests.post(url, json=call)
        if response.status_code == 200:
            return response.json()
        else:
            print(str(response))
            return None
    except:
        return None


def get_pause_as_ssml_tag():
    return "<break time='0.2s'/>"


def surround_text_with_short_pause(text):
    return get_pause_as_ssml_tag() + text + get_pause_as_ssml_tag()


def is_extended_ascii(s):
    """
    Check if the given string contains only extended ASCII characters (0-255).

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string contains only extended ASCII characters, False otherwise.
    """
    try:
        s.encode('latin-1')  # Latin-1 includes extended ASCII (0-255)
        return True
    except UnicodeEncodeError:
        return False



def extract_phrases_from_sentence(sentence):
    extr = "Break this sentence into reusable phrases and idioms for a Cantonese learner. Make a list and return as a in the following format [ {\"phrase\":phrase,\"translation\":english translation},...]. Here is the sentence: " + sentence
    api = openrouter.OpenRouterAPI()          
    # select free sometimes        
    result = api.open_router_qwen_25_72b(extr)
    result = result[result.find('['):]
    result = result[:result.find(']')]+']'
    result = json.loads(result)
    all = []
    for r in result:
        all.append({'word':r['phrase'],'translation':r['translation']})
    return all


too_common_words = ['美國人','佢哋','佢','但係','電話','同','人','佢','面對','包括','政府','的','來','包括','政府','係','佢','社交媒體','生意','食','三','多','明白','今','美國','喺','唔','老公','淨係','生活']

def should_word_be_learned(word,translation,previous_words):
    if word in too_common_words:
        return False
    if is_extended_ascii(word):
        return False
    if word == translation:
        return False
    
    if word in previous_words:
        return False
    
    return True

import hashlib

def md5_signature(input_string):
    """
    Generate an MD5 signature for the given string.

    Args:
        input_string (str): The string to hash.

    Returns:
        str: The MD5 hash of the string in hexadecimal format.
    """
    md5_hash = hashlib.md5()    
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()

def filename_from_string(astr):        
    path = md5_signature(astr) + ".mp3"
    return path

def make_sml_from_chinese_sentences(words_thats_been_given,sentences,include_prepostfix=True):
    sml_text = ''
    clean_text = ''
    fcounter = frequencytools.FrequencyCounter()
    for s in sentences:
        add_sentence_to_translated(s)

    difficultlevel.add_list_to_examples(sentences)
    if include_prepostfix == True:
        for s in sentences:
            sml_text += surround_text_with_short_pause(s) 
            clean_text +=  s + '\n'
    sml_text += "<break time=\"1.0s\"/>"    
    for s in sentences:
        sml_text += s + get_pause_as_ssml_tag()
        try:
            trycount = 0
            kson = []
            while trycount < 3:
                try:
                    #kson = extract_keywords_from_sentence(s)
                    kson = extract_phrases_from_sentence(s)
                    trycount=10
                except:
                    trycount+=1                    
            cnt = 0
            for k in kson:
                word = ''
                if 'word' in k.keys():
                    word = k['word']
                if 'text' in k.keys():
                    word = k['text']
                freq = fcounter.add_frequency(word)
                translation = k['translation']
                if should_word_be_learned(word,translation,words_thats_been_given) and freq < 30:
                    words_thats_been_given.append(word)
                    """
                    if freq < 10:
                        sml_text += "<break time=\"0.1s\"/>shortbreak" + word + 'shortbreak' + translation + 'shortbreak' +word +'shortbreak' + translation +'shortbreak' + word +'shortbreak' + translation +"<break time=\"0.1s\"/>"
                    else:
                        if freq < 15:
                            sml_text += "<break time=\"0.1s\"/>shortbreak" + word + 'shortbreak' + translation + 'shortbreak' +word +'shortbreak' + translation +"<break time=\"0.1s\"/>"
                        else:
                            sml_text += "<break time=\"0.1s\"/>shortbreak" + word + 'shortbreak' + translation + "<break time=\"0.1s\"/>"                                
                    """
                    sml_text += "<break time=\"0.1s\"/>shortbreak" + word + 'shortbreak' + translation + "<break time=\"0.1s\"/>"
                    cnt += 1
                    if cnt > 2:
                        sml_text += surround_text_with_short_pause(s)
                        cnt = 0
            sml_text +=  surround_text_with_short_pause(s)
            sml_text +=  surround_text_with_short_pause(s)                    
        except Exception as e:
            print(str(e))
        clean_text +=  s + '\n'

    if include_prepostfix == True:                        
        for s in sentences:
            sml_text += surround_text_with_short_pause(s)
            clean_text +=  s + '\n'
    sml_text += ' <break time=\"1.0s\"/>'
    fcounter.save_changes()
    f = open('lastssml.xml','w',encoding='utf-8')
    f.write(sml_text)
    f.close()
    return clean_text,sml_text


def make_sml_from_chinese_text(words_thats_been_given, translated):
    sentences = textprocessing.split_chinese_text_into_sentences(translated)
    # add to explanation work
    return make_sml_from_chinese_sentences(words_thats_been_given,sentences)