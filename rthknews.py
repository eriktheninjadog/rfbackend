
import requests
from bs4 import BeautifulSoup

import newspaper
from newspaper import Article


def get_all_links(url):
    try:
        
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    
        # Send a GET request to the URL
        response = requests.get(url,headers=headers)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> tags (which define hyperlinks)
        links = soup.find_all('a')

        # Extract the href attributes
        urls = [link.get('href') for link in links if link.get('href')]

        # Filter out non-article links (you may need to adjust this based on the website structure)
        #urls = [url for url in urls if '/5' in url]
        return urls
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []



def extract_src_links(url, depth=1):
    """
    Extract links from src attributes in elements like img, iframe, script, etc.
    Follows links one level deep if depth=1
    """
    visited_urls = set()
    all_src_urls = []
    
    def process_url(current_url):
        if current_url in visited_urls:
            return
        
        visited_urls.add(current_url)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find elements with src attributes (img, iframe, script, video, etc.)
            elements_with_src = soup.select('[src]')
            
            # Extract the src attributes
            src_urls = [el.get('src') for el in elements_with_src if el.get('src')]
            
            # Handle relative URLs
            parsed_url = urlparse(current_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            url_results = []
            for src in src_urls:
                if src.startswith('//'):
                    url_results.append(f"{parsed_url.scheme}:{src}")
                elif src.startswith('/'):
                    url_results.append(f"{base_url}{src}")
                elif not src.startswith(('http://', 'https://')):
                    url_results.append(f"{current_url}/{src.lstrip('/')}")
                else:
                    url_results.append(src)
            
            return url_results
            
        except requests.exceptions.RequestException as e:
            print(f"An error occurred extracting src links: {e}")
            return []
    
    # Process main URL
    main_urls = process_url(url)
    if main_urls:
        all_src_urls.extend(main_urls)
    
    # Process one level deep if depth is 1
    if depth == 1:
        links = get_all_links(url)
        for link in links[:10]:  # Limit to first 10 links to avoid too many requests
            # Handle relative URLs to create absolute URLs
            if link.startswith('/'):
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = base_url + link
            elif not link.startswith(('http://', 'https://')):
                link = url + '/' + link.lstrip('/')
                
            sub_urls = process_url(link)
            if sub_urls:
                all_src_urls.extend(sub_urls)
    
    # Remove duplicates
    return list(set(all_src_urls))
    

def find_audio_links(url, depth=1):
    """
    Find all audio file links on a page and optionally follow links to one level depth.
    
    Args:
        url: The URL to search for audio links
        depth: How deep to search (default is 1)
    
    Returns:
        A list of audio file links
    """
    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac']
    found_audio_links = []
    visited_urls = set()
    
    def extract_audio_from_page(page_url):
        if page_url in visited_urls:
            return []
        
        visited_urls.add(page_url)
        audio_links = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find audio-specific tags
            audio_tags = soup.find_all('audio')
            for tag in audio_tags:
                if tag.get('src'):
                    audio_links.append(tag.get('src'))
                
            # Find source tags within audio elements
            source_tags = soup.find_all('source')
            for tag in source_tags:
                if tag.get('src'):
                    audio_links.append(tag.get('src'))
            
            # Find links ending with audio extensions
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and any(href.lower().endswith(ext) for ext in audio_extensions):
                    audio_links.append(href)
            
            return audio_links
            
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {page_url}: {e}")
            return []
    
    # Get audio links from the main page
    main_page_audio = extract_audio_from_page(url)
    found_audio_links.extend(main_page_audio)
    
    # If depth is 1, follow all links and look for audio files
    if depth == 1:
        all_links = get_all_links(url)
        for link in all_links:
            # Handle relative URLs
            if link.startswith('/'):
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = base_url + link
            elif not link.startswith(('http://', 'https://')):
                link = url + '/' + link.lstrip('/')
                
            # Extract audio links from the page
            subpage_audio = extract_audio_from_page(link)
            found_audio_links.extend(subpage_audio)
    
    # Remove duplicates and return
    return list(set(found_audio_links))


import mp3helper

def get_last_hour_news():
    #https://archive.rthk.hk/mp3/radio/archive/cnca/cnca_hourly_news_2200/mp3/20250426.mp3

    # Get current time
    now = datetime.datetime.now()

    # Get current hour in 24-hour format (0-23)
    current_hour = now.hour
    if current_hour < 10:
        current_hour = f"0{current_hour}"
    else:
        current_hour = str(current_hour)

    # Determine if we're in the first or second half hour
    minute_suffix = "00" if now.minute < 30 else "30"

    # For debugging/testing
    print(f"Current hour: {current_hour}, Minute suffix: {minute_suffix}")

    base_url = f"https://archive.rthk.hk/mp3/radio/archive/cnca/cnca_hourly_news_{current_hour}{minute_suffix}/mp3/{now.strftime('%Y%m%d')}.mp3"
    
        # Download the audio file
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        print(f"Attempting to download news file from: {base_url}")
        
        # Make the request to download the file
        response = requests.get(base_url, headers=headers, stream=True)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Define the local filename to save to
        local_filename = f"hourly_news_{now.strftime('%Y%m%d')}_{current_hour}{minute_suffix}.mp3"
        
        # Save the downloaded file
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print(f"Successfully downloaded news file to {local_filename}")
        mp3helper.simple_process_mp3(local_filename)
        
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download news file: {str(e)}")
# return base_url

    
    
    None
    

import explaintext_in_simple_cantonese
# import explaintext_in_simple_cantonese    

import textprocessing

def get_rthk_tokenized_news():
    url = "https://news.rthk.hk/rthk/webpageCache/services/loadModNewsShowSp2List.php?lang=zh-TW&cat=4&newsCount=60&dayShiftMode=1&archive_date="

    links = get_all_links(url)
    return_news = []
    fullfilled = []
    random.shuffle(links)
    for i in links:      
        article = Article(i)
        article.download()
        article.parse()
        title = article.title
        text = article.text
        if len(text) > 0:
            fullfilled.append((title,text))
            return_news.append(textprocessing.split_text(text))
            if len(fullfilled) > 20:
                break
    return return_news

import mine_ai_dialog

import random
from urllib.parse import urlparse
import datetime

if __name__ == "__main__":
    
    
    url = "https://news.rthk.hk/rthk/webpageCache/services/loadModNewsShowSp2List.php?lang=zh-TW&cat=4&newsCount=60&dayShiftMode=1&archive_date="

    
    """
    
    get_last_hour_news()
    exit(0)
    # Define the URL you want to scrape
    
    audio_links = extract_src_links("https://news.rthk.hk/rthk/ch/news-bulletins.htm", depth=2)

    # Get all links from the webpage
    # Find and filter out all MP3 links from the extracted URLs
    mp3_links = [link for link in audio_links if 'mp3' in link.lower() or 'm4a' in link.lower()]
    
    """
    links = get_all_links(url)

    fullfilled = []
    random.shuffle(links)
    for i in links:      
        article = Article(i)
        article.download()
        article.parse()
        title = article.title
        text = article.text
        if len(text) > 0:
            fullfilled.append((title,text))
            if len(fullfilled) > 10:
                break
                    
    for i in fullfilled:
        title = i[0]
        text = i[1]
        try:
            #explaintext_in_simple_cantonese.explain_and_render_text(title+"。\n" + text)
            mine_ai_dialog.text_to_mp3_and_upload(title+"。\n" + text)
            print("Calling explain text " + title)
        except:
            print("Something went wrong but never mind that")