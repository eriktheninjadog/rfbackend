import requests
import json
import math
import os
import time
from pydub import AudioSegment
from typing import Optional, List, Tuple

class TranscriptionConfig:
    """Configuration class for transcription parameters"""
    def __init__(
        self,
        api_key: str,
        model: str = "whisper-large",
        language: str = "yue",
        chunk_length_ms: int = 300000,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "json"
    ):
        self.api_key = api_key
        self.model = model
        self.language = language
        self.chunk_length_ms = chunk_length_ms
        self.prompt = prompt
        self.temperature = temperature
        self.response_format = response_format

def seconds_to_srt_timestamp(seconds: float) -> str:
    """
    Converts seconds to SRT timestamp format.
    """
    milliseconds = int((seconds - int(seconds)) * 1000)
    timestamp = time.strftime('%H:%M:%S', time.gmtime(seconds))
    return f"{timestamp},{milliseconds:03d}"

def split_audio(audio_file_path: str, chunk_length_ms: int) -> List[Tuple[str, float]]:
    """
    Splits the audio file into chunks of specified length in milliseconds.

    Parameters:
    - audio_file_path (str): Path to the MP3 file to split
    - chunk_length_ms (int): Length of each chunk in milliseconds

    Returns:
    - List of tuples containing (chunk_file_path, start_time_in_seconds)
    """
    audio = AudioSegment.from_file(audio_file_path)
    total_length_ms = len(audio)
    chunk_files = []

    # Create a temporary directory for chunks if it doesn't exist
    temp_dir = "temp_audio_chunks"
    os.makedirs(temp_dir, exist_ok=True)

    for i, start_ms in enumerate(range(0, total_length_ms, chunk_length_ms)):
        end_ms = min(start_ms + chunk_length_ms, total_length_ms)
        chunk = audio[start_ms:end_ms]
        chunk_file = os.path.join(temp_dir, f"chunk_{i}.mp3")
        chunk.export(chunk_file, format="mp3")
        chunk_files.append((chunk_file, start_ms / 1000.0))

    return chunk_files

def transcribe_audio_segment(config: TranscriptionConfig, audio_file_path: str, segment_index: int = 0) -> Optional[List[dict]]:
    """
    Transcribe an audio segment using DeepInfra's Whisper model.

    Parameters:
    - config: TranscriptionConfig object containing API settings
    - audio_file_path: Path to the audio segment file
    - segment_index: Index of the current segment (used for prompt modification)

    Returns:
    - List of transcription segments or None if failed
    """
    url = "https://api.deepinfra.com/v1/inference/openai/whisper-1"
    
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "multipart/form-data"
    }

    # Modify prompt based on segment index
    current_prompt = config.prompt
    if current_prompt and segment_index > 0:
        current_prompt = f"Continuing transcription... {current_prompt}"

    with open(audio_file_path, 'rb') as audio_file:
        files = {
            'file': (audio_file_path, audio_file, 'audio/mpeg')
        }
        
        data = {
            'model': config.model,
            'language': config.language,
            'response_format': config.response_format,
            'temperature': config.temperature,
            'timestamps': True
        }

        if current_prompt:
            data['prompt'] = current_prompt

        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                segments = result.get('segments', [])
                
                if not segments:
                    print(f"No segments found in the response for chunk {segment_index}")
                    return None
                    
                return segments
            else:
                print(f"Error processing chunk {segment_index}: Status code {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Exception processing chunk {segment_index}: {str(e)}")
            return None

def transcribe_audio(audio_file_path: str, config: TranscriptionConfig) -> Optional[str]:
    """
    Main function to handle the complete transcription process.

    Parameters:
    - audio_file_path: Path to the audio file
    - config: TranscriptionConfig object containing all settings

    Returns:
    - SRT formatted string or None if failed
    """
    try:
        # Split the audio file into chunks
        chunk_files = split_audio(audio_file_path, config.chunk_length_ms)
        
        all_srt_segments = []
        caption_index = 1

        # Process each chunk
        for chunk_index, (chunk_file, chunk_start_time) in enumerate(chunk_files):
            print(f"Processing chunk {chunk_index + 1}/{len(chunk_files)}")
            
            segments = transcribe_audio_segment(config, chunk_file, chunk_index)
            
            if segments is None:
                print(f"Warning: Skipping chunk {chunk_index} due to transcription failure")
                continue

            # Process segments and adjust timestamps
            for segment in segments:
                start = segment.get('start', 0.0) + chunk_start_time
                end = segment.get('end', 0.0) + chunk_start_time
                text = segment.get('text', '').strip()

                if text:  # Only include non-empty segments
                    start_timestamp = seconds_to_srt_timestamp(start)
                    end_timestamp = seconds_to_srt_timestamp(end)
                    
                    srt_segment = f"{caption_index}\n{start_timestamp} --> {end_timestamp}\n{text}\n\n"
                    all_srt_segments.append(srt_segment)
                    caption_index += 1

            # Clean up chunk file
            os.remove(chunk_file)

        # Clean up temporary directory
        temp_dir = "temp_audio_chunks"
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

        # Combine all segments into final SRT content
        return ''.join(all_srt_segments)

    except Exception as e:
        print(f"Error in transcription process: {str(e)}")
        return None

def main():
    # Example configuration
    config = TranscriptionConfig(
        api_key="YOUR_DEEPINFRA_API_KEY",
        model="whisper-large",
        language="yue",
        prompt="""
        Please accurately transcribe this Cantonese audio.
        Use traditional Chinese characters.
        Maintain proper punctuation.
        Include speaker changes with [Speaker 1], [Speaker 2] notation if multiple speakers are present.
        """,
        temperature=0.0  # Lower temperature for more focused sampling
    )

    audio_file_path = "path/to/your/file.mp3"
    
    print("Starting transcription process...")
    srt_content = transcribe_audio(audio_file_path, config)

    if srt_content:
        # Save to file
        output_file = "transcription.srt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"Transcription completed and saved to {output_file}")
    else:
        print("Transcription failed")

if __name__ == "__main__":
    main()
