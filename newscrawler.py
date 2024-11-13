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
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

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

def build_audio_compose(text:str):
    parts = split_ssml_among_tags(text)
    dictionary = {}
    dd = []
    for p in parts:
        stringkey = filename_from_string(p)
        if not stringkey in dictionary.keys():
            dictionary[stringkey] = p
    for p in parts:
        dd.append( filename_from_string(p) )
    print("Unique strings " + str(len(dictionary.keys())) + "\n")
    return [dd,dictionary]


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

    for i in compose[0]:
        try:
            temp_file =  mp3cachedirectory + '/' + i
            audio_segments.append(AudioSegment.from_mp3(temp_file))
        except Exception as e:
            print(str(e))

    combined = sum(audio_segments)
    combined.export(filename, format='mp3')
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
            f"Pick out the news from the following text, write a summary of 600 words of each news in simple English that someone with a B2 level can understand. Ignore any news related to sports.\n{news_text}"
        )"""      
        api = openrouter.OpenRouterAPI()  
        count = 0
        ar = []
        while count < 3:
            try:
                summary = api.do_open_opus_questions(
                    f"Pick out the news from the following text, write a summary of 600 words of each news in simple English that someone with a B2 level can understand. Avoid using subordinate clauses or dependent clauses. Ignore any news related to sports. return the news in json format like this [[title1,summary1],[title2,summary2],...]. Only return json, no other text. \n{news_text}"
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
            f"Translate the following text to spoken Cantonese, like how people actually speak in Hong Kong. Make it so simple that a 8-year-old can understand it. Personal Names, place names (Toponyms), Brand names, organization names and product names in English. Do not include pronouncation guide. Only return the text, do not add comments. Here is the text:\n{text}"
        )
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""


def shorten_sentences(text):
    task = """Please revise this text by:
        Breaking compound sentences into simple ones
        Replacing comma-separated clauses (，) with separate sentences (。) where meaning permits
        Using active voice where possible
        Removing redundant connecting words like 因為、所以、由於
        Stating the main point first, then supporting details
        Removing repeated ideas
        Using direct verb-object structure instead of descriptive clauses
        Keep core meaning and key information intact. Do not add any comment, just respond with the rewritten text.\n\nHere is the text: """ + text
    try:
        api = openrouter.OpenRouterAPI()                  
        shortened = api.do_open_opus_questions(
                                                           task
        )
        return shortened
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""


def extract_keywords_from_sentence(sentence):
    extr = "Make a list of words in the sentence provided and return a json-array in the following format [ {\"word\":word,\"translation\":english translation},...]. Here is the sentence: " + sentence
    api = openrouter.OpenRouterAPI()          
    # select free sometimes        
    result = api.open_router_qwen_25_72b(extr)
    result = result[result.find('['):]
    result = result[:result.find(']')]+']'    
    return json.loads(result)
    
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



too_common_words = ['美國人','佢哋','佢','但係']

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
def translate_simplify_and_create_mp3(news:List) -> None:
    """
    Translate the given text to Cantonese, simplify it, create an MP3, and upload it.
    If the text is longer than 3000 characters, it's split into smaller parts and
    processed in series.
    """    
    clean_text = ''
    sml_text = ''
    words_thats_been_given = []
    for n in news:
        try:
            translated = shorten_sentences(translate_to_cantonese(n))
            sentences = textprocessing.split_chinese_text_into_sentences(translated)
            # add to explanation work
            for s in sentences:
                add_sentence_to_translated(s)

            for s in sentences:
                sml_text += 'shortbreak'+s+'shortbreak' 
                clean_text +=  s + '\n'
            sml_text += "<break time=\"1.0s\"/>"
            """
            keywords = extract_keywords(translated)
            for k in keywords:
                try:
                    clean_text += k[0] + '\n' 
                    sml_text+= k[0]+'" <break time=\"0.5s\"/>'+k[0]+'" <break time=\"0.5s\"/>'+k[0]+'" <break time=\"1.0s\"/>'+ k[1] + '" <break time=\"0.5s\"/>'+  k[2] + '<break time=\"0.5s\"/>' +k[0] + '<break time=\"1.0s\"/>' + findsentence_containing_word(k[0],sentences) +"<break time=\"1.0s\"/>" 
                    sml_text += ' <break time=\"1.0s\"/>'
                except Exception as ee:
                    print((str(ee)))
            """
            for s in sentences:
                sml_text += s + "<break time=\"1.0s\"/>"
                try:
                    trycount = 0
                    kson = []
                    while trycount < 3:
                        try:                         
                            kson = extract_keywords_from_sentence(s)
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
                        translation = k['translation']
                        if should_word_be_learned(word,translation,words_thats_been_given):
                            words_thats_been_given.append(word)
                            sml_text += "<break time=\"0.1s\"/>shortbreak" + word + 'shortbreak' + translation + 'shortbreak' +word +'shortbreak' + translation +'shortbreak' + word +'shortbreak' + translation +"<break time=\"0.1s\"/>"
                            cnt += 1
                            if cnt > 3:
                                sml_text += 'shortbreak'+s
                                cnt = 0
                except Exception as e:
                    print(str(e))
                clean_text +=  s + '\n'
                            
            for s in sentences:
                sml_text += s + "<break time=\"1.0s\"/>"
                clean_text += 'shortbreak'+ s + '\n'
            sml_text += ' <break time=\"1.0s\"/>'
        except Exception as e:
            print(str(e))
    audio_compose = build_audio_compose(sml_text)
    create_files_in_audio_compose(audio_compose)
    filename = f"spokenarticle_news{time.time()}_0.mp3"
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
        return None

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