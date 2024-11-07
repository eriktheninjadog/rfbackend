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
            f"Pick out the news from the following text, write a summary of 400 words of each news in simple English that someone with a B2 level can understand. Ignore any news related to sports.\n{news_text}"
        )"""
        summary = openrouter.open_router_nemotron_70b(
            f"Pick out the news from the following text, write a summary of 400 words of each news in simple English that someone with a B2 level can understand. Ignore any news related to sports.\n{news_text}"
        )
        return summary
    except Exception as e:
        print(f"Error summarizing news: {e}")
        return ""

def translate_to_cantonese(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        translated = openrouter.open_router_chatgpt_4o_mini("You are a Cantonese translator",
            f"Translate the following text to spoken Cantonese, like how people actually speak in Hong Kong. Make it so simple that a 7-year-old can understand it. Personal Names, place names (Toponyms), Brand names, organization names and product names in English. Do not include pronouncation guide. Here is the text:\n{text}"
        )
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""



def keywords(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        translated = openrouter.open_router_nemotron_70b(
            f"Extract keywords to understand this text. Make a list of the keywords, repear each keywords three times, tab and then the  definition in simple Cantonese that a child can understand. Like this keyword,keyword,keyword\tdefinition\nkeyword,keyword,keyword\tdefinition\n  Here is the text:\n{text}"
        )
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""


def wrap_in_ssml(text: str) -> str:
    """Translate the text to spoken Cantonese using OpenRouter."""
    try:
        translated = openrouter.open_router_chatgpt_4o_mini("You are an SSML assistant, formating text to SSML trying to make a text sound natural",
            f"Convert this text into SSML format. Use pauses to make it more suitable for listening. Only return the SSML. Here is the text:\n{text}"
        )
        idx = translated.find('<speak>')
        translated = translated[idx:]        
        return translated
    except Exception as e:
        print(f"Error translating to Cantonese: {e}")
        return ""

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
                akeywords = keywords(mp3_chunk)
                fulltext = akeywords + "\n\n" + mp3_chunk
                ssml_text = wrap_in_ssml(fulltext)
                create_and_upload_files(fulltext,fulltext, f"{chunk_index}_{i}")

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
        'https://news.rthk.hk/rthk/en/'
    ] * 11  # Repeated 11 times to match the original list

    for url in urls:
        process_news(url)

    # Example usage of the new function with a file
    #file_path = "sample_text.txt"
    #process_file_content(file_path)

if __name__ == "__main__":
    main()