import random
import re
import time
import json
import subprocess
from typing import List, Dict

import boto3
from newspaper import Article, build
import openrouter
import textprocessing
import ssml
import os




def split_long_text(text: str, max_length: int = 3000) -> List[str]:
    """
    Split a long text into chunks of approximately max_length characters,
    breaking at sentence boundaries.
    """
    sentences = re.split(r'(?<=\.) ', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def split_text(text: str, max_length: int = 1500) -> List[str]:
    """Split text into manageable chunks."""
    sentences = re.split(r'(?<=[。]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + "。"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "。"

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def split_text(text: str, max_length: int = 1500) -> List[str]:
    """Split text into manageable chunks."""
    sentences = re.split(r'。', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + "。"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "。"

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def split_ssml_among_tags(text:str):
    firstparts=text.split('>')
    l = []
    for pi in firstparts:
        l.append(pi+'>')
    return l

import urllib.parse

import hashlib

def md5_signature(input_string):
    """
    Generate an MD5 signature for the given string.

    Args:
        input_string (str): The string to hash.

    Returns:
        str: The MD5 hash of the string in hexadecimal format.
    """
    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    
    # Update the hash object with the bytes of the string
    md5_hash.update(input_string.encode('utf-8'))
    
    # Return the hexadecimal representation of the hash
    return md5_hash.hexdigest()


def filename_from_string(astr):        
    path = md5_signature(astr) + ".mp3"
    return path

def remove_ssml_from_text(txt):
    clean = txt.replace('shortbreak','')
    clean = clean.replace("<break time=\"0.2s\"/>","")
    clean = clean.replace("<break time=\"0.1s\"/>","")
    clean = clean.replace("<break time=\"0.5s\"/>","")
    clean = clean.replace("<break time=\"1.0s\"/>","")
    return clean

def build_audio_compose(text:str):
    parts = split_ssml_among_tags(text)
    dictionary = {}
    dd = []
    textparts = []
    for p in parts:
        stringkey = filename_from_string(p)
        if not stringkey in dictionary.keys():
            dictionary[stringkey] = p
    for p in parts:
        textparts.append(remove_ssml_from_text(p))
        dd.append( filename_from_string(p) )
    print("Unique strings " + str(len(dictionary.keys())) + "\n")
    return [dd,dictionary,textparts]

mp3cachedirectory = '/home/erik/mp3cache'

def create_files_in_audio_compose(compose):
    session = boto3.Session(region_name='us-east-1')
    polly_client = session.client('polly')

    for i in compose[1].keys():
        file_path = mp3cachedirectory + '/' + i
        if  os.path.isfile(file_path) == False:
            try:
                text =  '<speak><break time=\"0.5s\"/>' + compose[1][i] + '</speak>'
                text =text.replace('shortbreak','<break time=\"0.2s\"/>')
                response = polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat='mp3',
                    VoiceId='Hiujin',
                    Engine='neural',
                    TextType='ssml'            
                )
                with open(file_path, 'wb') as file:
                    file.write(response['AudioStream'].read())    
            except Exception as e:
                print(str(e))
                print("SSML " + text)
    return None

from pydub import AudioSegment

def assemble_audio_files(filename,compose):
    audio_segments = []
    textsegments = []
    cnt = 0
    timecount = 0
    for i in compose[0]:
        try:
            temp_file =  mp3cachedirectory + '/' + i
            texttxt = textprocessing.split_text(compose[2][cnt])
            mp3audio = AudioSegment.from_mp3(temp_file)
            textsegments.append([timecount,texttxt])
            timecount+=mp3audio.duration_seconds
            audio_segments.append(mp3audio)
        except Exception as e:
            print(str(e))
        cnt+=1
    
    combined = sum(audio_segments)
    combined.export(filename, format='mp3')
    f = open(filename+".subtitle",'w',encoding='utf-8')
    f.write(json.dumps(textsegments))
    f.close()
    print(f"MP3 file created successfully: {filename}")

    
def cantonese_text_to_mp3(text: str, output_file: str) -> None:
    """Convert a string of text to an MP3 file using AWS Polly."""
    session = boto3.Session(region_name='us-east-1')
    polly_client = session.client('polly')

    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Hiujin',
            Engine='neural',
            #TextType='ssml'            
        )

        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"MP3 file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred while creating MP3: {e}")


def create_and_upload_files(normal_text,chunk: str, index: int) -> None:
    """Create MP3 and hint files, then upload them."""
    splits = textprocessing.split_text(normal_text)
    filename = f"spokenarticle_news{time.time()}_{index}.mp3"
    hint_filename = f"{filename}.hint.json"

    cantonese_text_to_mp3(chunk, filename)

    with open(hint_filename, "w") as f:
        json.dump(splits, f)

    for file in [filename, hint_filename]:
        scp_command = f"scp {file} chinese.eriktamm.com:/var/www/html/mp3"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error uploading {file}: {result.stderr}")


def get_top_news(url: str, num_articles: int = 20) -> List[Dict[str, str]]:
    """Get top news articles from a given URL."""
    source = build(url, memoize_articles=False)
    top_news = []

    articles = source.articles
    random.shuffle(articles)

    for article in articles[:num_articles]:
        try:
            article.download()
            article.parse()
            top_news.append({
                'title': article.title,
                'url': article.source_url,
                'text': article.text
            })
        except Exception as e:
            print(f"Error processing article: {e}")
    return top_news


def summarize_news(news_text: str) -> str:
    """Summarize the news text using OpenRouter."""
    try:
        """        summary = openrouter.open_router_chatgpt_4o_mini(
            "You are an assistant who summarizes large amounts of texts that include news.",
            f"Pick out the news from the following text, write a summary of 600 words of each news in simple English that someone with a B1 level can understand. Ignore any news related to sports.\n{news_text}"
        )"""      
        api = openrouter.OpenRouterAPI()  
        count = 0
        ar = []
        while count < 3:
            try:
                summary = api.do_open_opus_questions(
                    f"Pick out the news from the following text, write a summary of 600 words of each news in simple English that someone with a B1 level can understand. Avoid using subordinate clauses or dependent clauses. Ignore any news related to sports. return the news in json format like this [[title1,summary1],[title2,summary2],...]. Only return json, no other text. \n{news_text}"
                )        
                bsummary = summary.replace('[[title1,summary1],[title2,summary2],...]','')
                bsummary = bsummary[bsummary.find('['):]
                ar = json.loads(bsummary)
                count = 10
            except Exception as e:
                print(str(e))
                count+=1
                                
        if len(ar) == 1:
            ar = ar[0]
        rr = []
        for r in ar:
            rr.append(r[0] + '\n' + r[1])
        return rr
    except Exception as e:
        print(f"Error summarizing news: {e}")
        return ""


def translate_to_cantonese(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        api = openrouter.OpenRouterAPI()          
        translated = api.do_open_opus_questions(
            f"Translate the following text to spoken Cantonese, like how people actually speak in Hong Kong. Make it so simple that a 7-year-old can understand it. Personal Names, place names (Toponyms), Brand names, organization names and product names in English. Do not include pronouncation guide. Only return the text, do not add comments. Here is the text:\n{text}"
        )
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""


def shorten_sentences(text):
    parts = split_text(text,2000)
    ret = ''
    for p in parts:        
        task = """Please revise this text by:\n
            Replacing comma-separated clauses (，) with separate sentences (。) where meaning permits.\n
            Keep core meaning and key information intact. Do not add any comment, just respond with the rewritten text. Return the whole text.\n\nHere is the text: """ + p
        try:
            api = openrouter.OpenRouterAPI()                  
            shortened = api.do_open_opus_questions(task)
            ret+= shortened
        except Exception as e:
            print(f"Error translating to Cantonese: {e}")
            return ""
    return ret
    
def extract_keywords_from_sentence(sentence):
    extr = "Make a list of words in the sentence provided and return a json-array in the following format [ {\"word\":word,\"translation\":english translation},...]. Here is the sentence: " + sentence
    api = openrouter.OpenRouterAPI()          
    # select free sometimes        
    result = api.open_router_qwen_25_72b(extr)
    result = result[result.find('['):]
    result = result[:result.find(']')]+']'    
    return json.loads(result)


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

    
def extract_keywords(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        api = openrouter.OpenRouterAPI()                  
        translated = api.do_open_opus_questions(
            f"Extract 20 keywords and difficult words necessary to understand this text. Return a list of those words in this json format [[keyword1,explanation in Cantonese that a child can understand,english translation],...]. Return only the json, no other text. Here is the text:\n{text}"
        )
        return json.loads(translated)
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""


def wrap_in_ssml(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        api = openrouter.OpenRouterAPI()                  
        translated = api.open_router_meta_llama_llama_3_1_8b_instruct(
            f"Convert this text into SSML format. Use pauses to make it more suitable for listening. Only return the SSML. Here is the text:\n{text}"
        )
        idx = translated.find('<speak>')
        translated = translated[idx:]        
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""


def findsentence_containing_word(word,sentences):
    try:
        result = []
        for s in sentences:
            if s.find(word) != -1:
                result.append(s)
        return random.choice(result)
    except Exception as e:
        print(str(e))
        return ""
    

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


import requests

def add_sentence_to_translated( sentence):
    
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


import stringstack
import frequencytools
def translate_simplify_and_create_mp3(news:List) -> None:
    """
    Translate the given text to Cantonese, simplify it, create an MP3, and upload it.
    If the text is longer than 3000 characters, it's split into smaller parts and
    processed in series.
    """    
    words_thats_been_given = []
    for n in news:
        try:
            render_to_cantonese_audio_and_upload(words_thats_been_given, n)
        except Exception as e:
            print(str(e))
    return None

def render_to_cantonese_audio_and_upload(words_thats_been_given, n):
    clean_text, sml_text = make_sml_from_english_text(words_thats_been_given, n)
    make_and_upload_audio_from_sml(clean_text, sml_text)


def render_from_chinese_to_audio_and_upload(words_thats_been_given, n,prefix=''):
    clean_text, sml_text = make_sml_from_chinese_text(words_thats_been_given, n)
    make_and_upload_audio_from_sml(clean_text, sml_text,prefix)


def make_sml_from_english_text(words_thats_been_given, n):
    translated = shorten_sentences(translate_to_cantonese(n))
    return make_sml_from_chinese_text(words_thats_been_given, translated)


import difficultlevel

def make_sml_from_chinese_text(words_thats_been_given, translated):
    sentences = textprocessing.split_chinese_text_into_sentences(translated)
    # add to explanation work
    sml_text = ''
    clean_text = ''
    fcounter = frequencytools.FrequencyCounter()
    for s in sentences:
        add_sentence_to_translated(s)

    difficultlevel.add_list_to_examples(sentences)
    for s in sentences:
        sml_text += 'shortbreak'+s+'shortbreak' 
        clean_text +=  s + '\n'
    sml_text += "<break time=\"1.0s\"/>"    
    for s in sentences:
        sml_text += s + "<break time=\"1.0s\"/>"
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
                        sml_text += 'shortbreak'+s
                        cnt = 0
            sml_text += 'shortbreak'+ s + "<break time=\"0.2s\"/>"
            sml_text += 'shortbreak'+ s + "<break time=\"0.2s\"/>"                    
        except Exception as e:
            print(str(e))
        clean_text +=  s + '\n'
                            
    for s in sentences:
        sml_text += 'shortbreak'+ s + "<break time=\"1.0s\"/>"
        clean_text +=  s + '\n'
    sml_text += ' <break time=\"1.0s\"/>'
    fcounter.save_changes()
    return clean_text,sml_text

def make_and_upload_audio_from_sml(clean_text, sml_text,prefix):
    audio_compose = build_audio_compose(sml_text)
    create_files_in_audio_compose(audio_compose)
    filename = f"spokenarticle_news{time.time()}_{prefix}.mp3"
    splits = textprocessing.split_text(clean_text)
    print(clean_text)
    hint_filename = f"{filename}.hint.json"
    assemble_audio_files(filename,audio_compose)
        #ssml.synthesize_ssml_to_mp3(sml_text,filename)
        
    with open(hint_filename, "w") as f:
        json.dump(splits, f)

    for file in [filename, hint_filename]:
        scp_command = f"scp {file}* chinese.eriktamm.com:/var/www/html/mp3"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error uploading {file}: {result.stderr}")

def process_file_content(file_path: str) -> None:
    """
    Read content from a file and process it using translate_simplify_and_create_mp3.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"Successfully read content from {file_path}")
        print(f"File content length: {len(content)} characters")
        
        translate_simplify_and_create_mp3(content)
        
        print(f"Finished processing content from {file_path}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except IOError as e:
        print(f"Error reading the file {file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {file_path}: {e}")

def process_news(url: str) -> None:
    """Process news from a given URL."""
    try:
        top_news = get_top_news(url)
        total_news = '\n'.join(f"{news['title']}\n{news['text']}" for news in top_news)

        summary = summarize_news(total_news)
        if not summary:
            return

        translate_simplify_and_create_mp3(summary)

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

def main():
    urls = [
        'https://www.nbcnews.com/',
        'https://www.bbc.com/',
        'https://www.taiwannews.com.tw/',
        'https://www.cnn.com/',
                
    ]  # Repeated 11 times to match the original list

    for url in urls:
        process_news(url)

    # Example usage of the new function with a file
    #file_path = "sample_text.txt"
    #process_file_content(file_path)

if __name__ == "__main__":
    main()
    exit(-1)
    lol = []
    orgtext = """
各位讀者各位聽眾大家好 我是利細文 今日是2024年11月19日 今日想講下在中國大陸發生的 他們稱之為遍地彰獻中的一個社會現象 我見到有不少分析都話 因為在中國大陸入邊 好多人係有冤無路數 因為積壓咗嘅憤怒 令到佢哋係會對無辜嘅人 或者係根本唔相干嘅人 去發洩佢哋呢一股憤怒 咁但但我自己就覺得 可憐之人必有好惡之處 這種無差別的攻擊其他人 其實是絕對不應該同情 你同情他 是不是等於鼓勵有更加多這樣的行為呢 雖然我說不同情他們 但又不代表我不會去嘗試了解發生什麼事 有另外一種分析就是 在中國大陸現在充滿著一種仇恨的情緒 他們這種仇恨幾乎是一種集體的情緒 他們又好憎美國好憎日本 以至到他們連自己好憎什麼都不是很清楚 這樣這個解釋令我想起在George Orwell的《1984》中 有一個情節就叫做兩分之一 兩分之一 一個解釋令我想起在George Orwell的《1984》入邊 有一個情節就叫做兩分鐘的仇恨 就是說那些人一起望著電視機 然後很澎湃的無敵放肆的去找些東西發洩 找些東西去罵�,制造敌人 因为在政治上,当你有共同的敌人的时候 你就能够团结大多数 这个情节又令到我想起 纳粹德国的时候有一个作家叫Dietrich Bonhoeffer 他寫了一篇文章去批評群眾愚昧 為何他會寫這篇文章呢? 講講背景 其實Bonhoeff�在1930年代 因為見到當時的納粹德國充滿仇恨 他當時公開批評社會現象 而他亦因為這個原因 被當時納粹德國的秘密警察 被抓去坐牢,送去集中營 以下這一篇我用廣東話翻譯的分享 其實就是他在獄中所寫的一些書信 Bonhoeffer 說 愚蠢比邪惡更加危險 是善良的一個更大敵人 我們可以對抗邪惡 因為我們可以揭露邪惡的問題 甚至有時候我們可以用武力去制止這些邪惡的發生 邪惡本身是会自己瓦解 因为邪恶的想法 多少都会令人在心里 留下一些不安的感觉 但是我们对这种群众的愚昧 就真的无法了 你抗议他也不是 你甚至乎用武力制止他 也一样是没用的 你对这些愚昧的群众去讲道理 他们会当听不到 你将事实放在他们眼前 告诉他们他们的错误 他们甚至会反过来说你是偏见 又或者你所说的事实,根本他们是不会接受 你将蠢人和衰人去比较的话 你就会发现这些愚昧的民众 他们是非常自信 而且你很容易激怒他们 令到自己的安全都受到威胁 令到他们去攻击你 所以我们面对着这些 愚昧的群众的时候 我们是要更加小心 永远都不要尝试 所以我们面对着这些愚昧的群众的时候 我们是要更加小心 永远都不要尝试用理由去说服这班人 因为你这样做是没有意义的 也是很危险的 但是我们如果想想要怎样战胜这种愚昧 首先第一个问题就是 我们要知道它的本质是什么 有一点可以肯定的就是愚昧的本质不是因为智力的问题 而是人性的问题 其实有些人的智力是非常之高 但是他们是可以很愚昧 有些人他未必智商很高 但是其实一点都不愚昧的 有些人他未必智商很高 但其實一點都不愚昧 有時候我們會發現 這種愚昧根本不是先天的缺陷 而是在某一種特定的社會環境之下 人會集體地變得愚昧 是他們自己令变得愚昧 是他们自己令到自己变得愚昧 我们如果进一步的看 如果有些人是愿意独立的生活 他们会比较少出现这些愚昧的行为 一些愚昧的思想 一些愚昧的倾向 反而是那些 强迫自己要融入群体的人 很容易就会表现出 有这些各种愚昧的缺陷 所以与其说愚昧是一个心理学的问题 倒不如说這是一個社會學問題 這是一種特定的歷史環境之下 對人類影響出來的結果 是因為外在條件的關係出現的心理現象 如果再細心一點看 其實每一次你有強權的崛起,无论是政治的,或是宗教的,它都会感染了大量的人,令他们变得愚昧。 我们可以说这是一个社会心理学的定律,就是强权统治 必须要有愚昧的群众去配合 这个现象不是因为人类的理解能力 他们的智力退化 而是因为强权崛起的影响之下 这些人不再有自我的存在 他們或多或少是有意識地放棄獨立思考 當你跟這些人對話的時候 你發覺你根本不是跟他對話 開口埋口就是那些口號、標語 好像中了槓頭 甚至乎在旁人眼中 他做出來的行為是不斷的 侮辱、貶低自己 然後他就會變成一個沒有思考的工具 可以做出一些邪惡的行為 而他自己是不會意識到 他自己做的事是有多邪惡的行为 而他自己是不会意识得到 他自己做的事是有多邪惡 这个也是愚弄大众最危险的地方 因为它可以完全摧毁了人性 也是因为这个原因 如果我们要克服这种集体的愚昧 要克服呢種 集體嘅愚昧 首先要做嘅唔係去教化呢啲愚昧嘅群眾 而係 我哋一定要面對一個現實 就係只有當枷鎖喺佢哋思想上邊嘅 束縛 係完全被去除咗之後 佢哋们才可以由内至外得到解放 而在我们能够重建这种自由的氛围之前 我们要放弃去说服这些愚昧的群众 甚至乎在这种情况之下 如果我们尝试去了解群众的真正想法是怎样 最终都是徒劳无功 是没意思 圣经说 敬畏上帝是智慧的开端 我们要克服愚昧去解放我们的思想 重点是在于我们可以在上帝面前过负责任的生活 而当我想到这一点的时候 至少给到我一些安慰 因为他告诉我 我们不需要相信人在大多数情况之下都是愚昧的 最终人民是不是愚昧 就取決於掌權的人 他是需要有 一些愚昧的人 還是他需要一些 有獨立思考有智慧的人 以上是 班霍佛寫的文字 我作出 這個分享 我覺得都要有啲補充 首先就係佢作為一個基督徒 佢係一個牧師 咁好自然呢去到最後就會講返宗教 我諗有啲冇宗教信仰嘅人會覺得 宗教本身就已經是一種愚昧 覺得Ben Hofer是自相矛盾 而我自己的看法就是 任何人都會有些信仰 有些人的信仰是宗教 有些人的信仰是政府 有些人的信仰是科學的方法 有不同信仰的人都总是会觉得 和自己信仰不一样的人是不可理喻 因为信这件事本身是非理性的 我们有没有可能做到完全绝对的理性呢? 在这个频道经常有人跟我留言说�對地理性呢 喺呢個頻道經常有人同我留言就話 你太過理性啦 你唔可以用常人嘅道理去了解呢啲人㗎 你唔可以用常人嘅道理去了解某一啲獨裁者㗎 但係我想講嘅一點就係 無論係獨裁者 但是我想说的一点就是 无论是独裁者或是群众 无论他们在想什么 他们都不可能摆脱到现实 现实是对任何思想最终的验证方法 我不是说说没有理想 现实和理想一定是有一个距离 问题就是 当你要由现实迈向你的理想的方向 究竟你要做些什么 最终还是要基于现实 所以当我们看到到有些人 或者有些社会 他们的思想方法 他们的行为 完全和现实不符的话 那我们就知道 这一帮人 这一帮群众 其实他们一样 都是处于一种很危险的状态 很容易被人利用 很容易變成剛才所講的那些不會思考的人慾工具 去到最後其實最重要的一點就是 當群眾不願意思考的時候 我們至少都要保持自己個人的思想维生 要保持我们自己的清醒 有些人很容易在这种群众的氛围之下 很容易会出现一种反作用力 而这些反作用力有时候会 衍生出有另外一群人出现 我们见到所谓的社會撕裂 就是這樣來的 講到這裡 其實我相信 有些就算看法 和我不一樣的人 都會覺得 那你們這幫人 是不是一樣都有 這種思想的盲點 是不是一樣都是愚昧呢 你所追求的獨立思考 你所追求的自由 你所追求的独立思考 你所追求的自由 你所追求的自主 是不是一样都是一种理想 其实这个问题 我是不断都有反省 我不是说因为知道现实是不自由的 所以我就放弃对自由这个价值的追求 我知道没有人是能够�對地獨立思考 我們一定都是受到其他人的想法的影響 問題是我們會不會對於這些想法能夠作出反省 能夠對自己周遭的社會環境 發生的各种事情 能够有一种反省 我相信这个已经是摆脱愚昧的第一步 如果我们连反省的自由都没有的话 这一个就真是最危险的情况 而在某些社會某些神奇國度 好似掌握了一切權力 甚至乎有非常龐大影響力的人 他們是不但止不願意自我反省 甚至乎是不可以被其他人對他們作出任何批評 不願意反省和不讓人作出批評 這個本質上就已經是愚昧的表現 講返遍地張獻忠事件 其實這個很明顯就是反映了這個社會已經有很嚴重的問題 當我這樣講的時候 一定是會有些人會覺得 美國很好嗎? 英國很好嗎? 歐洲很好嗎? 但就像 Bonhoeffer 在他文章裡面所說 有些愚昧的人 就算把事實放在他們眼前 他們都會說 這些只是個別例子 呢啲只不過係你嘅偏見 我係利細文 如果今日嘅分享能夠畀到你一啲唔同嘅睇法唔同嘅觀點 希望你可以向更加多朋友推介我呢個頻道 今日嘅分享暫告一段落多謝你嘅時間多謝你嘅收聽下次再
"""
    text = textprocessing.make_sure_traditional(orgtext)
    shortened = shorten_sentences(text)
    parts = split_text(shortened,500)
    cnt = 0
    for p in parts:
        if cnt == 4:
            render_from_chinese_to_audio_and_upload(lol,p,prefix="yt3_"+str(cnt))
        cnt+=1
    #   