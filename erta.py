import json
from typing import List, Dict, Tuple, Iterator, Optional, Union



class ERTATextProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = {"content": [], "dictionary": {}}

    def read_file(self) -> None:
        """Read the ERTAText JSON file and load its content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"ERTAText file not found: {self.file_path}")
        except json.JSONDecodeError:
            print(f"Invalid ERTAText JSON in file: {self.file_path}")

    def write_file(self) -> None:
        """Write the current data to the ERTAText JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

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

# Example usage
if __name__ == "__main__":
    processor = ERTATextProcessor("ertatext_data.json")

    # Read existing ERTAText file (if it exists)
    processor.read_file()

    # Add words to ERTAText content with timepoints in seconds
    processor.add_word_to_content("word1", 1.0)
    processor.add_word_to_content("word2", 1.5)
    processor.add_word_to_content("word3", 2.0)
    processor.add_word_to_content("word4")  # No timepoint
    processor.add_word_to_content("word5", 2.5)

    # Add words to ERTAText dictionary
    processor.add_word_to_dictionary("word1", "pronunciation1", "definition1")
    processor.add_word_to_dictionary("word2", "pronunciation2", "definition2")
    processor.add_word_to_dictionary("word3", "pronunciation3", "definition3")

    # Write to ERTAText file
    processor.write_file()

    # Demonstrate retrieval from ERTAText
    print("ERTAText Content:", processor.get_content())
    print("ERTAText Dictionary:", processor.get_dictionary())
    print("ERTAText Info for 'word1':", processor.get_word_info("word1"))

    # Demonstrate the undefined words function
    undefined_words = processor.get_undefined_words()
    print("Undefined words in ERTAText content:", undefined_words)

    # Demonstrate the enumerate_content function
    print("Enumerated content:")
    for index, word, timepoint in processor.enumerate_content():
        print(f"  {index}: {word} (Timepoint: {timepoint} seconds)")

    # Demonstrate the get_word_at_timepoint function
    print("Word at timepoint 1.75 seconds:", processor.get_word_at_timepoint(1.75))
    print("Word at timepoint 2.2 seconds:", processor.get_word_at_timepoint(2.2))