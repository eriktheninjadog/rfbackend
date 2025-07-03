#flashcardgenerate.py


import openrouter
import json
import re
import os
import pickle

flash_card_directory = "/home/erik/flashcards"


class DoubleIndex:
    def __init__(self):
        # Maps word ID to a set of sentence IDs
        self.word_to_sentences = {}

        # Maps sentence ID to a set of word IDs
        self.sentence_to_words = {}

    def add_word_sentence_relationship(self, word_id, sentence_id):
        """Adds a relationship between a word ID and a sentence ID."""
        # Add sentence ID to the word's set
        if word_id not in self.word_to_sentences:
            self.word_to_sentences[word_id] = set()
        self.word_to_sentences[word_id].add(sentence_id)

        # Add word ID to the sentence's set
        if sentence_id not in self.sentence_to_words:
            self.sentence_to_words[sentence_id] = set()
        self.sentence_to_words[sentence_id].add(word_id)

    def get_sentence_ids_for_word(self, word_id):
        """Returns a list of sentence IDs containing the given word ID."""
        return list(self.word_to_sentences.get(word_id, []))

    def get_word_ids_for_sentence(self, sentence_id):
        """Returns a list of word IDs in the given sentence ID."""
        return list(self.sentence_to_words.get(sentence_id, []))

    def save_to_disk(self, filename):
        """Saves the double index to a file."""
        with open(flash_card_directory+"/"+filename, "wb") as f:
            pickle.dump((self.word_to_sentences, self.sentence_to_words), f)

    @classmethod
    def load_from_disk(cls, filename):
        """Loads the double index from a file."""
        instance = cls()
        with open(flash_card_directory+"/"+filename, "rb") as f:
            instance.word_to_sentences, instance.sentence_to_words = pickle.load(f)
        return instance


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
    
    def get_all_words(self):
        return list(self.words.keys())
    
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
        

class SentenceDBBuilder:
    def __init__(self,sentencedb):
        self.sentencedb = sentencedb

    def process(self,card):
        idx = self.sentencedb.add_word(card['sentence'])
 

class ImageDBBuilder:
    def __init__(self,imagedb):
        self.imagedb = imagedb

    def process(self,card):
        idx = self.imagedb.add_word(card['md5signature'])

 
class WordSentenceIdxBuilder:
    def __init__(self,wsidx,worddb,sentencedb):
        self.wsidx = wsidx
        self.worddb = worddb
        self.sentencedb = sentencedb

    def process(self,card):
        sentence = card['sentence']        
        sentenceidx = self.sentencedb.get_index(sentence)
        string_list = self.worddb.get_all_words()
   
        automaton = ahocorasick.Automaton()
    
    # Add all strings to the automaton
        for idx, string in enumerate(string_list):
            automaton.add_word(string, (idx, string))
        
        # Make the automaton
        automaton.make_automaton()
        
        # Find all matches
        found_strings = set()
        for end_index, (insert_order, original_string) in automaton.iter(sentence):
            found_strings.add(original_string)

        alist = list(found_strings)
        for word in alist:
            wordidx = self.worddb.get_index(word)
            if wordidx is not None and sentenceidx is not None:
                self.wsidx.add_word_sentence_relationship(wordidx, sentenceidx) 



class WordImageIdxBuilder:
    def __init__(self,wiidx,worddb,imagedb):
        self.wiidx = wiidx
        self.worddb = worddb
        self.imagedb = imagedb

    def process(self,card):
        image = card['md5signature']
        imageidx = self.imagedb.add_word(image)
        word  = card['word']
        wordidx = self.worddb.get_index(word)
        self.wiidx.add_word_sentence_relationship(wordidx, imageidx) 

        
class ProcessFlashFile:
    def __init__(self,process_object):
        self.process_object  = process_object
        None
    
    def process(self,file):
        process_words(file,self.process_object)
        

def build_flashcards_from_wordlist(wordlist):
    wb = WordDatabase()    
    kc = KeyCounter()
    wc = WordCountObject(wb,kc)
    sdb = WordDatabase("sentencedb.json")
    imagedb = WordDatabase("imagedb.json")
    word_sentence_ci = DoubleIndex.load_from_disk("word_sentence_idx.pickle")
    word_image_ci = DoubleIndex.load_from_disk("word_image_idx.pickle")

    ret = []
    for word in wordlist:
        w_idx = wb.get_index(word)
        sentence_idxs = word_sentence_ci.get_sentence_ids_for_word(w_idx)
        sentences = []
        for s in sentence_idxs:
            asentence = sdb.get_word(s) 
            sentences.append(asentence)
        images = []
        imagesidxs =  word_image_ci.get_sentence_ids_for_word(w_idx)
        for i in imagesidxs:
            md5stuff = imagedb.get_word(i)
            images.append(md5stuff)   
        ret.append({ "word":word,"sentences":sentences,'images':images})
    return ret


def build_counters():
    wb = WordDatabase()    
    kc = KeyCounter()
    wc = WordCountObject(wb,kc)
    sdb = WordDatabase("sentencedb.json")
    imagedb = WordDatabase("imagedb.json")
    
    word_sentence_ci = DoubleIndex()
    word_image_ci = DoubleIndex()
    

    sbuilder = SentenceDBBuilder(sdb)
    imagebuilder = WordImageIdxBuilder(word_image_ci,wb,imagedb)
    
    pf =ProcessFlashFile(wc)
    process_flashcard_files(processobject=pf)
    wb.save_database()
    kc.save_to_file()
    
    
    
    pf =ProcessFlashFile(sbuilder)
    process_flashcard_files(processobject=pf)
    sdb.save_database()

    pf =ProcessFlashFile(imagebuilder)
    process_flashcard_files(processobject=pf)
    imagedb.save_database()
    word_image_ci.save_to_disk("word_image_idx.pickle")
    
  
    sdbb = WordSentenceIdxBuilder(word_sentence_ci,wb,sdb)
    pf =ProcessFlashFile(sdbb)
    process_flashcard_files(processobject=pf)
    word_sentence_ci.save_to_disk("word_sentence_idx.pickle")
    
#    idbb = WordImageIdxBuilder(word_image_ci,wb,imagedb)
#    pf =ProcessFlashFile(idbb)
#    process_flashcard_files(processobject=pf)
#    word_image_ci.save_to_disk("word_image_idx.pickle")
    
    

    list = wb.get_words_by_frequency(kc,4,5000)
    print(list)
    None


def extract_json_from_text(text):
    
    api = openrouter.OpenRouterAPI()
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

def filter_flashcards_by_word_list(flashcards, excluded_words):
    """
    Filters a list of flashcard dictionaries, removing cards whose 'word' value
    is found in the excluded_words list.
    
    Args:
        flashcards (list): List of flashcard dictionaries
        excluded_words (list): List of words to exclude
        
    Returns:
        list: Filtered list of flashcards
    """
    if not flashcards or not excluded_words:
        return flashcards
    
    return [card for card in flashcards if card['word'] not in excluded_words]


import ahocorasick
import glob

def get_words_in_text(text):
    wb = WordDatabase()    
    kc = KeyCounter()
    wc = WordCountObject(wb,kc)    
    pf = ProcessFlashFile(wc)
    process_flashcard_files(processobject=pf)
    wb.save_database()
    kc.save_to_file()
    
    string_list = wb.get_all_words()
   
    automaton = ahocorasick.Automaton()
    
    # Add all strings to the automaton
    for idx, string in enumerate(string_list):
        automaton.add_word(string, (idx, string))
    
    # Make the automaton
    automaton.make_automaton()
    
    # Find all matches
    found_strings = set()
    for end_index, (insert_order, original_string) in automaton.iter(text):
        found_strings.add(original_string)

    alist = list(found_strings)
    emptytext = text
    for l in alist:
        emptytext = emptytext.replace(l,"_")
    print(emptytext)
    return alist
    
def contains_chinese(text):
    """
    Check if the given text contains Chinese characters.
    
    Args:
        text (str): The text to check for Chinese characters
        
    Returns:
        bool: True if text contains at least one Chinese character, False otherwise
    """
    # Define the Unicode ranges for Chinese characters
    # Common Chinese/Japanese/Korean (CJK) Unified Ideographs range
    # This covers most common Chinese characters
    for char in text:
        # Check if character is in the main CJK unified ideographs block
        if '\u4e00' <= char <= '\u9fff':
            return True
        # Check if character is in CJK Unified Ideographs Extension A
        elif '\u3400' <= char <= '\u4dbf':
            return True
        # Check if character is in CJK Unified Ideographs Extension B
        elif '\u20000' <= char <= '\u2a6df':
            return True
    
    # No Chinese characters found
    return False

def filter_chinese_lines(text):
    """
    Filter a text to keep only lines that contain Chinese characters.
    
    Args:
        text (str): The input text to filter
        
    Returns:
        str: Text with only lines containing Chinese characters
    """
    lines = text.split('\n')
    chinese_lines = []
    
    for line in lines:
        if contains_chinese(line):
            chinese_lines.append(line)
    
    return '\n'.join(chinese_lines)




def generate_prompts_from_flash_card_file(filename):
    """
    Generate flashcards from a file containing text.
    
    Args:
        filename (str): Path to the file containing text
        
    Returns:
        None
    """
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
        flashcards = json.loads(text)
    
        for card in flashcards:         
            md5signature = hashlib.md5(card['prompt'].encode('utf-8')).hexdigest()
            with open(md5signature + ".prompt", "w", encoding="utf-8") as f:
                f.write(card['prompt'])
 
 
def process_all_flashcard_files(directory=None, pattern="flashcard*.json"):
    """
    Process all flashcard files matching the pattern in the specified directory
    and generate prompts for each flashcard.
    
    Args:
        directory (str): Directory to search for files. If None, uses current directory.
        pattern (str): File pattern to match (default: "flashcard*.json")
        
    Returns:
        int: Number of files processed
    """
    if directory is None:
        directory = os.getcwd()
    else:
        directory = os.path.expanduser(directory)
    
    # Get list of files matching pattern in the directory
    file_pattern = os.path.join(directory, pattern)
    files = glob.glob(file_pattern)
    
    count = 0
    for file_path in files:
        try:
            generate_prompts_from_flash_card_file(file_path)
            print(f"Processed {file_path}")
            count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Total flashcard files processed: {count}")
    return count
 
 
 

def generate_flashcards(text):    
    api = openrouter.OpenRouterAPI()
    
    list = get_words_in_text(text)
    
    #"""You are a chinese language learning content creator. You focus on material to help foreigner learn written Chinese.""",
    result = api.open_router_claude_3_7_sonnet("""You are a chinese language learning content creator. You focus on material to help foreigner learn written Chinese.""","""
    split this text into the separate words, split words longer than 4 characters into parts, and create a prompt for each one that is suitable to generate an image for the word that can be used in a flashcard game. Make the output in this json format [{"word":word,"sentence": the sentence the word is in in the structure,"prompt":prompt},...]. Do not include any these words: """ +str(list) + """ Here is the text:
    
    """+ text )
    flashcards = extract_json_from_text(result)
    flashcards = filter_flashcards_by_word_list(flashcards, list)
    for card in flashcards:         
         md5signature = hashlib.md5(card['prompt'].encode('utf-8')).hexdigest()
         card['md5signature'] = md5signature
         card['tokens'] = textprocessing.split_text(card['sentence'])
         with open(md5signature + ".prompt", "w", encoding="utf-8") as f:
            f.write(card['prompt'])
    save_flashcards_to_json(flashcards, prefix="flashcard")
 


def get_server_flashcard_from_text(text):
    global flash_card_directory
    flash_card_directory = "/var/www.html/flashcards"
    about = build_flashcards_from_wordlist(get_words_in_text(trim))
    return about


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
    
    
    #build_counters()
    
    
    #process_all_flashcard_files()
    
    #build_counters()
    trim = """
    旅發局委任劉鎮漢為總幹事，8月4日履新，接替將會離任的程鼎一。

    旅發局主席林建岳歡迎劉鎮漢加盟旅發局，認為對方擁有豐富的旅遊業和市場推廣經驗，富有卓越的領導和管治才能，是擔任總幹事的理想人選。

    他相信劉鎮漢定必能夠帶領旅發局團隊，根據《香港旅遊業發展藍圖 2.0》訂定的方向，聯同業界及不同的持份者，齊心推動旅遊業更上一層樓，鞏固香港成為一個更多元化體驗的世界級旅遊目的地，擴大旅遊業對社會的貢獻。

    林建岳提到，劉鎮漢曾於2007年至2019年間曾出任旅發局總幹事，其後於2023年出任為勞工及福利局香港人才服務辦公室總監。

    另外，林建岳代表旅發局感謝程鼎一過去六年帶領，渡過疫情挑戰，帶動旅遊業疫後穩步復蘇，為香港旅遊業作出重大貢獻。



    """
    
    get_server_flashcard_from_text(trim)
    about = build_flashcards_from_wordlist(get_words_in_text(trim))

    j_chinese = filter_chinese_lines(trim)

    #generate_flashcard_test(j_chinese)

    sample_text = "This is a sample text with some words that are not on HSK1-2 level. For example, 'abandon', 'zealous', and 'quintessential'."

    process_text_in_chunks(j_chinese,chunk_size=500)

    print("Flashcards generated and saved.")
    