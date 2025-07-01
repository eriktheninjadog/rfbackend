#flashcardgenerate.py





import openrouter
import json
import re
import os

flash_card_directory = "/home/erik/flashcards"
class KeyCounter:
    def __init__(self, filename="wb_freq_counter.json"):
        self.counts = {}
        self.filename = flash_card_directory + "/" + filename
        
        if self.filename and os.path.exists(self.filename):
            self.load_from_file()
    
    def increase_count(self, index):
        """
        Increase the count for the given index by 1
        
        Args:
            index (int): The index to increase count for
        
        Returns:
            int: The new count value
        """
        if index not in self.counts:
            self.counts[index] = 0
        self.counts[index] += 1
        return self.counts[index]
    
    def get_count(self, index):
        """
        Get the current count for an index
        
        Args:
            index (int): The index to get count for
        
        Returns:
            int: The count value (0 if index doesn't exist)
        """
        return self.counts.get(index, 0)
    
    def save_to_file(self, filename=None):
        """
        Save counts to a JSON file
        
        Args:
            filename (str, optional): The file to save to. If None, use the instance's filename.
        
        Returns:
            bool: True if successful, False otherwise
        """
        filename = filename or self.filename
        if not filename:
            return False
        
        try:
            with open(filename, 'w+', encoding='utf-8') as f:
                json.dump(self.counts, f)
            
            self.filename = filename
            return True
        except Exception as e:
            print(f"Error saving counts: {e}")
            return False
    
    def load_from_file(self, filename=None):
        """
        Load counts from a JSON file
        
        Args:
            filename (str, optional): The file to load from. If None, use the instance's filename.
        
        Returns:
            bool: True if successful, False otherwise
        """
        filename = filename or self.filename
        if not filename or not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.counts = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading counts: {e}")
            return False
class WordDatabase:
    def __init__(self, database_filename="wb.json"):
        self.words = {}  # Dictionary mapping words to their indices
        self.next_index = 1  # Start indexing from 1
        self.database_filename = flash_card_directory + "/" +database_filename
        
        # If a filename is provided, try to load the database
        if self.database_filename and os.path.exists(self.database_filename):
            self.load_database()
    
    def add_word(self, word):
        """
        Add a word to the database if it doesn't exist and return its index.
        If the word already exists, return its existing index.
        
        Args:
            word (str): The word to add
            
        Returns:
            int: The index of the word
        """
        if word in self.words:
            return self.words[word]
        
        # Add the word with the next available index
        self.words[word] = self.next_index
        self.next_index += 1
 
        return self.words[word]
    def get_words_by_frequency(self, freq_counter, min_freq=1, max_freq=float('inf')):
        """
        Get words with frequency counts within a specified range.
        
        Args:
            freq_counter (KeyCounter): The frequency counter object
            min_freq (int): Minimum frequency (inclusive)
            max_freq (int or float): Maximum frequency (inclusive)
            
        Returns:
            list: List of words with frequencies within the specified range
        """
        result = []
        for word, idx in self.words.items():
            freq = freq_counter.get_count(idx)
            if min_freq <= freq <= max_freq:
                result.append(word)
        return result
    
        
    def get_index(self, word):
        """
        Get the index of a word.
        
        Args:
            word (str): The word to look up
            
        Returns:
            int or None: The index of the word, or None if not found
        """
        return self.words.get(word)
    
    def get_word(self, index):
        """
        Get a word by its index.
        
        Args:
            index (int): The index to look up
            
        Returns:
            str or None: The word associated with the index, or None if not found
        """
        for word, idx in self.words.items():
            if idx == index:
                return word
        return None
    
    def save_database(self, filename=None):
        """
        Save the database to a file.
        
        Args:
            filename (str, optional): The filename to save to. 
                                      If None, uses the instance's database_filename.
        
        Returns:
            bool: True if successful, False otherwise
        """
        filename = filename or self.database_filename
        if not filename:
            return False
        
        try:
            with open(filename, 'w+', encoding='utf-8') as f:
                json.dump({
                    'words': self.words,
                    'next_index': self.next_index
                }, f, ensure_ascii=False)
            
            self.database_filename = filename
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def load_database(self, filename=None):
        """
        Load the database from a file.
        
        Args:
            filename (str, optional): The filename to load from.
                                      If None, uses the instance's database_filename.
        
        Returns:
            bool: True if successful, False otherwise
        """
        filename = filename or self.database_filename
        if not filename or not os.path.exists(filename):
            return False
            list = wb.get_words_by_frequency(kc,4,5000)

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.words = data['words']
                self.next_index = data['next_index']
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            return False




def process_flashcard_files(directory=flash_card_directory, pattern="flashcard*.json", processobject=None):
    """
    Process all flashcard JSON files matching a pattern in the specified directory.
    
    Args:
        directory (str): Directory to search for files. If None, uses current directory.
        pattern (str): File pattern to match (default: "flashcard*.json")
        processobject: Object with a process() method to call on each file
        
    Returns:
        int: Number of files processed
    """
    
    if directory is None:
        directory = os.getcwd()
    else:
        directory = os.path.expanduser(directory)
    
    if processobject is None:
        return 0
        
    # Get list of files matching pattern in the directory
    file_pattern = os.path.join(directory, pattern)
    files = glob.glob(file_pattern)
    
    count = 0
    for file_path in files:
        try:
            processobject.process(file_path)
            count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return count


def process_words(flash_file,process_object):
    with open(flash_file,"r",encoding="utf-8") as flashfile:
        flashcards = json.loads(flashfile.read())
        for card in flashcards:
            process_object.process(card)



class WordCountObject:
    def __init__(self,worddb,freqdb):
        self.worddb = worddb
        self.freqdb = freqdb

    def process(self,card):
        idx = self.worddb.add_word(card['word'])
        self.freqdb.increase_count(idx)
        

class ProcessFlashFile:
    def __init__(self,process_object):
        self.process_object  = process_object
        None
    
    def process(self,file):
        process_words(file,self.process_object)
        


def build_counters():
    wb = WordDatabase()    
    kc = KeyCounter()
    wc = WordCountObject(wb,kc)
    
    pf =ProcessFlashFile(wc)
    process_flashcard_files(processobject=pf)
    wb.save_database()
    kc.save_to_file()
    list = wb.get_words_by_frequency(kc,4,5000)
    print(list)
    None




def extract_json_from_text(text):
    
    api = openrouter.OpenRouterAPI
    """
    Extracts and parses a JSON block from within text.
    
    Args:
        text (str): Text containing a JSON block
        
    Returns:
        dict or list: Parsed JSON object or None if no valid JSON found
    """
    # Try to find JSON pattern (text between curly braces including nested structures)
    count = 5
    while count > 0:
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)    
        if json_match:
            try:
                # Extract the matched JSON string and parse it
                json_str = json_match.group(0)
                return json.loads(json_str)
            except json.JSONDecodeError:
                print("Found JSON-like structure but couldn't parse it")
                text = api.open_router_nova_lite_v1("Try to clean up and fix the json in this string: " + json_str)
                count=count - 1        
    return None

import hashlib
import random

def save_flashcards_to_json(flashcards, prefix="flashcard"):
    """
    Saves an array of flashcards to a JSON file with a random integer in the filename.
    
    Args:
        flashcards (list): Array of flashcard data to save
        prefix (str): Prefix for the filename (default: 'flashcard')
        
    Returns:
        str: The filename that was created
    """
    random_int = random.randint(1000, 9999)
    filename = f"{prefix}{random_int}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, ensure_ascii=False, indent=2)
    
    return filename


import textprocessing
import json
import os
import glob
def generate_flashcards(text):    
    api = openrouter.OpenRouterAPI()
    #"""You are a chinese language learning content creator. You focus on material to help foreigner learn written Chinese.""",
    result = api.open_router_claude_3_7_sonnet("""You are a chinese language learning content creator. You focus on material to help foreigner learn written Chinese.""","""
    split this text into the separate words, split words longer than 2 characters into parts, and create a prompt for each one that is suitable to generate an image for the word that can be used in a flashcard game. Make the output in this json format [{"word":word,"sentence": the sentence the word is in in the structure,"prompt":prompt},...]. Do not include these words: """ +str(list) + """ Here is the text:
    
    """+ text )
    flashcards = extract_json_from_text(result)
    for card in flashcards:
         md5signature = hashlib.md5(card['prompt'].encode('utf-8')).hexdigest()
         card['md5signature'] = md5signature
         card['tokens'] = textprocessing.split_text(card['sentence'])
         with open(md5signature + ".prompt", "w", encoding="utf-8") as f:
            f.write(card['prompt'])
    save_flashcards_to_json(flashcards, prefix="flashcard")
 



def process_text_in_chunks(text, chunk_size=200):
    wb = WordDatabase()    
    kc = KeyCounter()
    wc = WordCountObject(wb,kc)
    
    pf =ProcessFlashFile(wc)
    process_flashcard_files(processobject=pf)
    wb.save_database()
    kc.save_to_file()
    list = wb.get_words_by_frequency(kc,4,5000)


    """
    Split text into chunks of specified size and process each chunk with generate_flashcards
    
    Args:
        text (str): The text to process
        chunk_size (int): Size of each chunk in characters
    """
    # Split text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    print(f"Split text into {len(chunks)} chunks of approximately {chunk_size} characters each")
    
    # Process each chunk
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        generate_flashcards(chunk)
        
    print("All chunks processed successfully.")



if __name__ == "__main__":
    build_counters()
    trim = """
    好的，這是一個為您創作的故事第一章，希望能符合您的要求。

---

### **第一章：彌敦道上的單行道**

放學鐘聲，是每日的救贖，也是另一種迷惘的開始。

我叫陳浩然，中四學生，就讀於九龍塘一間普普通通的中學。成績普普通通，樣貌普普通通，身高一米七二，在人群中就像一顆沒人會多看一眼的石子。每日穿著燙得不怎麼筆直的校服，背著塞滿了課本和前途問號的書包，穿梭在香港這個擠迫得令人窒息的城市裡。

「喂，浩然！想什麼呢？口水都快流到地理書上了。」一把聲音把我從白日夢的邊緣拉回來。

是我的死黨，李偉傑，大家都叫他阿傑。他是我從中一就認識的朋友，籃球打得比我好，追女生的膽子比我大，功課……好吧，功課跟我一樣，在及格線的邊緣掙扎。

我抹了抹嘴角，還好是乾的。我剛剛正盯著窗外，看著樓下那棵鳳凰木。夏天快到了，火紅色的花瓣在悶熱的空氣中微微晃動，就像我那顆靜不下來的心。

但真正讓我分心的，不是鳳凰木，而是坐在我斜前方三排的林㴓君。

林㴓君，我們班的女神。不是那種遙不可及、會上電視的校花，而是一種更真實、更貼近生活的美好。她的馬尾總是梳得一絲不苟，陽光透過窗戶灑在她身上時，連髮絲都像在發光。她上課總是很專心，筆記永遠整齊得像印刷出來一樣。最重要的是，她笑起來的時候，嘴角會有兩個淺淺的酒窩，彷彿能裝下整個維多利亞港的溫柔。

我從來沒跟她說過超過三句話。第一句是「唔該，借借」，第二句是「對唔住」，第三句是……我想不起來了，大概也是類似的客套話。

「還在看你的㴓君女神？」阿傑用手肘撞了撞我，臉上掛著促狹的笑容。「拜託，你這樣看到畢業都沒用的。行動啊，兄弟！」

「怎麼行動？」我小聲地反駁，「難道衝過去跟她說『你好，我想做你男朋友』嗎？她大概會以為我是神經病，然後叫風紀老師過來。」

「嘖，你就是想太多。」阿傑一邊把書本胡亂塞進書包，一邊說：「機會是要自己創造的。你看，下個禮拜數學大測，你知道她數學超強的吧？你可以去問她問題啊，多麼順理成章的開場白。」

數學大測。這四個字像一塊巨石，瞬間把我心頭那點青春的悸動壓得粉碎。我的數學成績，用「災難」來形容都算是客氣了。

「問問題？我連題目都看不懂，要問什麼？」我愁眉苦臉地說。

「這就是問題所在了！」阿傑把書包甩到肩上，「所以，我有一個絕妙的計畫。」

我們跟著人潮走出校門，悶熱的空氣混雜著汽車廢氣迎面撲來。學校門口的紅色小巴站已經排起了長龍。我和阿傑習慣走去地鐵站，那段路不長不短，剛好夠我們聊一些不能在課室裡說的秘密。

「什麼計畫？」我問。

阿傑左右看了看，神秘兮兮地湊到我耳邊：「『出貓』。」

我愣住了。

「出貓？你瘋了？」我壓低聲音，但還是忍不住拔高了語調。「被抓到要記大過的！說不定還會影響考大學。」

「哎呀，富貴險中求嘛。」阿傑滿不在乎地說，「不是那種寫在手心上的低級方法。我聽說高年級的師兄有路子，可以弄到這次測驗的『溫習重點』，命中率百分之九十以上。我們只要湊點錢，就能搞到手。你想想，數學成績突然突飛猛進，老師肯定對你刮目相看，林㴓君說不定也會注意到你啊！覺得你『嘩，原來陳浩然是個隱藏的數學天才』。」

我沉默了。阿傑描繪的畫面確實很吸引人。在這個只看重成績的環境裡，一個好分數就像一件名牌外套，能立刻讓你整個人都亮起來。我也厭倦了每次派卷時，老師那種失望的眼神，和父母那句「唉，下次再努力吧」的嘆息。

但……這畢竟是作弊。從小到大，老師和家人都教導我要誠實。這條底線，我從來沒有跨越過。

「我……我考慮一下。」我含糊地說。

我們走進了旺角地鐵站，人潮像潮水一樣將我們吞沒。車廂裡，人們肩並肩地站著，每個人的臉上都帶著一絲疲憊。我握著扶手，看著窗外飛速倒退的黑暗，感覺自己的人生也像這班列車，被推著往前走，卻不知道終點在哪裡。

我為什麼要讀書？為了考上好大學。為什麼要考上好大學？為了找份好工作。為什麼要找份好工作？為了賺錢，為了在香港這個寸金寸土的地方生存下去。

這條路，就像彌敦道一樣，筆直、繁忙，所有人都朝著同一個方向前進。但這真的是我想要的嗎？我不知道。我只知道，我對未來感到迷茫，就像站在尖沙咀碼頭，隔著一片霧，看不清對岸的中環一樣。

「喂，想什麼呢？到旺角了。」阿傑拉了我一把。

走出地鐵站，一股屬於旺角的獨特氣息撲面而來——街頭小食的香氣、化妝品店的香水味、還有巨大的廣告牌上閃爍的霓虹燈光。西洋菜南街永遠都是那麼多人，我們像兩條小魚，在人海中奮力洄游。

「走，去信和中心逛逛，看有沒有新遊戲。」阿傑興致勃勃地說。

我心不在焉地點點頭。腦子裡還在想著「出貓」和林㴓君的事。這兩件事，一件是通往成功的捷徑，另一件是我心中遙不可及的美好。它們就像兩條完全相反的路。

就在這時，我的目光被街角的一家書店吸引住了。

不是因為書店本身，而是因為站在書店門口，正在認真翻閱一本參考書的人——是林㴓君。

她沒有穿校服，換上了一件簡單的白色T恤和牛仔褲，腳上是一雙乾淨的白色帆布鞋。她扎著馬尾，身旁放著一個布袋，樣子專注而安靜，與周圍的喧囂格格不入。

那一刻，時間彷彿變慢了。我看著她，她正在為下週的數學測驗認真地挑選練習題。而我，幾分鐘前，還在和阿傑討論如何用不光彩的手段去應付它。

一股莫名的羞愧感湧上心頭。

我想像了一下，如果我真的靠作弊拿了高分，然後故作聰明地去跟她討論題目，我還能坦然面對她那雙清澈的眼睛嗎？

追一個女孩子，到底是為了讓她喜歡上一個「更好」的自己，還是為了讓她喜歡上一個「真實」的自己？如果為了得到她的注意，而變成一個連自己都討厭的人，那這份喜歡，又有什麼意義？

「浩然？你看什麼呢？」阿傑順著我的目光望過去，也看到了林㴓君。「嘩，真是冤家路窄……不對，是天賜良緣啊！快去啊，就說『嗨，好巧啊，你也來買參考書嗎』，完美！」

我搖了搖頭，拉著阿傑轉身走進了另一條小巷。

「喂！你幹嘛啊？這麼好的機會！」阿傑不滿地嚷嚷。

「走吧，我不想去了。」我低聲說。

「為什麼啊？」

我深吸了一口氣，香港潮濕的空氣似乎也變得清新了一些。我停下腳步，看著阿傑，認真地說：

「我想靠自己試一次。」

也許我的努力換來的，依然會是一個不及格的分數。也許林㴓君永遠都不會注意到我這個普通得不能再普通的同學。

但是，至少，當我站在彌敦道的十字路口，選擇前進方向時，我可以選擇那條更難走，卻能讓我心安理得的路。

這是我第一次，為自己的人生，做出了一個小小的，但卻無比堅定的決定。

"""

    sample_text = "This is a sample text with some words that are not on HSK1-2 level. For example, 'abandon', 'zealous', and 'quintessential'."

    process_text_in_chunks(trim)

    print("Flashcards generated and saved.")
    