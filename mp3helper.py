#mp3helper.py

import os
from mutagen.mp3 import MP3

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