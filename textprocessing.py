#
# functions for cws and translation from simplified to traditional
#

import jieba
import jieba.posseg as pseg
import zhconv
import settings 
import opencc
from snownlp import SnowNLP
import re
import log


converter = opencc.OpenCC('s2t.json')

jieba.set_dictionary(settings.settings['jieba_dictionary'])
jieba.load_userdict(settings.settings['jieba_user_dictionary'])


# do we need to reload the dictionary?
# can we check is a dictionary is loaded in jieba?
def add_to_jieba(word):
    with open(settings.settings['jieba_userdict'], 'a', encoding="utf-8") as f:
        f.write(word + ' 1000 n\n')

def split_text(text):
    text_parts = pseg.cut(text)
    ret_parts = []
    for p in text_parts:
        ret_parts.append(p.word)
    return ret_parts

def get_word_class(text):
    text_parts = pseg.cut(text)
    ret_parts = {}
    for p,pos in text_parts:
        ret_parts[p] = pos
    return ret_parts

def split_text_parts(text):
    ret = []
    s = SnowNLP(text)
    for sent in s.sentences:
        ret.append(sent)
    return ret

def zng(paragraph):
    for sent in re.findall(u'[^「」!?。\.\!\?]+[」「!?。\.\!\?]?', paragraph, flags=re.U):
        yield sent

def split_text_sentences(text):
    ret = []
    for sent in zng(text):
        ret.append(sent)
    return ret

def split_text_paragraphs(text):
    ret = []
    for sent in text.split('\n'):
        ret.append(sent)
    return ret

def length_so_far(idx,parts):
    total = 0
    if idx == -1:
        return 0
    if idx == 0:
        return 0    
    for i in range(0,idx):
        total+= len( parts[i] )
    return total

def find_start_end_of_parts(text,parts):
    ret = []
    idx = 0
    while idx < len(parts):
        searchfor = parts[idx]
        sofar = length_so_far(idx,parts)
        whereisit = text.find(searchfor,sofar)
        if  (whereisit == -1):
            log.log("whereisit cannot be -1 " + searchfor)
            return []
        ret.append([whereisit,whereisit+len(parts[idx])])
        idx+=1
    return ret

# this only converts if the text is in simplified
def make_sure_traditional(text):
    return zhconv.convert(text,'zh-hk')
