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

from texttoaudio import filename_from_string


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


import texttoaudio

def create_files_in_audio_compose(compose):
    session = boto3.Session(region_name='us-east-1')
    polly_client = session.client('polly')

    for i in compose[1].keys():
        file_path = texttoaudio.mp3cachedirectory + '/' + i
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

def assemble_audio_files(filename,compose,postprefixaudio = None):
    audio_segments = []
    textsegments = []
    cnt = 0
    timecount = 0
    additional_audio = None
    if postprefixaudio != None:
        additional_audio = AudioSegment.from_mp3(postprefixaudio)
        audio_segments.append(additional_audio)
    for i in compose[0]:
        try:
            temp_file =  texttoaudio.mp3cachedirectory + '/' + i
            texttxt = textprocessing.split_text(compose[2][cnt])
            mp3audio = AudioSegment.from_mp3(temp_file)
            textsegments.append([timecount,texttxt])
            timecount+=mp3audio.duration_seconds
            audio_segments.append(mp3audio)
        except Exception as e:
            print(str(e))
        cnt+=1
        
    if additional_audio != None:
        audio_segments.append(additional_audio)
        
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
            f"Pick out the news from the following text, write a summary of 600 words of each news in simple English that someone with a B2 level can understand. Ignore any news related to sports.\n{news_text}"
        )"""      
        api = openrouter.OpenRouterAPI()  
        count = 0
        ar = []
        while count < 3:
            try:
                summary = api.do_open_opus_questions(
                    f"Pick out the political news from the following text, write a summary of 600 words of each news in English that someone with a B2 level can understand. Avoid using subordinate clauses or dependent clauses. Ignore any news related to sports. return the news in json format like this [[title1,summary1],[title2,summary2],...]. Only return json, no other text. \n{news_text}"
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

from texttoaudio import make_sml_from_chinese_text 

def render_to_cantonese_audio_and_upload(words_thats_been_given, n):
    clean_text, sml_text = make_sml_from_english_text(words_thats_been_given, n)
    make_and_upload_audio_from_sml(clean_text, sml_text,"")


def render_from_chinese_to_audio_and_upload(words_thats_been_given, n,prefix=''):
    clean_text, sml_text = make_sml_from_chinese_text(words_thats_been_given, n)
    make_and_upload_audio_from_sml(clean_text, sml_text,prefix)


def make_sml_from_english_text(words_thats_been_given, n):
    translated = shorten_sentences(translate_to_cantonese(n))
    return make_sml_from_chinese_text(words_thats_been_given, translated)



import difficultlevel
from texttoaudio import get_pause_as_ssml_tag,surround_text_with_short_pause


def make_and_upload_audio_from_sml(clean_text, sml_text,prefix,postprefixaudio=None):
    audio_compose = build_audio_compose(sml_text)
    create_files_in_audio_compose(audio_compose)
    filename = f"spokenarticle_news{time.time()}_{prefix}.mp3"
    splits = textprocessing.split_text(clean_text)
    print(clean_text)
    hint_filename = f"{filename}.hint.json"
    assemble_audio_files(filename,audio_compose,postprefixaudio)
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
        'https://www.bbc.com/',
        'https://www.cnn.com/',
        'https://www.nbcnews.com/',
        'https://www.taiwannews.com.tw/',
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
。你係眾望所歸無得留低。你要一筆Out銷。Goodbye。各位聽眾各位讀者大家好。我是李細文。今日係2014年12月5號星期四。剛才播果段聲帶唔知大家有冇啲印象呢。你係眾望所歸無得留低,你要一筆Out銷,Goodbye。呢個係好多年前喺香港嘅一個遊戲節目。叫做一筆Out銷,英文就叫做The。weakest。link。呢個遊戲我相信大家可能都有啲印象。而家喺美國同英國都仲有做緊。點解播返呢段聲帶畀大家聽勾起大家嘅回憶呢。話說我睇新聞見到楊潤雄同林世雄。兩個政治問責局局長被忽然撤職。一筆勾銷。令到我想起這個遊戲。如果問香港的朋友。有哪些局長是要一筆勾銷要離場呢。就恐怕名單會涵蓋所有現任的司局長。但是我在這個一筆勾銷嘅遊戲。The。weakest。link得到好多啟發。尤其是關於政治。如果冇睇過呢個遊戲嘅朋友。我簡單講下個遊戲玩法。每一集呢個一筆勾銷嘅節目。會有九個參賽者。咁佢哋就就要在限时之内。轮流答一些常识时事的问题。每个参赛者轮流作答。跟着落嚟答问题。就可以累积到。更加高的奖金。而每个参赛者。他可以在作答问题之前。听问题之前。就决定是不是要bank咗嗰啲钱。因为一bank咗呢。累积奖金嘅金额呢就会由最低开始。如果你冇bank到嗰啲钱。而你又答错问题呢。咁之前累积落嚟嘅所有奖金呢就会冇哂㗎喇。所以每一个答问题嘅人。可以选择拨一铺去拨更多的累积奖金。或者他bank了然后又由最低的奖金额开始再累积。但是这个游戏最好看最精彩的地方就是每一个回合之后。这么多位仍然在台上玩的參賽者。就可以投票選將其中一個參賽者淘汰。這個遊戲原本的名字叫做。The。weakest。link。即是說理論上大家就應該每一輪淘汰一個最沒有常識的隊友。轮就淘汰一个最无常识的队友。但是这个是一个淘汰赛。意思就是最后只会得番两名参赛者。而最后两名参赛者呢。就会以答岸问题最多个一个参赛者。就会拿哂所有的累積獎金。如果從經濟學上的博弈論去了解這個遊戲。它有趣的地方就是每個參賽者其實同其他既有合作的關係。但亦都有競爭的關係。當然你可以最理想的情況就是。一直淘汰到最后。就是最强的两个参赛者在最后一轮就做公平的竞赛。但是呢以我看这个节目那么多次的经验。通常都不会出现一个最理想的状态。虽然最初呢一些最弱势勢嘅參賽者就會被淘汰。但係去到中後段呢。大概去到第四round左右。就一啲強勢好叻好有常識嘅參賽者。就會畀其他相對差少少嘅參賽者。係甲粉去淘汰咗佢。因為每個參賽者自己都會諗住去到最後一輪。佢可以係相對上呢就提早去將佢最強勁嘅對手呢就率先淘汰咗。呢個遊戲其實同政治嘅現實係非常之相似。講返而家呢個特區政府嘅情況。理論上李家超就應該喺身邊就安置啲最叻嘅人。建立一個最強勁嘅團隊。然後話畀北京知自己做得好好。問題就係如果喺佢嘅團隊入邊有人嘅能力顯得比佢更高嘅時候。就好容易去到下一屆去選行政長官嘅時候。佢未必有機會留低,反而比其他人一筆勾銷。多爾在特區政府高官問責制遊戲入面。通常最叻同埋最咋嘅人都係不容於團隊入面。至於楊潤雄同林世雄呢兩個人究竟係能幹定係無能呢就相信大家心目中都有一個判斷。但係如果按照返呢個博弈倫嘅推斷。嚟緊嘅日子喺特區政府入邊呢官員會究竟點樣去表現呢。喺呢個動態平衡之下你又唔可以表現得太過無能。你都唔可以表現得太過能幹。所以出現嘅情況呢就係所有人都係嘗試令到自己唔係最叻嗰個。亦都唔係最咋嗰個。你有足夠嘅價值去繼續留喺個遊戲入邊。但係與此同時你又唔可以表現得自己太過能幹太過有為。亦即係我哋經常所講嘅唔可以攻高蓋主。呢種咁嘅情況唔單止係政治環境入邊有。好多時大機構大企業都有咁嘅情況。呢個亦都解釋咗點解當一個機構一個企業大到某一個程度嘅時候。好多時就會出現融財係能夠步步高升。反而係啲好有能力呀或者好有想法嘅人呢最終都係不容。於呢啲咁�於團隊入面。另外一點就是越是人治機構。就越容易出現逆向的淘汰。其實好多研究政治學者一早都發現。很多專制獨裁的社會。很多時在獨裁者未上台前,。被人的感覺都是沒有殺傷力,甚至是親和力很強的人。。但一旦成功成為獨裁者後,。他們的行為表現會完全180度轉變。在這個日常政治學的頻道入邊。我經常都提到。就是獲得權力的過程。用的手段、策略。同埋你要去保留你自己的權力。去行使你的權力的時候。態度是非常之唔一樣。我自己嘅觀察就係。能夠具備兩種能力嘅人呢。係少之又少。即係話喺未上位之前。係能夠韜光養晦。但係去到一奪得權力嘅時候。就心狠手辣。歷史上有冇啲咁嘅例子呢。我諗好多人會用德川家康做例子。另外一個延伸思考就係。奪權嘅時候呢。通常呢啲奪權嘅團隊呢。一樣喺入邊都有類似嘅動態平衡。換句話說每個團隊入面。係幫這個奪權者去打江山嗰班人。佢哋入邊當然有啲人係能幹啲。有啲人係無能啲。但係當奪權成功之後呢。往往就係最有能力嗰班人。就最先被淘汰。而留下的就是逆向選擇。就會選一些平庸但又不是最差的那班人。我想所謂的政治智慧。好多時就是怎樣在表現自己能力的同時。又不會表現得自己與的同時。又不會。表現得自己與眾不同。唔會太過展示自己的實力。唔會太過張揚。講返呢個特區政府嘅政治現實啦。因為佢哋每一個人。最終可以做得到嘅呢。亦都只不過係香港特區政府嘅政治任命官員。咁呢班政治任命官員佢係威脅唔到北京嘅。喺個制度上邊設計呢班人只可以喺香港呢一個有限嘅空間。去進行佢哋自己嘅政治鬥爭。北京就唔會話避忌有一個好能幹嘅香港特區行政長官。問題就係呢一個能夠爬上呢個位嘅人呢。往往亦都唔係真係最叻個一個。基本上每一個做緊行政長官嘅人呢。都一定係會首先將佢身邊最大威脅嗰個對手呢去淘汰咗就令自己有機會連任。而呢一個現象往往都會喺行政長官嘅第一個任期入面出現。如果諗返轉頭喺19年之後林鄭月娥首先除去的對手。就是張建宗,當時的政務司司長。再數上一屆政府,梁振英的時代。正正就是他沒有去對付身邊兩大對手。一個叫做曾俊華,一個叫林鄭月娥。如果我們這樣看,解釋得到為什麼當年林鄭月娥未得到北京的祝福之前。就一直擺出一套,我都是一個師奶,我打算照顧兒子,打算和老公游山玩水的態度。她有沒有野心?她一定有野心。但梁振英將她全部精力放在曾俊華身上。如果我們再數上一屆政府當時的曾蔭權。她有一個特別的情況。因為她第一個任期是接替董建華的餘下任期。然後佢其實嚴格嚟講只係喺2007年當選過一次行政長官。而佢亦都知道自己最多亦都只係做到2012年就要自己落台。所以當時佢亦都有宣佈係唔會再參加行政長官選舉。如果我哋再數上一任行政長官。即係董建華。咁更加明顯啦。就係佢當時第一個去除嘅競爭對手。就係陳方安生。而如果大家記得呢。就係陳方安生以私人理由。辭去政務司司長職位後。由曾蔭權接替。當時由於董建華。推行所謂高官問責制。曾蔭權沒有直接指揮。其他司局長的能力。當時傳媒稱他為無兵司令。曾蔭權沒有直接指揮其他司局長嘅能力。亦都當時我記得傳媒呢。係稱佢為無兵司令。甚至乎有人話曾蔭權有手好閒呀冇嘢做呀。素佳大隊長呀等等。其實呢啲就係剛才所講。你要表現得自己有用。但係又唔會功高震主的另外一個幾好的案例。但無奈的就是。好似曾蔭權咁識做嘅人。佢喺佢任期就快屆滿嘅時候。都係接連咁畀人爆佢同商界利益輸送的各種醜聞。包括他去澳門新濠天地賭場出席晚宴。坐人家的私人飛機遊艇。在深圳租的一個單位。是由一個全國政協黃楚標。用一個很低租金租給他。各種利益輸送問題。但以我在傳媒的經驗。對於曾蔭權各種醜聞消息。如何流出給公眾見?。背後一定有人推動。而且時間上是這麼密集的話。絕對不是一個偶然。今日的分享希望可以給到大家一個不同的角度。去了解政治的現實是怎樣去操作。希望今日大家的時間過得充實如果你覺得我嘅分享係值得向你。朋友推介嘅話呢個係對我最大嘅支持。多謝大家嘅時間多謝大家收聽我係李世民下次再會"""
    text = textprocessing.make_sure_traditional(orgtext)
    shortened = shorten_sentences(text)
    parts = split_text(shortened,500)
    cnt = 0
    for p in parts:
        render_from_chinese_to_audio_and_upload(lol,p,prefix="yt4_"+str(cnt))
        cnt+=1
    #   