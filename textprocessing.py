#
# functions for cws and translation from simplified to traditional
#

import jieba
import jieba.posseg as pseg
import settings 
import opencc

converter = opencc.OpenCC('s2t.json')

# do we need to reload the dictionary?
# can we check is a dictionary is loaded in jieba?
def add_to_jieba(word):
    with open(settings.settings['jieba_userdict'], 'a', encoding="utf-8") as f:
        f.write(word + ' 1000 n\n')

def split_text(text):
    jieba.set_dictionary(settings.settings['jieba_dictionary'])
    jieba.load_userdict(settings.settings['jieba_userdict'])
    text_parts = pseg.cut(text)
    ret_parts = []
    for p in text_parts:
        ret_parts.append(p.word)
    return ret_parts

def convert_to_traditional(text):
    return converter.convert(text)
