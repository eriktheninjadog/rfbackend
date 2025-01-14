import time
import random
import re
import math
import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydub import AudioSegment
import expandmp3file



def get_links_with_a(url, max_retries=3, delay=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    session = requests.Session()
    
    for attempt in range(max_retries):
        try:
            # Add random delay to avoid too many requests
            time.sleep(delay + random.random())
            
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            a_links = []
            for link in links:
                href = link['href']
                # Check if the URL contains '/a/' but not '-'
                if '/a/' in href and '-' not in href:
                    # Make absolute URLs if they're relative
                    absolute_url = urljoin(url, href)
                    a_links.append(absolute_url)
            
            # Remove duplicates while preserving order
            a_links = list(dict.fromkeys(a_links))
            
            return a_links

        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Giving up.")
                return []
            time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            

def download_mp3s(url, base_filename):
    """
    Download all MP3 files found on a web page.
    
    Args:
        url (str): The URL of the web page to search
        base_filename (str): Base name for saving the files
    
    Returns:
        list: List of downloaded file names
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
    }
    
    downloaded_files = []
    
    try:
        # Get the webpage content
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links and source tags that might contain MP3 files
        potential_mp3s = []
        
        # Look for direct links to MP3 files
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.lower().endswith('.mp3'):
                potential_mp3s.append(href)
                
        # Look for audio source tags
        audio_sources = soup.find_all('source', src=True)
        for source in audio_sources:
            src = source['src']
            if src.lower().endswith('.mp3'):
                potential_mp3s.append(src)
                
        # Look for audio tags
        audio_tags = soup.find_all('audio', src=True)
        for audio in audio_tags:
            src = audio['src']
            if src.lower().endswith('.mp3'):
                potential_mp3s.append(src)
                
        # Additional search for MP3 links in scripts or other tags
        scripts = str(soup)
        mp3_urls = re.findall(r'https?://[^\s<>"]+?\.mp3', scripts)
        potential_mp3s.extend(mp3_urls)
        
        # Remove duplicates while preserving order
        potential_mp3s = list(dict.fromkeys(potential_mp3s))
        
        # Download each MP3 file
        for index, mp3_url in enumerate(potential_mp3s, 1):
            try:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(url, mp3_url)
                
                # Create filename
                if len(potential_mp3s) > 1:
                    # Add number prefix if multiple files
                    filename = f"{base_filename}_{index}.mp3"
                else:
                    filename = f"{base_filename}.mp3"
                
                print(f"Downloading: {absolute_url} -> {filename}")
                
                # Download the file with streaming
                with requests.get(absolute_url, headers=headers, stream=True) as r:
                    r.raise_for_status()
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                downloaded_files.append(filename)
                print(f"Successfully downloaded: {filename}")
                
            except Exception as e:
                print(f"Error downloading {mp3_url}: {e}")
                continue
    
    except Exception as e:
        print(f"Error processing webpage: {e}")
    
    return downloaded_files



def downloadfirstpagenews():
    url = 'https://www.voacantonese.com/z/4065'
    
    print("Fetching links...")
    links = get_links_with_a(url)
    
    if links:
        print(f"\nFound {len(links)} unique links containing '/a/' but not '-':")
        for i, link in enumerate(links, 1):
            print(f"{i}. {link}")
    else:
        print("No links found or an error occurred.")

    # Optionally, save the links to a file
    if links:
        with open('filtered_links.txt', 'w', encoding='utf-8') as f:
            for link in links:
                f.write(link + '\n')
        print("\nLinks have been saved to 'filtered_links.txt'")
    
    files = download_mp3s(links[0],"voanews")
    return files




def split_mp3(input_file, segment_length_minutes=10):
    """
    Split an MP3 file into segments of specified length.
    
    Args:
        input_file (str): Path to the input MP3 file
        segment_length_minutes (int): Length of each segment in minutes (default: 10)
    
    Returns:
        list: List of created segment filenames
    """
    try:
        # Load the MP3 file
        print(f"Loading {input_file}...")
        audio = AudioSegment.from_mp3(input_file)
        
        # Calculate segment length in milliseconds
        segment_length_ms = segment_length_minutes * 60 * 1000
        total_length_ms = len(audio)
        
        # Calculate number of segments
        num_segments = math.ceil(total_length_ms / segment_length_ms)
        
        # Create output filenames
        base_name = os.path.splitext(input_file)[0]
        output_files = []
        
        print(f"Splitting into {num_segments} segments...")
        
        # Split the audio file
        for i in range(num_segments):
            # Calculate start and end times for this segment
            start_time = i * segment_length_ms
            end_time = min((i + 1) * segment_length_ms, total_length_ms)
            
            # Extract segment
            segment = audio[start_time:end_time]
            
            # Generate output filename
            output_filename = f"{base_name}_part{i+1:03d}.mp3"
            
            # Export segment
            print(f"Exporting {output_filename}...")
            segment.export(output_filename, format="mp3")
            
            output_files.append(output_filename)
        
        print("Splitting complete!")
        return output_files
    
    except Exception as e:
        print(f"Error splitting MP3: {str(e)}")
        return []

def get_duration_str(ms):
    """Convert milliseconds to human-readable duration string."""
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    
    if hours > 0:
        return f"{hours}:{minutes%60:02d}:{seconds%60:02d}"
    else:
        return f"{minutes}:{seconds%60:02d}"

def split_mp3_with_info(input_file, segment_length_minutes=10):
    """
    Enhanced version of split_mp3 with additional information and checks.
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        # Load the MP3 file
        print(f"Loading {input_file}...")
        audio = AudioSegment.from_mp3(input_file)
        
        # Get audio information
        duration_ms = len(audio)
        duration_str = get_duration_str(duration_ms)
        print(f"Audio duration: {duration_str}")
        
        # Calculate segment length in milliseconds
        segment_length_ms = segment_length_minutes * 60 * 1000
        num_segments = math.ceil(duration_ms / segment_length_ms)
        
        print(f"Splitting into {num_segments} segments of {segment_length_minutes} minutes each...")
        
        # Create output directory if needed
        base_name = os.path.splitext(input_file)[0]
        output_dir = f"{base_name}_segments"
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = []
        
        # Split the audio file
        for i in range(num_segments):
            start_time = i * segment_length_ms
            end_time = min((i + 1) * segment_length_ms, duration_ms)
            
            # Extract segment
            segment = audio[start_time:end_time]
            
            # Generate output filename
            output_filename = os.path.join(output_dir, f"{os.path.basename(base_name)}_part{i+1:03d}.mp3")
            
            # Show progress
            segment_duration = get_duration_str(len(segment))
            print(f"Exporting part {i+1}/{num_segments} ({segment_duration})...")
            
            # Export segment with metadata
            segment.export(
                output_filename,
                format="mp3",
                tags={
                    'title': f"Part {i+1} of {num_segments}",
                    'artist': 'Split by Python',
                    'album': os.path.basename(base_name)
                }
            )
            
            output_files.append(output_filename)
        
        print(f"\nSplitting complete! Files saved in: {output_dir}")
        return output_files
    
    except Exception as e:
        print(f"Error splitting MP3: {str(e)}")
        return []


import datetime
from datetime import datetime

def get_sbs_cantonese():
    
    filename = "sbs_cantonese.mp3"
    url = "https://fos.prod.edsprd01.aws.sbs.com.au/v2/web/radio-catchup?pathOrId=/language/chinese/zh-hant/radio-program/cantonese/4sdft857g&page=1&limit=12"
    response = requests.get(url, timeout=10)
    jsona = response.json()
    data = jsona['data']
    mp3url = data[0]['audio']['url']
    with requests.get(mp3url , stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    files = split_mp3_with_info(filename, segment_length_minutes=15)
    expandmp3file.process_mp3_file(files[0],filename_addon="sbs"+datetime.now().strftime("%Y%m%d")
)        
    
import streamlink

import ffmpeg


def get_rhk_news():
    datepart = datetime.now().strftime("%Y%m%d")
    streams = streamlink.streams("https://rthkaod2022.akamaized.net/m4a/radio/archive/radio1/newspaper/m4a/"+datepart+".m4a/master.m3u8")
    stream = streams['best']
    with stream.open() as out:
        with open('output.mp4', 'wb') as out_file:
            while True:
                data = out.read(1024)
                if not data:
                    break
                out_file.write(data)
    ffmpeg.input('output.mp4').output("output.mp3", format='mp3', acodec='libmp3lame').run()
    expandmp3file.process_mp3_file("output.mp3",filename_addon="rthk"+datetime.now().strftime("%Y%m%d"))




import yt_dlp

def get_latest_video_url(channel_url):
    ydl_opts = {
        'quiet': True,  # Suppress output
        'extract_flat': 'first',  # Extract only metadata, do not download
        'skip_download': True  # Do not download the video
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            
            # Check if the result contains the 'entries'
            if 'entries' in result:
                # Get the first video entry
                latest_video = result['entries'][0]
                latest_video_url = f"https://www.youtube.com/watch?v={latest_video['id']}"
                return latest_video_url
            else:
                return "No videos found."

    except yt_dlp.DownloadError as e:
        return f"An error occurred: {e}"


def progress_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', None), info.get('id', None)


def download_youtube_audio_as_mp3(youtube_url, output_file='output.mp3'):
    output_path = '/tmp'
    title, video_id = get_video_info(youtube_url)
    try:
        ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path + '/%(id)s.%(ext)s',
                'progress_hooks': [progress_hook],
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        print(f"Download completed successfully: {title}")
        mp3_file_path = os.path.join(output_path, f"{video_id}.mp3")
        os.rename(mp3_file_path, output_file)

    except Exception as e:
        print(f'An error occurred: {e}')

def make_mp3_file_from_youtube(youtube_url,extra_filename_addon="youtube"):
    download_youtube_audio_as_mp3(youtube_url)
    expandmp3file.process_mp3_file("output.mp3",filename_addon=extra_filename_addon+datetime.now().strftime("%Y%m%d"))


def get_lastest_robot():
    make_mp3_file_from_youtube("https://www.youtube.com/watch?v=dtx2PaQgL5E",extra_filename_addon="dasrobot")


import youtubesearcher



def main():
    u = youtubesearcher.YouTubeSearcher()
    results = u.search("鄺俊宇")
    print(results)
    return None
    get_lastest_robot()
    return None
    get_rhk_news()
    #get_sbs_cantonese()
    return None
    files = downloadfirstpagenews()
    parts = split_mp3(files[0])
    print(str(parts))
    for p in parts:
        expandmp3file.process_mp3_file(p,filename_addon="voa")

if __name__ == "__main__":
    main()
