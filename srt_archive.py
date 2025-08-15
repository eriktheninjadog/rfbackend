import os
import re
import random
import subprocess
import jieba
from typing import List, Dict, Tuple, Set, Optional
import pysrt
import paramiko
from scp import SCPClient


class SrtArchive:
    
    def __init__(self, directory_path: str):
        """Initialize the SRT archive with a directory of SRT files.

        Args:
            directory_path: Path to the directory containing SRT files
        """
        # Create directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)
        self.directory_path = directory_path
        self._srt_files = {}  # Map of filename to parsed SRT content
        self._index = {}      # Map of words to (file, line_num, timestamp) tuples
        self._all_lines = []  # List of (text, file, timestamp) tuples
        self._initialized = False
    
    def download_srt_files(self):
    # Define source and destination paths
        remote_path = "erik@storage.eriktamm.com:/home/erik/srt_archive/*.srt"
        local_dir = self.directory_path

        # Create the destination directory if it doesn't exist
        if not os.path.exists(local_dir):
            print(f"Creating directory: {local_dir}")
            os.makedirs(local_dir)

        # Execute scp command to download all files
        print(f"Downloading files from {remote_path} to {local_dir}...")
        try:
            subprocess.run(
                ["scp", "-r", remote_path, local_dir], 
                check=True
            )
            print("Download completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error downloading files: {e}")
            return False 
        
    def _initialize(self):
        """Parse all SRT files in the directory and build the index."""
        if self._initialized:
            return
        # Check if there are SRT files in the directory
        srt_files_exist = any(filename.lower().endswith('.srt') for filename in os.listdir(self.directory_path))

        # If no SRT files found, try to download them
        if not srt_files_exist:
            print("No SRT files found. Attempting to download...")
            # Try with SSH key first (assuming default location)
            if not self.download_srt_files():
                # Prompt for credentials if automatic download fails
                print("Automatic download failed. Please provide credentials.")
        
        for filename in os.listdir(self.directory_path):
            if filename.lower().endswith('.srt'):
                file_path = os.path.join(self.directory_path, filename)
                try:
                    subs = pysrt.open(file_path, encoding='utf-8')
                    self._srt_files[filename] = subs
                    
                    # Index each subtitle line
                    for sub in subs:
                        text = sub.text.replace('<i>', '').replace('</i>', '').replace('\n', ' ')
                        timestamp = f"{sub.start} --> {sub.end}"
                        
                        # Store the line for random access
                        self._all_lines.append((text, filename, timestamp))
                        
                        # Index words for searching
                        words = jieba.cut(text)
                        for word in words:
                            word = word.strip()
                            if word:
                                if word not in self._index:
                                    self._index[word] = []
                                self._index[word].append((filename, len(self._all_lines) - 1, timestamp))
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
        
        self._initialized = True

    def search(self, search_terms: List[str], match_all: bool = False) -> List[Dict]:
        """Search for lines containing the specified terms.

        Args:
            search_terms: List of terms to search for
            match_all: If True, lines must contain all search terms. If False, lines with any term will be included.

        Returns:
            List of dictionaries with 'text', 'file', and 'timestamp' keys
        """
        self._initialize()
        
        results = []
        matching_lines = set()
        
        # Find line indices containing each search term
        term_results = {}
        for term in search_terms:
            term_results[term] = set()
            for word, occurrences in self._index.items():
                if term in word:
                    for filename, line_idx, timestamp in occurrences:
                        term_results[term].add((filename, line_idx))
        
        # Determine which lines to include based on match_all flag
        if match_all:
            # Get lines that contain all search terms
            common_lines = None
            for term, line_set in term_results.items():
                if common_lines is None:
                    common_lines = line_set
                else:
                    common_lines &= line_set
            
            matching_lines = common_lines or set()
        else:
            # Get lines that contain any search term
            for term, line_set in term_results.items():
                matching_lines.update(line_set)
        
        # Format the results
        for filename, line_idx in matching_lines:
            text, _, timestamp = self._all_lines[line_idx]
            results.append({
                'text': text,
                'file': filename,
                'timestamp': timestamp
            })
        
        return results
    
    def get_random_lines(self, count: int = 1, min_length: int = 0, max_length: Optional[int] = None) -> List[Dict]:
        """Get random lines from the SRT files.

        Args:
            count: Number of random lines to retrieve
            min_length: Minimum character length of lines
            max_length: Maximum character length of lines (if None, no maximum)

        Returns:
            List of dictionaries with 'text', 'file', and 'timestamp' keys
        """
        self._initialize()
        
        if not self._all_lines:
            return []
        
        # Filter lines by length
        eligible_lines = []
        for idx, (text, _, _) in enumerate(self._all_lines):
            length = len(text)
            if length >= min_length and (max_length is None or length <= max_length):
                eligible_lines.append(idx)
        
        if not eligible_lines:
            return []
        
        # Select random lines
        result_indices = random.sample(eligible_lines, min(count, len(eligible_lines)))
        results = []
        
        for idx in result_indices:
            text, filename, timestamp = self._all_lines[idx]
            results.append({
                'text': text,
                'file': filename,
                'timestamp': timestamp
            })
        
        return results


if __name__ == "__main__":
    # Example usage
    archive = SrtArchive("srt_directory")
    
    # Search for lines containing "你好" and "世界"
    search_results = archive.search(["你好", "世界"])
    for result in search_results:
        print(f"File: {result['file']}, Time: {result['timestamp']}")
        print(f"Text: {result['text']}")
        print()
    
    # Get 5 random lines with 10-50 characters
    random_lines = archive.get_random_lines(count=5, min_length=10, max_length=50)
    for result in random_lines:
        print(f"Random: {result['text']}")