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

# ... (previous functions remain the same)

def translate_simplify_and_create_mp3(text: str) -> None:
    """
    Translate the given text to Cantonese, simplify it, create an MP3, and upload it.
    If the text is longer than 3000 characters, it's split into smaller parts and
    processed in series.
    """
    try:
        # Split the text into chunks if it's longer than 3000 characters
        text_chunks = split_long_text(text) if len(text) > 3000 else [text]

        for chunk_index, text_chunk in enumerate(text_chunks):
            print(f"Processing chunk {chunk_index + 1} of {len(text_chunks)}...")

            # Translate and simplify the text chunk
            translated_text = translate_to_cantonese(text_chunk)
            if not translated_text:
                print(f"Translation failed for chunk {chunk_index + 1}. Skipping this chunk.")
                continue

            # Split the translated text into smaller chunks for MP3 creation
            mp3_chunks = split_text(translated_text)

            # Create MP3 and upload for each chunk
            for i, mp3_chunk in enumerate(mp3_chunks):
                create_and_upload_files(mp3_chunk, f"{chunk_index}_{i}")

            print(f"Successfully processed chunk {chunk_index + 1} with {len(mp3_chunks)} MP3 parts.")

        print(f"Finished processing all {len(text_chunks)} chunks of the original text.")
    except Exception as e:
        print(f"Error in translate_simplify_and_create_mp3: {e}")

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
        'https://www.nbcnews.com/',
    ] * 11  # Repeated 11 times to match the original list

    for url in urls:
        process_news(url)

    # Example usage of the new function with a file
    file_path = "sample_text.txt"
    process_file_content(file_path)

if __name__ == "__main__":
    main()