import json
from typing import List, Dict, Tuple, Iterator, Optional, Union, Callable


import json
import re



class ERTATextProcessor:
    def __init__(self, file_path: str = None, text: str = None, splitter: Callable[[str], List[str]] = None):
        self.file_path = file_path
        self.data = {"content": [], "dictionary": {}}

        if file_path:
            self.read_file()
        elif text and splitter:
            self.populate_content_from_text(text, splitter)

    def read_file(self) -> None:
        """Read the ERTAText JSON file and load its content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"ERTAText file not found: {self.file_path}")
        except json.JSONDecodeError:
            print(f"Invalid ERTAText JSON in file: {self.file_path}")

    def populate_content_from_text(self, text: str, splitter: Callable[[str], List[str]]) -> None:
        """Populate the content array using the provided text and splitter function."""
        words = splitter(text)
        self.data['content'] = [{"word": word} for word in words]

    def write_file(self) -> None:
        """Write the current data to the ERTAText JSON file."""
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)
        else:
            print("No file path specified. Cannot write to file.")

    def add_word_to_content(self, word: str, timepoint: Optional[float] = None) -> None:
        """Add a word to the ERTAText content list with an optional timepoint in seconds."""
        if timepoint is not None:
            self.data['content'].append({"word": word, "timepoint": timepoint})
        else:
            self.data['content'].append({"word": word})

    def add_word_to_dictionary(self, word: str, pronunciation: str, definition: str) -> None:
        """Add a word to the ERTAText dictionary with its pronunciation and definition."""
        self.data['dictionary'][word] = [pronunciation, definition]

    def get_word_info(self, word: str) -> Tuple[str, str]:
        """Get the pronunciation and definition of a word from the ERTAText dictionary."""
        if word in self.data['dictionary']:
            return tuple(self.data['dictionary'][word])
        return ("", "")

    def get_content(self) -> List[Dict[str, Union[str, float]]]:
        """Get the ERTAText content list."""
        return self.data['content']

    def get_dictionary(self) -> Dict[str, List[str]]:
        """Get the ERTAText dictionary."""
        return self.data['dictionary']

    def get_undefined_words(self) -> List[str]:
        """
        Return a list of words from the content that are not in the dictionary.
        """
        undefined_words = []
        for item in self.data['content']:
            if item['word'] not in self.data['dictionary']:
                undefined_words.append(item['word'])
        return list(set(undefined_words))  # Remove duplicates

    def enumerate_content(self) -> Iterator[Tuple[int, str, Optional[float]]]:
        """
        Return an enumerator for the content.
        Yields tuples of (index, word, timepoint) for each item in the content.
        """
        for index, item in enumerate(self.data['content']):
            yield (index, item['word'], item.get('timepoint'))

    def get_word_at_timepoint(self, target_timepoint: float) -> Optional[str]:
        """
        Return the word at or immediately before the given timepoint.
        Returns None if no word is found before the timepoint.
        """
        last_word = None
        for item in self.data['content']:
            if 'timepoint' in item:
                if item['timepoint'] > target_timepoint:
                    return last_word
                last_word = item['word']
        return last_word


import openrouter

def beginner_chinese_splitter(str):
    return json.loads( openrouter.do_open_opus_questions("Split this text into useful words,idiomatic expressions and idioms suitable for a Cantonese intermediate learner. Make the return in json like ['word1','word2','word3',...]. Only return json, no other text.\n"+ str) )


def chinese_ai_lookup(words):
    ask = json.dumps(words)
    return json.loads( openrouter.do_open_opus_questions("Take each one of the chinese words in the provided json structure and return json array looking like this ['words','jyutping','english definition']. Only return json, no other text .\n"+ ask) )



import requests

def call_api(base_url, endpoint, data):
    # Construct the full URL
    url = f"{base_url}/{endpoint}"
    # Set up the parameter
    try:
        # Make the GET request
        response = requests.post(url,json=data)
        
        # Check if the request was successful
        response.raise_for_status()        
        # Return the JSON response
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

import constants

def remote_dictionary(word):
    data = {constants.PARAMETER_SEARCH_WORD:word }
    ret = call_api("https://chinese.eriktamm.com/api","dictionarylookup",data)
    return ret


# Example usage
if __name__ == "__main__":
    # Example splitter function
    
    thetext = """
  北韓領袖金正恩召開國防和安全會議。他指明當前的軍事活動方向，提出了在啟動國家防衛力量、行使自衛權來維護國家主權和安全利益方面的任務。

金正恩在會上闡明黨和政府強硬的軍事政治立場。

另一方面，北韓勞動黨副部長金與正昨日通過朝中社發表談話，指無人機滲透至平壤事件由南韓軍方主導，美國應為其負責，但她未有提出相關證據。

南韓傳媒分析，金與正的談話是要反駁南韓軍方指稱平壤未能確認無人機在平壤散佈傳單的講法。
    """
    
    pop = ERTATextProcessor(text=thetext,splitter=beginner_chinese_splitter)


    for i in pop.get_undefined_words():
        result = remote_dictionary(i) 
        if result['result'] != None:
            pop.add_word_to_dictionary(i,result['result'][1],result['result'][2])   


    for i in pop.get_undefined_words():
        print(i)
        
    ret = chinese_ai_lookup(pop.get_undefined_words())
            
    for i in ret:
        print(str(i))


    """
    
    def simple_splitter(text: str) -> List[str]:
        return text.split()

    # Create an ERTATextProcessor instance with a text string and splitter function
    text = "This is a sample text for testing the new constructor."
    processor = ERTATextProcessor(text=text, splitter=simple_splitter)

    # Print the content to verify it's been populated
    print("ERTAText Content:", processor.get_content())

    # Add some words to the dictionary
    processor.add_word_to_dictionary("sample", "sam-puh l", "a small part or quantity intended to show what the whole is like")
    processor.add_word_to_dictionary("testing", "tes-ting", "the process of evaluating a system or its component(s) with the intent to find whether it satisfies the specified requirements or not")

    # Print the dictionary
    print("ERTAText Dictionary:", processor.get_dictionary())

    # Get undefined words
    undefined_words = processor.get_undefined_words()
    print("Undefined words in ERTAText content:", undefined_words)

    # Enumerate content
    print("Enumerated content:")
    for index, word, timepoint in processor.enumerate_content():
        print(f"  {index}: {word} (Timepoint: {timepoint} seconds)")

    # Try to write to a file (this will print a message since no file path was specified)
    processor.write_file()
    """