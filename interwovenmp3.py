#interwovenmp3.py
import requests
import json

import boto3

from pydub import AudioSegment


import openrouter




#this will try to fix the chinese problem of always 
#stacking , on top of each other

def split_string_on_char(s, min_length, max_length, special_char):
    """
    Splits a long string into substrings of a specified minimum and maximum length,
    ensuring splits occur on a special character.

    Args:
        s (str): The string to be split.
        min_length (int): The minimum length of each substring.
        max_length (int): The maximum length of each substring.
        special_char (str): The character on which to split the string.

    Returns:
        list: A list of substrings, each between min_length and max_length.
    """
    # Split the string by the special character
    parts = s.split(special_char)
    result = []
    current_segment = ""

    for part in parts:
        # If adding the part exceeds the max length, we need to split the current segment
        if len(current_segment) + len(part) + (1 if current_segment else 0) > max_length:
            if len(current_segment) >= min_length:
                result.append(current_segment)  # Append current segment if it meets min length
            current_segment = part  # Start a new segment
        else:
            if current_segment:  # Add special character if not the first segment
                current_segment += special_char
            current_segment += part

    # Append any remaining segment if it meets the minimum length
    if len(current_segment) >= min_length:
        result.append(current_segment)

    return result

# Example usage:
# long_string = "apple;banana;cherry;date;elderberry;fig;grape;kiwi"
# min_len = 15
# max_len = 25
# special_char = ";"
# print(split_string_on_char(long_string, min_len, max_len, special_char))


def shorten_sentences(chinese):
    txt = openrouter.open_router_chatgpt_4o_mini("You are a Cantonese assistant editor whose job is to shorten sentences by by replacing ， with 。","Try to shorten the sentences in this text by replacing ， with 。 were possible without changing the meaning. Do not do any other changes to the text. Reply with the text only, do not add any extra text (no comments, explanations) . The returned text must be the same length as the input text. Here is the text:\n" + chinese)
    #txt = openrouter.do_open_opus_questions("Try to shorten the sentences in this text by replacing \"，\" with \'。\' were possible without changing the meaning. Do not do any other changes to the text. Reply with the text only, do not add any extra text (no comments, explanations) . Here is the text:\n" + chinese)
    return txt

def find_differences(str1, str2):
    """
    Returns a list of positions where two equal-length strings differ.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        list: A list of positions (indices) where the strings differ.
    
    Raises:
        ValueError: If the strings are not of equal length.
    """
    if len(str1) != len(str2):
        raise ValueError("Strings must be of equal length.")

    differences = []
    
    for index in range(len(str1)):
        if str1[index] != str2[index]:
            differences.append(index)

    return differences

def concatenate_mp3(filenames, output_file):
    """
    Concatenates multiple MP3 files into a single MP3 file.

    Args:
        filenames (list): List of MP3 filenames to concatenate.
        output_file (str): Path to the output MP3 file.
    """
    combined = AudioSegment.empty()  # Create an empty AudioSegment

    for filename in filenames:
        try:
            audio = AudioSegment.from_mp3(filename)
            combined += audio  # Concatenate the audio segments
        except Exception as e:
            print(f"An error occurred while processing {filename}: {e}")

    # Export the combined audio to a single MP3 file
    combined.export(output_file, format="mp3")
    print(f"Combined MP3 file created successfully: {output_file}")


def text_to_mp3(text, output_file):
    """
    Converts a string of English text to an MP3 file using AWS Polly.

    Args:
        text (str): The text to convert to speech.
        output_file (str): Path to the output MP3 file.
    """
    # Initialize a session using your AWS credentials
    session = boto3.Session(region_name='us-east-1')
    
    polly_client = session.client('polly')

    try:
        # Call Amazon Polly to synthesize speech
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'  # You can change the voice as needed
        )

        # Save the audio stream to an MP3 file
        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"MP3 file created successfully: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")



def translate_chinese_to_english(chinese):
    #return openrouter.open_router_qwen("You are a Cantonese translator.","Translate the following sentence from Cantonese to English. Stay as close to English as possible. Only return the english translation. There is the sentence:\n" + chinese)
    return openrouter.do_open_opus_questions("Translate the following sentence from Cantonese to English. Stay as close to English as possible. Only return the english translation. There is the sentence:\n" + chinese)


def download_mp3(url, filename):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses

        # Open a file in binary write mode
        with open(filename, 'wb') as file:
            # Write the content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {url}. Error: {e}")


def download_and_parse_json(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON content
        data = response.json()  # Automatically parses JSON response
        
        return data  # Return the parsed JSON data
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError:
        print("Failed to parse JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

def split_file(times,mintime):
    ret_times = []
    current_time = 0
    last_point = 0
    text = ''
    for i in times:
        start_time = i['start_time']
        end_time = i['end_time']
        current_time = end_time - last_point
        text = text + i['word']
        if current_time > mintime:
            if i['word'] == '？' or i['word'] == '。' or i['word'] == '！' :
                ret_times.append([text,last_point])
                last_point = end_time
                text = ''
    return ret_times
    
def split_mp3(file_path, timepoints):
    audio = AudioSegment.from_mp3(file_path)
    segments = []

    # Add start point (0ms) to the timepoints list
    #timepoints = [["",0]] + timepoints

    # Iterate over timepoints to create segments
    for i in range(len(timepoints) - 1):
        start_time = timepoints[i][1] *1000
        end_time = timepoints[i + 1][1] *1000
        segment = audio[start_time:end_time]
        segments.append(segment)
        part_file_name = file_path+"_"+str(i) + ".mp3"
        timepoints[i].append(part_file_name)     
        segment.export(part_file_name,format="mp3")
    return timepoints

def get_english_translations(data_file):
    for i in data_file:
        if len(i) == 2:
            break
        
        chinese = i[0]
        english = translate_chinese_to_english(chinese)
        #english = "This is just a sample English."
        filename = i[2] + ".eng.mp3"        
        text_to_mp3(english,filename)        
        i.append(english)
        i.append(filename)
    return data_file

def make_the_big_file(data,id):
    files = []
    for i in data:
        if len(i) < 4:
            break
        files.append(i[2])
        files.append(i[4])
    concatenate_mp3(files,id + ".big.mp3" )

import os

def rename_file(old_name, new_name):
    """
    Renames a file from old_name to new_name.

    Args:
        old_name (str): The current name of the file.
        new_name (str): The new name for the file.
    """
    try:
        os.rename(old_name, new_name)
        print(f"File renamed from '{old_name}' to '{new_name}'")
    except FileNotFoundError:
        print(f"Error: The file '{old_name}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied while renaming '{old_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

import subprocess

def split_string_by_lengths(s, lengths):
    """
    Splits a string into segments based on the specified lengths.

    Args:
        s (str): The string to be split.
        lengths (list): A list of lengths for each segment.

    Returns:
        list: A list of string segments.
    """
    segments = []
    start = 0

    for length in lengths:
        # Slice the string from the current start position
        segment = s[start:start + length]
        segments.append(segment)
        start += length        
        # If the end of the string is reached, break
        if start >= len(s):
            break

    return segments



def preprocess_text(times):
    orgtext =''
    listoflengths = []
    for i in times:
        orgtext = orgtext + i['word']
        listoflengths.append(len(i['word']))
    newtext = shorten_sentences(orgtext)
    print( " Length newtext: " + str(len(newtext)) + " old " + str(len(orgtext)))

    newtokens = split_string_by_lengths(newtext,listoflengths)
    for i in range(len(times)):
        try:
            times[i]['word'] = newtokens[i]
        except:
            break
    return times


def download_mp3_subtitles(id:str):
    baseurl = "https://chinese.eriktamm.com/mp3"    
    mp3path = baseurl+"/"+id+".mp3"
    hintpath = mp3path + ".allhint.json"
    download_mp3(mp3path,id+".mp3")
    times = download_and_parse_json(hintpath)
    
    times = preprocess_text(times)
    
    
    tmpf = open( id+".big.mp3.allhint.json","w")
    tmpf.write(json.dumps(times))
    tmpf.close()
    tmpf = open( id+"big.mp3.hint.json","w")
    tmpf.write(json.dumps(times))
    tmpf.close()
    
    split_times = split_file(times,10)
    split_times = split_mp3(id+".mp3",split_times)
    split_times = get_english_translations(split_times)
    make_the_big_file(split_times,id)
    scpcommand = "scp *" + id + "*big* chinese.eriktamm.com:/var/www/html/mp3"   
    subprocess.run(scpcommand,shell=True,capture_output=True,text=True)
    return None

import sys
if __name__ == "__main__":
#    if len(sys.argv) > 2:
#        download_mp3_subtitles(sys.argv[1])
#    else:
    download_mp3_subtitles("spokenarticle_4825af32f7621e444a7a29d657966106")