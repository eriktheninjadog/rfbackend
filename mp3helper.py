#mp3helper.py

import os
import boto3
from mutagen.mp3 import MP3
from pydub import AudioSegment

def extract_audio_segment(mp3_filename, start_timepoint, end_timepoint, outfilename):
    # Load the original MP3 file
    audio = AudioSegment.from_mp3(mp3_filename)
    
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


# Example usage:
if __name__ == "__main__":
    mp3_files = [
        "/path/to/song1.mp3",
        "/path/to/song2.mp3",
        "/path/to/song3.mp3"
    ]

    total_seconds = get_total_mp3_duration(mp3_files)
    formatted_time = format_duration(total_seconds)

    print(f"Total duration: {formatted_time}")
    print(f"Total seconds: {total_seconds:.2f}")