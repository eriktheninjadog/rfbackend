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
    
    都知道英國國王愛德華八世（Edward VIII）的佳話，不愛江山愛美人，為了美人，甘願放棄王位。其實這是誇大了愛德華八世的品德，因為權力會帶給人痴迷，有著無上權力的人，幾乎不大可能放棄權力，無論他受到什麼道德的感召。而愛德華八世，作為一個君主立憲制的國王，權力小得可憐，論名氣，論身分，當然世界矚目，但要論享受權力的快感，可能還不如中國古代的一個縣令。所以，對愛德華八世的品德，不可太迷信，其實我們春秋時代的君主，有些比他高尚多了，比如可憐的魯隱公。

翻開《左傳》，第一個魯國國君就是魯隱公，一位有著高尚品德的貴胄公子。他老爸魯惠公去世的時候，嫡太子公子允還小，不能執政，所以大臣立了惠公的庶長子息姑（名字看似很女性，但確實是男的），也就是魯隱公。按照後世政治的玩法，一朝權在手，便把隱患除。公子允基本上是死定了，不需要魯隱公動手，左右自會主動請纓。當然，這不能怪左右諂媚，而是君主的權力，哪怕在滿眼貴族的春秋時代，也是有些嚇人的。

話說魯隱公這個國君一直當了十一年，公子允漸漸長大成人了，另一個大臣公子翬主動向魯隱公提議：「雖然您一直說自己只是暫時代掌君位，將來必歸政公子允，但老百姓不答應啊，他們都覺得您這個君主最偉大、最光榮、最正確，不如這樣，我幫您殺了公子允，您封我當太宰。」

換了別人，肯定求之不得。當然，公子翬以求封宰相為交換，很可惡，但沒關係，先利用他殺了公子允，然後再宣布他悍然殺儲君，罪大惡極，將之名正言順處死，豈不美哉？但魯隱公卻傻傻地說：「這種事怎麼能做？不行不行。我已經在菟裘那個地方建了房子，很快就要把君位還給他，我搬過去養老。」

公子翬一聽，天下還有這樣的傻瓜。現在怎麼辦？自己的餿主意沒被採納，哪天新君即位，知道了這件事，我還有活路嗎？於是他當機立斷，跑到公子允那裡，說：「魯隱公這人太壞了，想殺掉您，永遠霸占君位。」公子允一聽很感動，當即對公子翬發出指示：派刺客，找機會把魯隱公殺了。

有了公子允的指示，公子翬執行起來大刀闊斧。這年冬天，在一個姓寪的小貴族家裡。公子翬的刺客順利地殺掉了正在那裡齋戒的魯隱公，公子允正式即位，是為魯桓公。

這個故事能給我們不少啟示：

首先，道德在中國古代還真有發揮過滿大的作用。
第二，道德已經出現危機，敢率先拋棄道德的人，卻成了勝利者。
第三，千萬千萬不要拒絕壞人的好意，否則你會死得很慘。
從楚簡看矛盾的楚平王
提起楚平王棄疾，大概誰也不會認為他是一個英明的君主。因為就是他殺了伍子胥之父兄伍奢、伍尚，使伍子胥逃奔吳國，借吳兵攻楚，數次打敗楚兵，最後竟攻入郢都。好在這時楚平王已經死了，伍子胥不能解恨，掘開楚平王的墳墓，鞭笞其屍體。如果不是秦國發兵救援，強大的楚國將因此滅亡，這在楚國歷史上可謂第一次奇恥大辱。照理說，像楚平王這樣的君主，可以算是百分之百的昏君了。

可是事情遠不是如此簡單。從史書上看，楚平王不但智商不低，而且為人還很不錯。他是楚共王最小的兒子，在他上面的哥哥，除了老大楚康王繼承君位之外，還有公子圍、公子比、公子子皙，照理說他沒資格繼位為王。但是楚康王死後，公子圍先殺了姪子自立為王，是為楚靈王。這個靈王好大喜功，得罪了很多權臣，又是性情中人，喜歡離開國都，遊山玩水，長年居住在楚國著名的風景區乾溪。趁著這個機會，幾個心懷怨恨的大臣在一起密謀策劃，將他推翻，扶持流亡晉國的公子比即位。

當叛亂的大臣們帶著甲士衝進郢都的時候，楚靈王還在乾溪玩樂。聽到郢都發生政變，自己的兒子全部被殺，他傷心欲絕，從車中撲倒在泥地上，嚎啕大哭。政變的大臣率兵趕到了乾溪，頒下命令，凡是楚靈王身邊的臣屬、衛士，如果及時返回郢都，都可以保留原先的田產、爵位和薪資待遇，否則不但家產充公，還要全部割掉鼻子；敢收留靈王的，誅夷三族。於是靈王的禁衛軍和親信大臣馬上跑得一乾二淨，靈王本人像野鬼一樣，飢餓地在山中徘徊。就在餓得快要死的時候，一個曾經受過他恩惠的大臣申亥收留了他，供給他吃喝，但是也許是想到自己一無所有，復國無望吧，沒過多久，他就悲觀自縊，死在申無宇（申亥之父）家裡。變態的申亥還眼淚汪汪地讓自己的兩個女兒自殺，為靈王殉葬。

楚靈王生前很喜歡自己的幼弟公子棄疾，先後派他率兵滅了陳、蔡兩國，並且慷慨地封他為陳蔡公，管理這兩個大縣。陳、蔡兩縣各擁有一千乘兵車，實力相當於一個中型的諸侯國。那些反叛楚靈王的大臣，正是假借棄疾的命令，仗著棄疾掌握的這些兵力政變成功的。實力如此強大的棄疾，怎麼會甘心讓流亡在外十三年的哥哥公子比當國君呢？他到處散布靈王沒死，將回國報仇的謠言，使郢都空氣緊張，大臣和百姓都因此惶惶不安，最後逼得公子比和令尹子皙先後自殺。他順理成章接替了君位，是為楚平王。

比起他哥哥楚靈王來，楚平王似乎不算壞，這從他們的諡號也看得出來。因為「靈」是惡諡，而「平」卻是美諡。而且，透過出土的竹簡〈平王問鄭壽〉，我們還知道了楚平王的諡號不是單諡，而是雙諡，全稱為「楚景平王」：

競（景）平王就鄭壽，訊之於尸廟，曰：「禍敗因重於楚邦，懼鬼神之為怒，使先王無所歸，吾何改而可？」鄭壽辭不敢答，王固訊之，答：「如毀新都戚陵、臨陽，殺左尹宛、少師無忌？」王曰：「不能。」鄭壽曰：「如不能，君王與楚邦懼難。」鄭壽告有疾，不事。明歲，王復見鄭壽。鄭壽出居路，以須王。與之語少少，王笑曰：「前冬言曰，邦必喪，我及，今何若？」答曰：「臣為君王臣，介備名，君王踐處，辱於老夫。君王所改多多，君王保邦。」王笑：「如我得免，後之人何若？」答曰：「弗知。」

簡文的內容是講楚平王問大臣鄭壽：「楚國禍亂頻仍，恐怕鬼神會發怒，怎麼辦？我怎麼改過才會逢凶化吉。」鄭壽勸道：「如果毀掉新建的城邑戚陵、臨陽，殺掉讒佞的大臣左尹郤宛、少師費無忌，大概可以改善國運。」楚平王搖搖頭，說：「我做不到。」鄭壽就警告他：「如果做不到，那君王和楚國都可能遭受不測之災。」之後鄭壽稱疾不上班。第二年，楚平王又召見鄭壽，笑問他：「你曾經告訴我，我們國家會滅亡，我個人也會趕上這個不幸。現在怎麼樣呢？」言下之意鄭壽當時是危言聳聽。鄭壽只好回答說：「君王已經改了很多，所以國家沒有覆亡。」楚平王又笑問：「如果我能逃脫災禍，接替我的人會怎麼樣？」鄭壽回答：「不知道。」

從這幾段簡文可以得知，楚平王當時對自己國家的危難處境是清楚的。他本來是個名聲很好的人，還在當陳蔡公的時候，晉國貴族叔向就曾讚揚他治政清明，使得朝中苛慝不起，境內盜賊平息，還能控制自己的私欲，以順應民心，很得百姓擁護。這些評價都是很實在的，平王確實因此順利地獲得了國君的位置。可是偏偏在他即位為楚王之後，卻控制不了自己的情欲，最終為國家帶來了滅頂之災。

事情的緣起是因為他的太子建，他為太子建請了兩位師傅，一位太傅，即伍奢；一位少傅，即費無忌。太子建不喜歡費無忌，只和伍奢關係好，費無忌因此懷恨在心。楚平王即位的第二年，派費無忌到秦國去為太子建迎娶妻子，費無忌回來後就勸平王：「秦女長得非常漂亮，君王不如自己娶了享享豔福，太子那邊，幫他另娶一個就是了。」平王一聽當即心動，於是強娶了自己的兒媳，還生了一個孩子，取名為熊珍。

大概是怕太子懷恨，過了四年，平王把十九歲的太子派到邊境城邑城父去守邊。費無忌繼續在平王耳邊讒毀太子：「君王娶了太子的妻子，太子一定會怨恨。現在太子在城父，天天練兵交接諸侯，只怕有朝一日會帶兵來搶奪君位。」平王害怕了，因為當年他也是為楚國守衛邊境，這個楚王的位置就是這麼搶來的。於是他召見伍奢，責備伍奢沒有教導好太子，將伍奢父子殺死，又派司馬奮揚去城父殺太子建。幸好奮揚同情太子建，早早通風報信，讓太子建逃走了。伍奢的小兒子伍子胥逃到了吳國，發憤圖強，天天教吳王練兵，進攻楚國。楚國屢敗，為此疲憊不堪。簡文中平王對鄭壽的抱怨，應當就是在這種時時受到吳國騷擾的處境下發出的。

而且從簡文中可以看到，平王的確不算一位暴君，面對鄭壽的直言不諱，他沒有惱怒。鄭壽因此稱疾抗議，他也沒有在意。要是換個暴君或者昏君，鄭壽肯定性命不保。第二年他召見鄭壽，言語中似乎有些得意，好像證明鄭壽的預言失敗了。但他究竟不敢肯定，因此問鄭壽，即便自己有生之年逃脫了災禍，接替他的太子不知道會怎樣。由此可見，他也知道，這個國家的危機極為深重，絲毫沒有得到解決。果然，在他死後十年，吳兵三戰三敗楚兵，緊追入郢，將他從墳墓裡拖出來鞭屍。他兒子，也就是楚昭王到處流亡，險些性命不保。

奇怪的是，對這位為楚國帶來深重災難的楚平王，楚國人似乎並沒有心懷怨恨。在他剛死的時候，他們不但給了他「景平」兩個字的美諡（按照諡法：治而無眚曰平，布義行剛曰景），而且都衷心擁護他幼小的兒子熊珍為王。甚至他的子孫，一直在楚國占據著很重要的地位。以前我們知道，楚國地位最高的貴族是昭、屈、景三家，號稱「三閭」。按照那時的情況，各諸侯國內的貴族大部分都是王族支脈，楚國也是如此。他們的姓氏不少是取自他們所出王的諡號，比如昭氏就是楚昭王的後裔；屈氏是楚武王的後代，因為後裔封在屈這個地方，所以以地為姓；而景氏就是這位楚平王（全稱為楚景平王）的後裔。一般來說，如果一位楚王不是有較好的政聲，他的後裔不會如此顯赫繁茂。楚武王熊通開拓疆土，在楚國歷史上立有赫赫功勛。楚昭王，也就是楚平王的兒子熊珍，因為不肯使巫祝移過於大臣的舉措，曾受到孔子的讚美，是楚國著名的賢君。楚平王的後裔能和他們並駕齊驅，想來在楚國人的心目中，印象不會太差。

事實上也確實如此，楚國人認為，所有的錯都是費無忌造成的。楚平王死後，費無忌向令尹子常進讒言，殺了左尹郤宛全家，引起了國內一片怨言。沈尹戌因此勸子常道：「殺郤宛這件事，你做錯了。費無忌這個人人品很差，當年太子建逃亡，伍奢被殺，都是費無忌向平王進讒言，掩蔽了平王的耳目。不然的話，以平王的溫惠恭儉，比楚國的先代賢王楚成王、楚莊王還要有過之而無不及，又怎麼會最終搞得和諸侯不睦呢？」

自古以來，政治的敗壞，下層百姓總認為是奸臣的過錯，君王都是好的。這一方面是因為君王身分太高，不敢否定，而將批判指向大臣，還可以不承擔因之帶來的後果；另一方面也反映了愚昧百姓的真實想法，他們心目中的楚平王，確實是有政績的，而且遠遠算不上暴虐。

客觀地說，楚平王的為人的確不差，史書的記載和上面所引的竹簡簡文皆可以為證。他只是因為英雄難過美人關，搶了兒子的老婆，從此在內心留下了內疚和陰影，以致不得不在後來處處彌縫，陷入無休止的被動之中，最終殺親子、屠良臣，鬧得不可收拾。這其中費無忌雖然有比較多的影響，但楚平王本人也不可推卸責任。劉備說得好：「勿以惡小而為之。」說起來是容易的，奈何人究竟難以抵禦私欲，如果當時楚平王能受到一定的約束，即使想那麼做也做不到，又何至於有後來的一系列惡果呢？

生搬硬套地評價一下，算是曲終奏雅：絕對的權力導致絕對的災難，其楚平王之謂乎！

弦高犒師」是《左傳．僖公三十三年》裡的一個故事，說的是秦國想偷襲鄭國，被鄭國商人弦高發現了，弦高就假裝成鄭國的使者，從半道上截住了秦軍，並且假借鄭君的名義送了十二頭牛對秦軍進行犒勞，暗示鄭國已經知道秦軍的行動。當然，這個弦高可實在夠倒楣的，損失夠大，一下子丟了自己的十二頭牛。在當時，的確不是一筆小數目。而這個故事在大部分人眼裡，表現出的是「愛國主義」的典範。

再說春秋時代，每個諸侯國的人都很愛國，似乎又不是那麼回事。就拿一個叫衛懿公的人來說吧，他喜歡養仙鶴，本來這不是什麼毛病，誰沒個愛好，養鶴好歹也是陶冶情操的事情，總比酗酒抽菸等不良嗜好要好些吧。可是偏偏這傢伙仗著自己是個國君，把那些鶴全部封了「大夫」。那時候，「大夫」這個職稱可不是鬧著玩的，官到了這個級別，馬上就有扈從、田產和車馬侍候著，也就是說食有魚、出有車，不奏樂就吃不下飯。人家孔子跑遍天下到處遊說，當了多少年的老師，忙了半天，才混上個下大夫的職稱，憑什麼這鶴一點貢獻沒有，卻過得如此之爽？衛國的老百姓對鶴們嫉妒得要死，可是無可奈何。後來，敵人來攻打衛國，衛懿公慌了，要在太廟授兵，派老百姓去幫他抵禦。老百姓們這下不願意了，說：「有職稱的是鶴，讓牠們去幫你打吧，我們這些賤民哪裡配幫您打仗？」一哄而散，結果這個衛懿公就當了俘虜，國家也滅亡了。

這兩個故事一聯繫，我越來越疑惑了。看來身為哪個國家人，就愛哪個國家，這個說法靠不住。鄭國和衛國都是姬姓國，而且衛國人的祖先是赫赫有名的衛康叔，比鄭國人的祖先周厲王風光多了。難道在康叔他老人家的德化薰陶下的國民，反而會比鄭國國民的品行差？後來我看《左傳》，似乎有點明白了，什麼愛國主義，全是毫無根據，關鍵還是利益。

可是弦高犒師會有什麼利益？這要先從鄭國的歷史和地理位置說起。在所有的姬姓國中，鄭國是建國最晚的，一直拖延到西周晚期。它的故土本來在關中的鄭地，後來周平王在犬戎的壓力下東遷，鄭國也很怕，只好跟著宗主跑。它採取坑蒙拐騙的手段奪取了今天河南的一大塊土地，將那地方改名為新鄭。不過它的土地究竟有限，特別是晉國和楚國崛起後，它夾在兩個大國之間，十分難受。所以縱觀一部春秋史，沒有哪個國家是像鄭國這樣反覆無常的了：晉國打來了，就和晉國建立外交關係；楚國來了，就背棄晉國，投入楚國的懷抱。鄭國的貴族自己也不諱言這一點，也毫不為恥，在和晉國數不清的盟誓中的某次，它的盟辭就是：「天禍鄭國，使介居二大國之間，大國不加德音，而亂以要之，使其鬼神不獲歆其禋祀，其民人不獲享其土利，夫婦辛苦墊隘，無所底告。自今日既盟之後，鄭國而不唯有禮與強可以庇民者是從，而敢有異志者，亦如之！」看，它清楚地說了，我鄭國如果不老老實實地服從軍事政治力量強大的國家，那將會受到鬼神的報應。當時參與盟誓的晉國大夫荀偃怒道：「你這樣寫盟書怎麼行，這不是貪利忘義的做法嗎？」鄭國的貴族狡猾地回答：「改盟誓已經來不及啦！盟誓都可以隨便改，那麼還有什麼不能做的？」不過說老實話，鄭國要是不狡猾，早就被楚國和晉國瓜分了。再說人家鄭國也可憐啊。本來在河南一角好好地過日子，招誰惹誰了？偏偏你們一定要輪流去打人家。每次大軍一到，鄭國都是免不了要出血，用納稅人的錢去招待兩邊的士兵。

鄭國好像也的確是個富裕的不得了的國家，國土就那麼點，可是商人卻很多。我們在先秦典籍中經常看見鄭國的商人，在天下到處奔走，倒買倒賣，可見鄭國是很重視商業的。河南又是天下的輻輳，地勢平坦，交通發達，經商大概比較方便。而且，我還懷疑，鄭國的服務業也很發達，比如唱歌跳舞啊，都是鄭國的特長。這讓後來堅持農業社會倫理的孔子很看不慣，氣得說要「放鄭聲，遠佞人」。這也是有證據的，鄭國每次要外交，總要送幾個藝人致敬。比如魯襄公十一年，鄭國就賄賂了晉侯三個名叫「師悝」、「師觸」、「師蠲」的樂師，外加廣車、 軘車各十五乘，總共兵車百乘，歌鐘二肆，還有一套套的鎛磬，外加妙齡女郎十六個。送美女我們都能理解，可是送三個瞎眼的糟老頭子（那時候一般樂師似乎都是盲人）給晉侯，而且排在禮品清單的第一頁，遠遠位居美女之上，這是為什麼呢？這說明那三個糟老頭子的確有點本事，的確讓鄭國拿得出手，拿得有恃無恐。再比如魯襄公十五年，鄭國為了和宋國外交，又送給宋國馬車四十乘，外加「師烷」、「師慧」兩個樂師。可見，把藝人當禮品的確成了鄭國的特色，只此一家，別無分店。大家都知道，國家越發達，娛樂產業在 GDP 中所占的比重越大。所以鄭國雖然夾在晉、楚這兩個不要臉的大國之間，仍然活得很好，實在不是沒有原因的。他們雖然對晉國謙稱自己是「蕞爾邦」，大概只是一種不敢過分炫富的矛盾心理吧。

不過鄭國雖然適合發展娛樂產業，可是還得有配套政策啊。鄭國也一樣，昭公十六年發生的一個小故事可以透露一點訊息。那年的三月，正是草長鶯飛的季節，晉國的上卿韓宣子到鄭國來做友好訪問。說是訪問，其實就相當於視察。韓宣子是晉國的執政，而晉國是春秋兩百多年的霸主，得罪了韓宣子，就相當於得罪了整個晉國的士兵，絕對沒有好果子吃。所以鄭國國君親自接見，在鄭國的國賓館舉行了會晤。主客雙方在友好的氣氛中交換了意見，可是在某些主要問題上卻並沒有達成一致。原來韓宣子有一個玉環，可能很值錢。這玉環早先應該是一對，可是韓宣子只有其中一個，另一個在鄭國某富商的手裡。自然，他來鄭國的目的之一就是把另外那個玉環弄到手。在酒席上，他就對鄭侯委婉地表達了這個要求，猜想鄭國肯定會趕著送上。孰料鄭國的執政子產卻不肯買帳，他解釋說：「您老人家要的那個玉環不是我們官府的東西，我們國君恐怕愛莫能助。」其他幾個鄭國貴族聽見子產這樣漫不經心地打官腔，說些不著調的外交辭令，嚇得不輕，趕忙將他拉到一邊，勸道：「老兄啊，你怎麼能這麼說話？這個韓宣子我們可惹不起啊，要是他不高興，回去帶了幾萬士兵來，我們可就虧大了啊，後悔也來不及了啊。老兄何必吝惜一個玉環呢？還是想辦法從商人那裡找來給他，破財消災吧。」子產說：「你們才真叫不懂事呢，是韓宣子又怎麼了？他要什麼就給他什麼，這不但不符合禮節，還會助長他的貪欲，到時我們哪有那麼多寶物來滿足他。而且他因為一個玉環的罪狀來討伐我們，傳到國際上去，他好意思嗎？在聯盟大會上，他好發言嗎？ 」

說實話，這個韓宣子畢竟是晉國的貴族，算不上無賴，比起後世的王瑾、魏忠賢等人，品行高多了。他看在國君那裡要不到，只好親自去找那個商人買。商人嘟囔說：「賣給你沒問題，不過按規矩，這件事得向我們的政府首腦彙報一下。」韓宣子就又去找子產，很疑惑地問：「先前跟你說到玉環的事，你不肯答應，說政府管不了商人。現在我去向那商人買，他卻說一定要先報告政府，能不能說說原因？」子產明白是怎麼回事了：這傢伙肯定是捨不得花大價錢，拚命壓價強買，於是解釋道：「老韓啊，你不知道啊，當年我先君桓公來這裡建國的時候，是和一幫商人一起來的，他們共同艾殺蓬蒿，開闢了這個地方，而且定下了世世代代不能違背的盟誓，盟誓辭裡說了：『你不要背叛我，我也不強買你的貨物，更不會強搶你的貨物。你有什麼財寶，我也不想染指。』就是靠著這樣的盟誓，我們和商人們才能相保以至於今天。現在您老人家來訪問我們國家，卻想叫我們政府強搶商人的東西，這是嚴重的違背盟誓的行為，會遭天譴的！而且如果我們開了這個惡例，商人們就不再會覺得鄭國是安全的了，很快就會跑得一乾二淨了—實話說吧，如果鄭國娛樂產業衰落下去，今後你們再來要錢，我們恐怕也拿不出了。因為稅收的來源沒有了。」韓宣子一聽，傻眼了，只好訥訥地說：「那個玉環我不要了。」因為殺雞取卵的方法他不想做，也不敢做，假如回去後遭到國君責難，那就死有餘辜了。

我繞著圈子說了這麼長的話，無外乎就是想說，弦高的所謂愛國主義是可疑的。他是個商人，懂得鄭國如果完蛋的話，再也不會有比它更好的政府來保障商人的權益了，那時還沒有其他國家的政府肯和商人簽訂盟誓。他雖然丟了十二頭牛，可是換來了更長遠的利益。更何況，我們還可以假設，他的那十二頭牛，鄭國政府有可能會賠償給他。他真是個幸運兒，因這件事，他真可以說是名利雙收呢！
〈昭王毀室〉和春秋末年社會思潮
自從近十多年的戰國文字資料《郭店楚墓竹簡》和《上海博物館藏戰國楚竹書》出版以來，很多研究思想史的學者都聲稱，這些失傳古書的出土，將使我們對先秦兩漢思想史有新的認識，尤其可以增加我們對於先秦儒家子思學派的了解。更有學者認為，這些竹書將在一定程度上改寫思想史。我個人一向覺得這些觀點過於誇張，因為那些資料所反映的思想基本上能在傳世文獻中找到。但是《上海博物館藏戰國楚竹書（四）》中有一篇〈昭王毀室〉，卻讓我對先秦，尤其是楚國國君和百姓之間的關係跌破眼鏡。

〈昭王毀室〉講的是春秋時期楚昭王時代的一個故事。全文記載在五枝竹簡上，簡文略有殘缺，但內容基本完整，不影響我們對文意的理解。為了便於講述，我先將竹簡釋文引在下面，由於竹簡通假字較多，現參照一些學者的考釋觀點，基本採用通行字隸定：

昭王為室於死（夷）𣳟（沮）之滸，室既成，將落之。王誡邦大夫以飲酒，既型（請）落之，王入，將落。有一君子喪服冕，廷，將閨。 稚（寺）人止之曰：「君王已入室，君之服不可以進。」不止，曰：「小人之告（此處有缺漏字），將斷於今日。爾必止小人，小人將召寇。」稚（寺）人弗止，至閨。卜令尹陳省為視日，告：「僕之母（毋）辱君王，不幸僕之父之骨在於此室之階下。僕將亡老……以僕之不得併僕之父母之骨，私自（坿？）。」卜令尹不為之告。「君不為僕告，僕將召寇。」卜令尹為之告……曰：「吾不知其爾墓，爾姑須既落，焉從事。」王徙居於坪蕅 （瀨），卒以大夫飲酒於坪蕅 （瀨），因命至俑（傭）毀室。

總的來說，這篇簡文的敘述，和一般的傳世古書相比，言辭稍嫌簡單。比如有的地方省略了說話者，粗看過去，不容易讀懂。還有個別詞語不好理解，有待於進一步研究。但基本文意還算可以貫通，我這裡就稍微詳細地解說一下。故事說的是楚昭王在夷水和沮水之間的岸邊建了一座新宮殿，將要舉行落成典禮，召集了朝廷士大夫去飲酒慶賀。有一個君子穿著喪服，戴著孝帽也想闖進去。新宮的守門人兩手張得像鳥翼一樣，鼻子裡噴出一串串不耐煩：「去去去，你這小子穿戴著孝服，還東跑西跑的，真晦氣！快滾，大王正在飲宴，可不想見你這個掃把星。」闖宮者語氣非常謙恭，但是軟中有硬：「小人要向大王告狀，而且一定要在今天見到大王。要是你阻止小人，小人只好去招引強盜來了。」守門人倒吸了一口冷氣，讓他進去了。闖宮人心裡不屑地哼了一聲：也是個沒底氣的傢伙。他大搖大擺地往裡面走，一直走到宮中的小門處，終於驚動了楚王。

卜令尹陳省今天正排上為昭王值班，當然要履行職責，也攔住他：「哪來的野小子，王宮也敢闖？」闖宮人站住了，還是不卑不亢地扠手行禮：「僕並不是想侮辱君王，只不過僕父親的骨頭埋在這個房子的臺階之下。僕將祭祀……僕現在不能把僕的父母的遺骨合葬了。你老人家是君王的值日官員，你看怎麼辦吧？」看，他語氣多含蓄啊，自稱「僕」。可是在中國古代，光憑這麼點謙卑就想打動官僚，那不是做夢嗎？卜令尹當然不想為他報告這件事，說：「滾蛋滾蛋，什麼貨色，還想見我們大王。」

闖宮人沒有辦法，只好又來硬的：「君不肯為僕報告大王，那僕只好去招引強盜來囉。」看，又是這一套，不過很有效。卜令尹聽到這句，臉色變了，趕緊跑去報告：「大王大王，不好啦不好啦，有個人要見你，說如果你不見，他就要招引強盜來。」後面是什麼，簡文有殘缺，總之是楚王屈服了，怯懦地向此人賠禮：「我不知道這個地方是你家的祖墳，你稍微等一下，我典禮完畢就走，到時你想幹什麼就幹什麼。」闖宮人正色道：「大王，知錯就改，果然英明，不過，還等您喝完這輪，這不是怙惡不悛嗎？再說了，您也別急著走，您瞧瞧，我這細手臂細腿的，手無縛雞之力，怎麼拆？您要這麼一拍屁股走人，把這麼大的房子留在這裡可不行。」天哪！人家君王都不要那宮殿了，還不讓人走。

楚王聽他這麼一鬧，生怕他再叫囂要「召寇」，趕忙息事寧人地說：「好吧，先生不要生氣，我幫您拆掉算了，保證把現場清理得乾乾淨淨的。」說著楚王馬上招來手下：「還愣在這裡幹什麼？還不趕快準備幾輛馬車，到郢都找人來幫這位先生拆牆。」

關於闖宮者的身分，我們需要根據簡文裡人物的稱謂討論一下。簡文開始說闖宮者是「一君子」，按照我們對春秋時代的普遍認識，君子是指貴族，那麼這個闖宮人還不算是普通老百姓。但是一個貴族怎麼動不動就聲言去招引盜賊？當然，「召寇」的「寇」我們既可以理解為普通群盜，也可以理解為他國的軍隊。在先秦古書中，「寇」當他國軍隊來講的例子是屢見不鮮的。然而就算是一個小貴族隨便以招引他國軍隊來威脅他的君王，也是頗不尋常的。這個君子對守宮門的人自稱「小人」，可能是一種自謙的稱呼，並不一定表示自己的地位不如守門人，也不能說明他是一個普通百姓。在《包山楚簡》裡，有很多官吏對上級官吏都自稱「小人」，而普通百姓向官吏告狀也自稱「小人」，這說明這個自稱不代表他們的社會身分，只代表官階高低。何況簡文中的闖宮人對守門人的稱呼是「爾」，這是一種不很客氣的稱呼，這至少說明，那個守門人的地位不見得比他高。但是以「小人」自稱，又至少說明，他也不是什麼大人物。按照《周禮．天官冢宰》的記載，貴族按照等級的不同，他們墳墓的封土規格也是不同的。孔子說：「古者墓而不墳。」說的也是比較古老的情況，在春秋時代，也許開始有封土的墳墓了，有的學者就贊同那時有封土墓。如果闖宮人是個大貴族，他的家族墓地一定不至於太不顯眼，以至於楚王派去建宮殿的人可以將之完全忽視。何況，楚王在新宮落成典禮時，命令貴族們都去飲宴，如果闖宮者地位很高，應該會在飲宴的邀請者行列。這些都說明，這個闖宮者的地位也不會太高。

闖宮人見到卜令尹的時候換了一種稱呼，自稱「僕」。在當時的楚國，「僕」有可能是面對楚王時才採用的一種專門稱呼。在《包山楚簡》一三一號到一三九號簡記載的一個完整案例當中，告狀的幾個普通百姓—「陰人」對陰縣的地方官都自稱「小人」，後來因為陰縣的地方官吏沒有為他們公正斷案，他們又直接上書楚王。在上告楚王的文書中，他們自稱「僕」，可以為證。在上揭的這段簡文中，卜令尹顯然是作為「視日」（楚王辦公室的值日官），代表楚王來詢問闖宮者的，所以闖宮者實際上是對楚王說話，符合對楚王自稱「僕」的慣例。至於楚國人為什麼都對楚王自稱「僕」，還有待研究，也許僅僅是想表明這樣一種觀念：楚國的所有民眾，無論貴賤，對於他們的君王來說都是僕人。

再分析簡文內容，有趣的是，一國之君建個宮殿竟不能隨心所欲，國人因為這宮殿建在自己的家族墓地上，就穿著孝服去搗亂。而且守宮人和卜令尹一開始都不想理會他，卻在他一再敦告「將召寇」的威脅下，不得不報告楚王，楚王最後也只能將新建好的宮殿拆除了事，這和我們印象中的古代社會簡直大相逕庭。《詩經》裡說：「普天之下，莫非王土。」這是講周王的權威。至於諸侯，在自己的封國內，也自然是可以隨心所欲的。春秋時代的楚國，雖然也有大大小小的封君貴族，弒君之事也偶爾會發生，但那都是上層貴族內部之間的衝突，具體到一個小人物以招引強盜來威脅君王改變主意，這種情況似乎還聞所未聞。西方君主立憲制有一個自豪的說法是，普通百姓對自己的房子有絕對主權，「風能進，雨能進，國王不能進」。但在楚國，連一個百姓的墓地君王也不能隨便徵用。從表面上看，民權幾乎要駕君權而上之了。當然，它們仍有具體差別，西方公民是透過法律制約君王；而楚國小貴族卻只能揚言「召寇」來威脅君王，兩者之間是不可同日而語的。後者和「水能載舟，亦能覆舟」的道理仍是一樣的，君王怕的是被武力推翻，總歸來說在思想上沒有太大新意。只是由一個國民對君王親口威脅，這種情況過於奇怪罷了。

至於闖宮者為什麼兩次以「召寇」來威脅楚王，也許正好反映了一種特定時代的社會狀況。我們知道，楚昭王在位的時候，楚國一直不大太平，屢次和以吳國為首的諸侯國發生戰爭。楚昭王十年的冬季，更是大敗於吳國，吳兵還直接攻入了楚國的郢都。昭王倉皇出亡，途中多次遇險，一開始被雲夢人射傷，繼而差點被鄖公的弟弟殺掉，最後逃到隨國，也險些被出賣。他對這些遭遇可能記憶猶新，所以當闖宮人威脅說要「召寇」時，他很快軟了下來。而且，這次險些亡國的事件就是和他父親楚平王的胡作非為有關。當年楚平王因為聽信奸臣讒言，殺了大臣伍子胥的父兄，伍子胥出逃吳國，發誓報仇，親自訓練吳國的軍隊，並率兵長驅郢都，雖然楚平王已死，卻仍被伍子胥掘墓鞭屍。按照文獻記載，伍氏家族也是楚國的貴族，血統高貴，符合「君子」身分。所以楚昭王一聽到這個闖宮人也要「召寇」，擔心又惹來破國的慘劇，只好服軟了。春秋時代，「楚材晉用」赫赫有名，楚王不愛惜自己的人才從而為國家帶來禍患，這在昭王腦子裡也許留下了永恆的陰影。

    """
    
    #get_server_flashcard_from_text(trim)
    #about = build_flashcards_from_wordlist(get_words_in_text(trim))
    get_dictionary_words_not_in_flashcards(textprocessing.split_text(trim))

    j_chinese = filter_chinese_lines(trim)

    #generate_flashcard_test(j_chinese)

    sample_text = "This is a sample text with some words that are not on HSK1-2 level. For example, 'abandon', 'zealous', and 'quintessential'."

    process_text_in_chunks(j_chinese,chunk_size=500)




    print("Flashcards generated and saved.")
    