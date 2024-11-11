
import requests
import json
import random
import wordlists
import textprocessing
import os

def pick_random_sentence_from_cache():
    repos = read_cache_from_file()
    if len(repos) == 0:
        return None
    repo = random.choice(repos)
    sentence = random.choice(repo)
    return sentence

def pick_random_sentences_from_cache(nr):
    ret = []
    for i in range(nr):
        sentence = pick_random_sentence_from_cache()
        if sentence != None:
            ret.append(sentence)
    return ret
    
def read_bearer_key():
    f = open('/var/www/html/api/rfbackend/routerkey.txt','r')
    bearer = f.readline()
    f.close()
    return bearer.strip()

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


def create_proper_cantonese_questions(level,number_of_sentences):
    sentences = pick_random_sentences_from_cache(number_of_sentences)
    print(str(sentences))
    ret = '\n'
    for s in sentences:
        for t in s['chinese']:
            ret = ret + t
        ret = ret + '\n'
    whole = "For each sentence in the list, rewrite it into plain spoken Cantonese.Return these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure. Here is the list: " + ret
    print("Here are the cantonese " + whole)
    return whole

def create_pattern_example_question(level,number_of_sentences):
    text = "Create "+ str(number_of_sentences) +" examples in Cantonese using the following sentence pattern: " + wordlists.pick_sample_sentence__pattern() + ". Return these together with english translation in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."
    return text

def create_poe_example_question(level,number_of_sentences):
    text = "Write " + str(number_of_sentences) + " example sentences in English at a " + level + " level of difficulty, along with their Cantonese translation, in a dictionary in JSON format without any other text."        
    text = "Create "+ str(number_of_sentences) +" sentences at A1 level including some the following words: " + wordlists.get_sample_A1_wordlist(30)+ ". Return these together with vernacular cantonese translation (use traditional charactters) in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."
#    if random.randint(0,10) > 7:
#        text = "Create "+ str(number_of_sentences) +" sentences at A1 level including some the following words: " + wordlists.get_sample_A1_wordlist(30)+ ". Return these together with a simple, spoken cantonese equivalent (use traditional charactters) in json format like this: [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}].Only respond with the json structure."        
    if random.randint(0,10) > 3:
        text = create_pattern_example_question(level,number_of_sentences)
    #if random.randint(0,10) > 7:        
    #    text = create_proper_cantonese_questions(level,number_of_sentences)    
    return text

def do_opus_questions():
    question = create_poe_example_question('A1',20)
    
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "anthropic/claude-3-opus", # Optional
        "messages": [
        {"role": "user", "content": question}
        ]
    })
    )
    responsejson = response.json()
    f = open('opusanswer.json','w',encoding ='utf-8')
    f.write(json.dumps(responsejson))
    f.close()
    parserouterjson(responsejson)
    
    
def newParsePoe(aresult):
    result = []
    for i in aresult:
        english = i['english']
        chinese = i['chinese']
        tok = textprocessing.split_text(chinese)
        result.append( {"chinese":tok,"english":english} )
    return result
    
def parserouterjson(adict):
    choices = adict['choices']
    message = choices[0]['message']
    examples = message['content']
    parsedexamples = json.loads(examples)
    #print(examples))
    result = newParsePoe(parsedexamples)
    add_examples_to_cache(result)
    None
    
    
    
    
def do_open_opus_questions(question):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "anthropic/claude-3.5-sonnet",
        #"model": "anthropic/claude-3-opus", # Optional
        "messages": [
        {"role": "assistant", "content": question}
        ]
    })
    )
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    return content



def open_router_nemotron_70b(user_content):
    response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "nvidia/llama-3.1-nemotron-70b-instruct", # Optional
        "messages": [
        {"role": "user", "content": user_content},
        {"role": "system", "content": "You are an assistant used to summarize and simplify news"}        
        ],
        
    })
    )
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    return content




def open_router_meta_llama_llama_3_1_8b_instruct(user_content):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "meta-llama/llama-3.1-8b-instruct", # Optional
        "messages": [
        {"role": "user", "content": user_content},
        {"role": "system", "content": "You are an assistant"}        
        ],
        
        })
    )
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    return content



    

def open_router_chatgpt_4o(system_content,user_content):
    response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "openai/chatgpt-4o-latest", # Optional
        "messages": [
        {"role": "user", "content": user_content},
        {"role": "system", "content": system_content}        
        ],
        
    })
    )
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    return content





def open_router_chatgpt_4o_mini(system_content,user_content):
    response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "openai/gpt-4o-mini", # Optional
        "messages": [
        {"role": "user", "content": user_content},
        {"role": "system", "content": system_content}        
        ],
        
    })
    )
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    print(content)
    return content


def open_router_meta_llama_llama_3_2_3b_instruct_free(text):
    response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "meta-llama/llama-3.2-3b-instruct:free", # Optional
        "messages": [
        {"role": "user", "content": text}
        ],
        
    }))
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    print(content)
    return content


def open_router_qwen(system_content,user_content):
    response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
        "Authorization": read_bearer_key(),
        "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "qwen/qwen-2.5-72b-instruct", # Optional
        "messages": [
        {"role": "user", "content": user_content},
        {"role": "system", "content": system_content}        
        ],
        
    })
    )
    responsejson = response.json()
    print(responsejson)
    choices = responsejson['choices']
    message = choices[0]['message']
    content = message['content']
    print(content)
    return content




"""
f = open('opusanswer.json','r',encoding ='utf-8')
l = f.read()
f.close()
parserouterjson(json.loads(l))
"""
    
if __name__ == "__main__":
    
    open_router_chatgpt_4o("You are a Cantonese language expert, specializing in correcting errors in transcriptions based upon context.",'''
    Here is a transcription. Each word is on a new line. Give the lines where you think there are mistakes and what the proper word should be:
    


 ''')
    
    #do_opus_questions()
    #print(do_open_opus_questions('what is the meaning of båt in swedish?'))