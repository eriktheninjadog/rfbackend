"""Cache management service"""
import random
import cachemanagement


def pick_random_sentence_from_cache():
    """Pick a random sentence from cache"""
    repos = cachemanagement.read_cache_from_file()
    if len(repos) == 0:
        return None
    repo = random.choice(repos)
    sentence = random.choice(repo)
    return sentence


def pick_random_sentences_from_cache(nr):
    """Pick multiple random sentences from cache"""
    ret = []
    for i in range(nr):
        sentence = pick_random_sentence_from_cache()
        if sentence != None:
            ret.append(sentence)
    return ret
    

def get_examples_from_cache():
    """Get examples from cache and remove them"""
    cache = cachemanagement.read_cache_from_file()
    if len(cache) == 0:
        return None
    examples = cache.pop()
    cachemanagement.save_cache_to_file(cache)
    return examples