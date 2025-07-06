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
        total_filename =flash_card_directory+"/"+filename 
        with open(total_filename, "rb") as f:
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




def process_vocab_list(filename):
    with open(filename,"r",encoding="utf-8") as f:
        blob = f.read()
        mystuff = json.loads(blob)
        for card in mystuff:
            card['md5signature'] =  hashlib.md5(card['prompt'].encode('utf-8')).hexdigest()
            with open(card['md5signature'] + ".prompt", "w", encoding="utf-8") as f:
                f.write(card['prompt'])
        prefix = "flashcard"
        random_int = random.randint(1000, 9999)
        filename = f"{prefix}{random_int}.json"
        with open(filename,"w",encoding='utf-8') as f:
            f.write(json.dumps(mystuff))



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
   
        found_strings = find_strings_simple(sentence, string_list)
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


import glob

def find_strings_simple(text, string_list):
    found_strings = []
    for string in string_list:
        if string in text:
            found_strings.append(string)
    return found_strings


def get_words_in_text(text):
    wb = WordDatabase()    
    kc = KeyCounter()
    wc = WordCountObject(wb,kc)    
    pf = ProcessFlashFile(wc)
    process_flashcard_files(processobject=pf)
    wb.save_database()
    kc.save_to_file()
    
    string_list = wb.get_all_words()
    # Sort string_list by length (descending) so longer words are found first
    string_list.sort(key=len, reverse=True)
   
    found_strings = find_strings_simple(text, string_list)
    
    # Add all strings to the automaton
 
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
 
def dictionarylookup(word):
    """
    Lookup a word in a remote Chinese dictionary
    
    Args:
        word (str): The Chinese word to lookup
        
    Returns:
        dict: Dictionary response containing the word definition and information
            or None if the request failed
    """
    try:
        url = "https://chinese.eriktamm.com/api/dictionarylookup"
        params = {"word": word}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url, json=params, headers=headers)
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error looking up word '{word}': {e}")
        return None
 
 
 

def generate_flashcards(text):    
    api = openrouter.OpenRouterAPI()
    
    #list = get_words_in_text(text)
    list = []
    
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
    flash_card_directory = "/var/www/html/flashcards"
    about = build_flashcards_from_wordlist(get_words_in_text(text))
    return about


def get_server_flashcard_from_list(wordlist):
    global flash_card_directory
    flash_card_directory = "/var/www/html/flashcards"
    about = build_flashcards_from_wordlist(wordlist)
    return about



def get_dictionary_words_not_in_flashcards(wordlist, flashcard_files=None):
    """
    Get words from a wordlist that are not present in any flashcard files.
    
    Args:
        wordlist (list): List of words to check
        flashcard_files (list, optional): List of flashcard files to check against
        
    Returns:
        list: Words from the wordlist that are not found in any flashcard file
    """
    wb = WordDatabase()
    chosenwords = []
    for word in wordlist:
        word = word.strip()
        if not word:
            continue
        
        if wb.get_index(word) is not None:
            print(f"Word '{word}' already exists in flashcard database.")
            continue

        foundit = dictionarylookup(word)
        if foundit['result'] == None:
            print(f"Error looking up word: {word}")
            continue
        #now we want to find the word in the flashcard files
        chosenwords.append(word)
    
    if (len(chosenwords) == 0):
        print("No words found in the wordlist that are not already in flashcards.")
        return  

    api = openrouter.OpenRouterAPI()
    
    #list = get_words_in_text(text)
    list = []
    
    #"""You are a chinese language learning content creator. You focus on material to help foreigner learn written Chinese.""",
    result = api.open_router_claude_3_7_sonnet("""You are a chinese language learning content creator. You focus on material to help foreigner learn written Chinese.""","""
    for each word in the provided text: create a prompt that is suitable to generate an image for the word that can be used in a flashcard game. Make the output in this json format [{"word":word,"sentence": a sample sentence the word is used in,"prompt":prompt},...]. Do not include any these words: """ +str(list) + """ Here is the list:
    
    """+ str(chosenwords) )
    flashcards = extract_json_from_text(result)
    flashcards = filter_flashcards_by_word_list(flashcards, list)
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



import rthknews
import requests

def generate_flashcards_for_rthk_news(use_dictionary=False):
    """
    Generate flashcards for RTHK news articles.
    
    This function fetches the latest RTHK news articles, extracts text from them,
    and generates flashcards based on the content.
    
    Returns:
        None
    """
    articles = rthknews.get_rthk_tokenized_news()
    for tokenarray in articles:
        #make a string from  all the elemments in the tokenarray
        article = "".join(tokenarray) 
        text = article
        if not use_dictionary:
            generate_flashcards(text)
        else:
            get_dictionary_words_not_in_flashcards(tokenarray)
    
    
    
    
    
    get_dictionary_words_not_in_flashcards


if __name__ == "__main__":
    
    
    #process_vocab_list("wordlist.json")
    
    build_counters()
    

    #generate_flashcards_for_rthk_news(use_dictionary=True)
    
    #process_all_flashcard_files()
    
    #build_counters()
    trim = """
    不知道你有沒有聽過一個關於沉船之際的笑話？

這則笑話簡明易懂地表現出各國民族性和價值觀。

一艘載著來自各國遊客的豪華客船即將沉沒，然而救生艇的數量卻不及乘載所有乘客，船長因此勸說乘客自行投海，他依乘客的國籍不同來改變勸進的說法。

對美國人說：「跳下去，你就是英雄了！」

對義大利人說：「欸，海裡有美女在游泳呢！」

對英國人說：「所謂的紳士，就是在這樣的時刻往海裡跳的人喔！」

對德國人說：「這是規定，所以請你跳進海裡。」

對日本人說：「大家都已經跳下去囉！」

對韓國人說：「日本人已經跳下去了喔！」

這則笑話是一個例子，說明了不同國家國民的動機各不相同，這一點十分有趣。從這則笑話可以得知兩個啟示。

一、創造動機的結構各有不同
在這個例子中，因為在社會上被視為美德的行為不同，讓人有興趣去做一件事的開關也各自相異。這不只是在團體裡，每一個人受到刺激引發動機的點也各不相同。

二、懂得動機的運作方式，下點功夫就能改變心態
在這則笑話，船長只是稍微改變用詞如英雄、美女、規定等，就能激發動機，同樣的道理，早起、運動、整理也只需要下一點功夫就能讓你提起勁做到。

要改變自己的心，非常困難。但如果只要下一點功夫點燃自己的熱情，你是不是就覺得可以做得到了呢？

本書的主題，不在於勉強提升自己做事的幹勁或動機，而是要找到好的方法，讓自己願意去做。如果能讓自己願意去做，自然能夠點燃動機。因此，先找到讓自己有興趣的開關非常重要。

以早起為例，先不想正確答案或對不對、訣竅等，而是先試著想怎樣才會讓自己有興趣。

曾經，人們將清晨的活動稱為「朝活」，流行一段時間，有些人因此養成了早起的習慣，然而這方法並不適合所有人。

有些人替自己準備有名店家的麵包，讓自己期待早起，有些人則是每天在臉書上發文昭告自己的起床時間，逼著自己，激發自己的意願。

也有人在陽台放把椅子，期待早起能邊喝咖啡邊看報紙。也有人因為喜歡上在安靜的通勤電車中讀書的感覺，因而能持續早起的習慣。

此外，也有人因為在晨跑之後上班，實際感受到早起是開啟一整天良性循環的關鍵，因而能夠持續。

運動也是一樣，不是所有人都到健身房就好，有些人因為夫妻一起慢走而能持續下去，有些人享受打網球的樂趣，有些人如果可以在不勉強自己的情況下游泳十五分鐘，就可以持之以恆。我則是因為練空手道的關係，只要是能夠增加身體運動強度的事情，就能讓我躍躍欲試。

此外，從別的角度來看，有些女性只要穿上可愛的運動服就願意跑步，也有些人喜歡和朋友繞著天皇所居住的皇居跑，更有人是訂下了目標，要挑戰鐵人三項或跑完全程馬拉松，因而能夠持續運動。

總之，只要在行動上下一點功夫，就能點燃一個人的動機。反過來說，如果因為微妙的差距而搔不到癢處，習慣的養成就不會順利。

我當過許多人的教練，在過程中，我漸漸認為，讓習慣和人生都好轉的竅門，在於學會「有意念地做自己有興趣的事，並且有勇氣放棄自己做起來不起勁的事！」

因此，我將本書的核心思想放在「巧妙地誘發自己的興致」。

「那件事，我做起來感覺有興致，還是沒有呢？」「如果提不起勁，用什麼樣的方法能誘發我的興致呢？」對自己提問，是找到答案的方法。「如何才能誘發自己行動的興致？」「對事情採取什麼想法、看法，能誘發我的興致呢？」「想要讓自己樂在其中，我的信念和欲求是什麼？」「能幫助我進入狀況的環境在哪裡？」

希望你能隨著本書，從行動、思考、感受、環境等習慣的六十五個面向來找到提起自己興致的方法。為了讓你能夠找到完全符合你自己的開關，我盡可能提供許多方法，使本書成為一本習慣養成大全。請挑選適合自己的方法，忽視那些不適合你的。

    """
    
    #get_server_flashcard_from_text(trim)
    #about = build_flashcards_from_wordlist(get_words_in_text(trim))
    get_dictionary_words_not_in_flashcards(textprocessing.split_text(trim))

    j_chinese = filter_chinese_lines(trim)

    #generate_flashcard_test(j_chinese)

    sample_text = "This is a sample text with some words that are not on HSK1-2 level. For example, 'abandon', 'zealous', and 'quintessential'."

    process_text_in_chunks(j_chinese,chunk_size=500)




    print("Flashcards generated and saved.")
    