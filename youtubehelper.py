from googleapiclient.discovery import build

def get_youtube_video_details(api_key, video_id):
    # Build the YouTube API service
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the videos.list method to retrieve video details
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        # Get video details
        video_details = response['items'][0]
        return video_details
    else:
        return None
    
    
def check_video_has_subtitles(api_key, video_id):
    # Build the YouTube API service
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the captions.list method to see if captions exist
    request = youtube.captions().list(
        part='snippet',
        videoId=video_id
    )
    response = request.execute()

    # Check for caption tracks
    if 'items' in response and len(response['items']) > 0:
        subtitle_tracks = response['items']
        return True, subtitle_tracks
    else:
        return False, None


import re
def parse_srt(srt_file_path):
    
    def convert_time(time_string):
        """Convert SRT time format to VTT time format."""
        # Replace comma with dot for milliseconds
        return time_string.replace(',', '.')
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.read()

        # Use regex to find and process each subtitle block
        subtitle_blocks = re.findall(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:(?!\n\n).|\n)*)', srt_content, re.DOTALL)
        ret = []
        for block in subtitle_blocks:
            # Convert time format
            start_time = convert_time(block[1])
            end_time = convert_time(block[2])
            # Add the converted block to VTT content
            ret.append({'start_time':start_time,'end_time':end_time,'text':block[3]})
        return ret
    except FileNotFoundError:
        print(f"Error: The file {srt_file_path} was not found.")
        # Write the VTT content to file
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
from typing import List, Tuple, Optional

    
class VTTParser:
    
    TIME_PATTERN = re.compile(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})')
    
    def __init__(self, vtt_content: str):
        self.vtt_content = vtt_content
    
    def parse(self) -> List[Tuple[str, str, List[str]]]:
        """
        Parse the VTT content.
        
        Returns:
            A list of tuples, each containing start time, end time, and list of text lines.
        """
        lines = self.vtt_content.splitlines()
        cues = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("WEBVTT") or not line or line.startswith('NOTE'):
                # Skip header, empty lines, or notes
                i += 1
                continue
            
            # Detect time line
            if '-->' in line:
                start_time, end_time = self._parse_time_line(line)
                i += 1
                
                # Collect all text lines for the current cue
                text_lines = []
                while i < len(lines) and lines[i].strip() != '':
                    text_lines.append(lines[i].strip())
                    i += 1
                
                cues.append((start_time, end_time, text_lines))
            
            i += 1
        
        return cues
    
    def _parse_time_line(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse the VTT time format.

        Returns:
            A tuple with (start_time, end_time)
        """
        times = line.split(' --> ')
        if len(times) != 2:
            return None, None
        start_time, end_time = times[0].strip(), times[1].strip()
        return start_time, end_time
    

import yt_dlp

def download_youtube_subtitles(video_url, language='en', output_filename='subtitles.srt'):
    # Extract the base name without the extension to construct the full filename later
    base_output_filename = output_filename.rsplit('.', 1)[0]

    ydl_opts = {
        'writesubtitles': True,                # Write subtitles to a file
        'subtitleslangs': [language],          # Specify the language of the subtitles
        'skip_download': True,                 # Do not download the video itself
        'subtitlesformat': 'srt',              # Download the subtitles in 'srt' format
        'outtmpl': f'{base_output_filename}.%(ext)s',  # Template for the output files
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Downloading and extracting subtitle
            ydl.download([video_url])
            print(f"Subtitles downloaded successfully as {output_filename}")
        except Exception as e:
            print(f"An error occurred: {e}")




import voa
import textprocessing
import random
import json
import os
import subprocess

def rename_file(current_name, new_name):
    try:
        # Use os.rename() to rename the file
        os.rename(current_name, new_name)
        print(f"File renamed from {current_name} to {new_name}")
    except FileNotFoundError:
        print(f"The file {current_name} does not exist.")
    except PermissionError:
        print(f"Permission denied: Unable to rename {current_name}.")
    except Exception as e:
        print(f"An error occurred: {e}")



def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return None
    except json.JSONDecodeError:
        print(f"The file {file_path} is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
    
def download_video_from_ids(api_key, video_ids, target_languages):    
    # Build the YouTube API service
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos_with_subtitles = []
    for video_id in video_ids:        
        try:
            # Check if the video has captions in the target language    
            ydl = yt_dlp.YoutubeDL({'quiet': True})
            result = ydl.extract_info('https://www.youtube.com/watch?v='+video_id, download=False)
            subtitles = result.get('subtitles', {})
            print(str(subtitles.keys()))
            if any(lang in subtitles for lang in target_languages):
                    lang = [lang for lang in target_languages if lang in subtitles][0]
                    videos_with_subtitles.append({
                        'videoId': video_id,
                        'title': video_id,
                        'language': lang
                    })
                    
                    # we need to download the video
                    voa.download_youtube_audio_as_mp3("https://www.youtube.com/watch?v="+video_id,"tmp.mp3")
                    download_youtube_subtitles("https://www.youtube.com/watch?v="+video_id,language=lang,output_filename="tmp.srt")
                    
                    f = open("tmp."+lang+".vtt","r",encoding="utf-8")
                    vtttext = f.read()
                    f.close()
                    
                    vtp = VTTParser(vtttext)
                    popa = vtp.parse()
                    
                    txt = ''
                    for i in popa:
                        txt += "".join( i[2])
                        txt += '\n'
                    jsonpart = textprocessing.split_text(txt)
                    jsonpart.append("<a href=\"" +  "https://www.youtube.com/watch?v="+video_id+"\">>video</a>")
                    filenamestart = "spokenarticle_news_u2" + str(random.randint(0,1000)) + ".mp3"
                    f = open(filenamestart+".hint.json","w")
                    f.write(json.dumps(jsonpart))
                    f.close()
                    rename_file("tmp.mp3",filenamestart)
                    scp_command = f"scp {filenamestart}* chinese.eriktamm.com:/var/www/html/mp3/"
                    print(scp_command)
                    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
                    # need to change the srt file to txt file
                    # Stop checking after finding a target language caption
        except:
            print("error")    
    return videos_with_subtitles


    
def search_videos_with_subtitles(api_key, query, target_languages):
    # Build the YouTube API service
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Search for videos
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        publishedAfter="2024-12-30T00:00:00Z",  # Adjust the date as needed
        maxResults=100,  # Adjust as needed,
        videoDuration='medium'
    ).execute()
    
    # List to store videos with target language subtitles
    videos_with_subtitles = []

    # Iterate over found videos
    for item in search_response['items']:
        video_id = item['id']['videoId']
        
        # Check if the video has captions in the target language
        captions_response = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
        
        for caption in captions_response.get('items', []):
            if caption['snippet']['language'] in target_languages:
                videos_with_subtitles.append({
                    'videoId': video_id,
                    'title': item['snippet']['title'],
                    'language': caption['snippet']['language']
                })
                
                # we need to download the video
                thelanguage = caption['snippet']['language']
                
                downloadanduploadvideo(video_id, thelanguage)

                # need to change the srt file to txt file
                # Stop checking after finding a target language caption
    
    return videos_with_subtitles

def downloadanduploadvideo(video_id, thelanguage):
    voa.download_youtube_audio_as_mp3("https://www.youtube.com/watch?v="+video_id,"tmp.mp3")
    download_youtube_subtitles("https://www.youtube.com/watch?v="+video_id,language=thelanguage,output_filename="tmp.srt")
                
    f = open("tmp."+thelanguage+".vtt","r",encoding="utf-8")
    vtttext = f.read()
    f.close()
                
    vtp = VTTParser(vtttext)
    popa = vtp.parse()
                
    txt = ''
    for i in popa:
        txt += "".join( i[2])
        txt += '\n'
    jsonpart = textprocessing.split_text(txt)
    jsonpart.append("<a href =\"https://www.youtube.com/watch?v="+video_id+"\">video</a>")
    filenamestart = "spokenarticle_news_u2" + str(random.randint(0,1000)) + ".mp3"
    f = open(filenamestart+".hint.json","w")
    f.write(json.dumps(jsonpart))
    f.close()
    rename_file("tmp.mp3",filenamestart)
    scp_command = f"scp {filenamestart}* chinese.eriktamm.com:/var/www/html/mp3"
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)

import expandmp3file

def generate_random_filename():
    """Generate a random 12-character filename with .mp3 extension."""
    # Define possible characters for the filename
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    # Generate a random string of 12 characters
    random_string = ''.join(random.choice(characters) for _ in range(12))
    
    # Return the filename with .mp3 extension
    return f"{random_string}.mp3"

import mp3helper

def download_explain_uploadvideo(video_id):
    newfilename=generate_random_filename()
    base_name = newfilename.split('.')[0]
    voa.download_youtube_audio_as_mp3("https://www.youtube.com/watch?v="+video_id,newfilename,save_video=True)
    simple_process_mp3  = "tmp.mp3"
    #expandmp3file.process_mp3_file("tmp.mp3","youtube_"+video_id)
    #mp3helper.simple_process_mp3(newfilename)
    
    scp_command = f"scp {base_name}.webm chinese.eriktamm.com:/opt/watchit"
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
    scp_command = f"scp {base_name}.srt chinese.eriktamm.com:/opt/watchit"
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
    scp_command = f"scp {base_name}.mp3 chinese.eriktamm.com:/opt/mp3_to_process"
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
    scp_command = f"scp {base_name}.mp3 chinese.eriktamm.com:/var/www/html/mp3"    
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
    

import youtubesearcher
import sys
if __name__ == "__main__":
    # Example usage
    #machine
    
    #for i in ['oh2Z6Y-scxs','aQjAQntp2Fg','Vy7c3FYVA2k','IpsxMftMUq4','OVfUclnPheI','oa9MkmSIkJk','zLj7iSc2Xgg']:
    #    download_explain_uploadvideo(i)
    
    your_api_key = 'AIzaSyDTczpLLlzdHN4We1mzu5x2mKkuJqadID0'
    for i in ['-BSroezFd9A','Bb5o5CTsC0Y','He9zVyz_u9s','iSYuwq1jUSY','WrX1lRE_Q1c']:
        download_explain_uploadvideo(i)
    exit(-1)
    
    """
    https://www.youtube.com/watch?v=
    https://www.youtube.com/watch?v=
    https://www.youtube.com/watch?v=
    https://www.youtube.com/watch?v=
    https://www.youtube.com/watch?v=
    
    if (len(sys.argv)> 1):
        videoid =  sys.argv[1]   
        download_explain_uploadvideo(videoid)
        exit(0)
    """
    channels = ["檔案","內地傳媒","報道","指出","核心變化"]
    download_video_from_ids(your_api_key,youtubesearcher.get_sloppy_match_list(),["yue-HK","zh-HK","zh-Hant","zh-TW"])
    
    searchterm = random.choice(channels)
    results = search_videos_with_subtitles(your_api_key,searchterm,["yue-HK","zh-HK","zh-Hant","zh-TW"])
    for i in results:
        print(str(i))
    exit(0)
    
    video_id = 'JU-qeTkNk8A'
    video_details = get_youtube_video_details(your_api_key, video_id)
    video_subtitles = check_video_has_subtitles(your_api_key, video_id)
    if video_details:
        print("Title:", video_details['snippet']['title'])
        print("Description:", video_details['snippet']['description'])
    else:
        print("No video details found.")

    if video_subtitles:
        print(str(video_subtitles))
        print("Title:", video_details['snippet']['title'])
        print("Description:", video_details['snippet']['description'])
    else:
        print("No video details found.")





