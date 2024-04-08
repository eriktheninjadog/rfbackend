#cachemanatmpgement.py
import json
import sys


import webapi
import textprocessing




def import_examples_file(filename):
    f = open(filename,'r',encoding='utf-8')
    lines = json.loads(f.read())
    f.close()
    tmplines = []
    for l in lines:
        english = l['english']
        chinese = l['chinese']
        if (len(chinese) < 2):
            propchinese = chinese[0]
            chinese = textprocessing.split_text(propchinese)
        tmplines.append({'english':english,'chinese':chinese})
        if len(tmplines) == 10:
            webapi.add_examples_to_cache(tmplines)
            tmplines = []
    webapi.add_examples_to_cache(tmplines)


import_examples_file(sys.argv[1])



