#mp3helper.py

import os
import boto3
from mutagen.mp3 import MP3
from pydub import AudioSegment
import requests
import json
import time

def extract_audio_segment(filename, start_timepoint, end_timepoint, outfilename):
    # Load the original MP3 file
    audio = AudioSegment.from_mp3(filename)
    
    # Convert start and end timepoints from seconds to milliseconds
    start_time_ms = start_timepoint * 1000
    end_time_ms = end_timepoint * 1000
    
    # Extract the segment
    audio_segment = audio[start_time_ms:end_time_ms]
    
    # Export the segment to a new MP3 file
    audio_segment.export(outfilename, format="mp3")
    
    print(f"Segment extracted and saved to {outfilename}")

# Example usage:
# extract_audio_segment("input.mp3", 10, 20, "output.mp3")

def get_total_mp3_duration(mp3_files):
    """
    Calculate the total duration of a list of MP3 files.

    Args:
    mp3_files (list): A list of paths to MP3 files.

    Returns:
    float: The total duration in seconds.
    """
    total_duration = 0

    for file_path in mp3_files:
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue
        
        try:
            # Load the MP3 file
            audio = MP3(file_path)
            
            # Add the duration to the total
            total_duration += audio.info.length
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

    return total_duration

# Helper function to format seconds to HH:MM:SS
def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    
def create_srt_from_mp3(mp3_path, output_srt_path, api_key, chunk_size_seconds=60, overlap_seconds=2):
    """
    Create a subtitle (SRT) file from an MP3 file using DeepInfra API.
    The function splits the audio into manageable chunks if necessary.
    
    Args:
        mp3_path: Path to the MP3 file
        output_srt_path: Path to save the output SRT file
        api_key: DeepInfra API key
        chunk_size_seconds: Size of each chunk in seconds
        overlap_seconds: Overlap between chunks in seconds to ensure continuity
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(mp3_path):
        print(f"Error: File not found - {mp3_path}")
        return False
    
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        total_duration = len(audio) / 1000  # Convert to seconds
        
        # Process in chunks if longer than chunk_size_seconds
        if total_duration > chunk_size_seconds:
            all_segments = []
            chunk_count = 0
            
            # Split audio into chunks with overlap
            for start_time in range(0, int(total_duration), chunk_size_seconds - overlap_seconds):
                chunk_count += 1
                end_time = min(start_time + chunk_size_seconds, total_duration)
                
                # Create temporary chunk file
                temp_chunk_path = f"temp_chunk_{chunk_count}.mp3"
                chunk = audio[start_time * 1000:end_time * 1000]
                chunk.export(temp_chunk_path, format="mp3")
                
                print(f"Processing chunk {chunk_count}: {start_time}s to {end_time}s")
                
                # Process this chunk
                chunk_segments = transcribe_audio(temp_chunk_path, api_key, start_time)
                if chunk_segments:
                    all_segments.extend(chunk_segments)
                
                # Clean up temp file
                os.remove(temp_chunk_path)
        else:
            # Process the whole file at once
            all_segments = transcribe_audio(mp3_path, api_key)
        
        # Write the SRT file
        if all_segments:
            write_srt_file(all_segments, output_srt_path)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing MP3 file: {str(e)}")
        return False

def transcribe_audio(audio_path, api_key, time_offset=0):
    """
    Transcribe audio using DeepInfra API.
    
    Args:
        audio_path: Path to the audio file
        api_key: DeepInfra API key
        time_offset: Time offset in seconds for this chunk
    
    Returns:
        list: Transcript segments with timing information
    """
    url = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": audio_file}
            response = requests.post(url, headers=headers, files=files)
            
        if response.status_code == 200:
            result = response.json()
            
            # Adjust timestamps with the offset
            segments = result.get("segments", [])
            for segment in segments:
                segment["start"] += time_offset
                segment["end"] += time_offset
                
            return segments
        else:
            print(f"API request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during API call: {str(e)}")
        return None

def write_srt_file(segments, output_path):
    """
    Write segments to an SRT file.
    
    Args:
        segments: List of transcript segments
        output_path: Path to save the SRT file
    """
    with open(output_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")
    
    print(f"SRT file created successfully: {output_path}")

def format_timestamp(seconds):
    """
    Format seconds to SRT timestamp format (HH:MM:SS,mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remain = seconds % 60
    milliseconds = int((seconds_remain - int(seconds_remain)) * 1000)    
    return f"{hours:02d}:{minutes:02d}:{int(seconds_remain):02d},{milliseconds:03d}"


def extract_text_from_srt(srt_file_path):
    """
    Extract all text from a subtitle (SRT) file and return it as a single string.
    
    Args:
        srt_file_path: Path to the SRT file
    
    Returns:
        str: Concatenated text from all subtitle entries
    """
    if not os.path.exists(srt_file_path):
        print(f"Error: SRT file not found - {srt_file_path}")
        return ""
    
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split the content by double newlines (which separate subtitle entries)
        subtitle_blocks = content.strip().split('\n\n')
        
        extracted_text = []
        for block in subtitle_blocks:
            lines = block.split('\n')
            # Skip the first line (subtitle number) and the second line (timestamp)
            if len(lines) > 2:
                # Join all remaining lines (the actual text)
                text = ' '.join(lines[2:])
                extracted_text.append(text)
        
        return ' '.join(extracted_text)
    
    except Exception as e:
        print(f"Error extracting text from SRT file: {str(e)}")
        return ""


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

import textprocessing
import subprocess
    # Get the DeepInfra API key from environment variable
def simple_process_mp3(filepath):
    deepapi = os.environ.get('DEEP', '')    
    create_srt_from_mp3(filepath,filepath+".srt",deepapi)
    naked_text = extract_text_from_srt(filepath+".srt")
    split_naked_text = textprocessing.split_text(naked_text)
    hint_filename = f"{filepath}.hint.json"
    with open(hint_filename, "w") as f:
        json.dump(split_naked_text, f)
    print(f"Hint file created: {hint_filename}")
    scp_command = f"scp {filepath}* chinese.eriktamm.com:/var/www/html/mp3"
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
    return None


# Example usage:
if __name__ == "__main__":
    simple_process_mp3("/home/erik/Downloads/viu_recruitment_2.mp3")



