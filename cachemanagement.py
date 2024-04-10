#cachemanatmpgement.py
import json
import sys


import textprocessing

def save_cache_to_file(cache):
    f = open('/var/www/html/scene/examplescache.txt',"w",encoding='utf-8')
    f.write( json.dumps(cache))
    f.close()

def read_cache_from_file():
    cache = []
    try:
        f = open('/var/www/html/scene/examplescache.txt',"r",encoding='utf-8')
        content = f.read()
        f.close()
        cache = json.loads(content)
    except:
        cache = []
    return cache

    
def add_examples_to_cache(examples):
    cache = read_cache_from_file()
    cache.append(examples)
    save_cache_to_file(cache)


def import_examples_file(filename):
    f = open(filename,'r',encoding='utf-8')
    lines = json.loads(f.read())
    f.close()
    tmplines = []
    for l in lines:
        english = l['english']
        chinese = l['chinese']
        if (len(chinese) < 5):
            propchinese = chinese[0]
            chinese = textprocessing.make_sure_traditional(chinese)
            chinese = textprocessing.split_text(propchinese)
        tmplines.append({'english':english,'chinese':chinese})
        if len(tmplines) == 10:
            add_examples_to_cache(tmplines)
            tmplines = []
    add_examples_to_cache(tmplines)


if __name__ == "__main__":
    import_examples_file(sys.argv[1])



