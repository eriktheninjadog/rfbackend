#deepinfra.py
from openai import OpenAI
import os
import os.path
import json

#add caching to make it cheaper and faster when debugging!





def make_md5_from_file(file_path):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()




def call_deepinfra_gemini_flash_2_5(systemprompt, text):
    """
    Calls the DeepInfra Gemini Flash 2.5 model with the provided system prompt and text.
    Returns the response from the model.
    """
    apikey = os.getenv("DEEPINFRAKEY")
    client = OpenAI(
        api_key= apikey,
        base_url="https://api.deepinfra.com/v1/openai"
    )
    
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": systemprompt},
            {"role": "user", "content": text}
        ]
    )
    
    return response.choices[0].message.content

def combine_short_segments(segments, min_duration=2.0):
    """
    Combines segments that are shorter than the minimum duration into longer segments.
    
    Args:
        segments: List of transcription segments
        min_duration: Minimum duration in seconds for a segment
        
    Returns:
        List of combined segments
    """
    if not segments:
        return []
    
    combined = []
    current = segments[0].copy()
    
    for next_segment in segments[1:]:
        # Calculate current duration
        current_duration = current['end_time'] - current['start_time']
        
        # If current segment is too short and not the last one, combine with next
        if current_duration < min_duration:
            current['end_time'] = next_segment['end_time']
            current['text'] += " " + next_segment['text']
        else:
            # Current segment is long enough, add it to result
            combined.append(current)
            current = next_segment.copy()
    
    # Don't forget to add the last segment
    combined.append(current)
    
    return combined

def write_srt_from_audio(audio_file_path, output_srt_path=None):
    """
    Transcribes audio and writes the result to an SRT subtitle file.
    
    Args:
        audio_file_path: Path to the audio file to transcribe
        output_srt_path: Path where the SRT file should be written (defaults to audio filename with .srt extension)
    
    Returns:
        Path to the created SRT file
    """
    if output_srt_path is None:
        # Default to same name as audio file but with .srt extension
        output_srt_path = os.path.splitext(audio_file_path)[0] + ".srt"
    
    # Get transcription data
    segments = transcribe_audio(audio_file_path)
    #lets skip the combining for now, it is not needed
    #segments = combine_short_segments(segments, min_duration=4.0)
    
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, 1):
            # Format timestamp as HH:MM:SS,mmm
            start_time = format_timestamp(segment['start_time'])
            end_time = format_timestamp(segment['end_time'])
            
            # Write SRT entry
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{segment['text']}\n\n")
    
    return output_srt_path

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    # SRT uses comma as decimal separator
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{int((seconds % 1) * 1000):03d}"

def transcribe_audio(file_path):
    transpath = make_md5_from_file(file_path)+".transcache"    
    if os.path.isfile(transpath):
        with open(transpath, "r") as f:
            return json.load(f)
        
    apikey = os.getenv("DEEPINFRAKEY")
    client = OpenAI(
        api_key= apikey,
        base_url="https://api.deepinfra.com/v1/openai"
    )

    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
    model="openai/whisper-large-v3",
        file=audio_file,
        response_format="verbose_json",
        language="zh",
        timestamp_granularities=["segment"],
    )
    roar = []
    for s in transcript.segments:
        ret = {}
        ret['text'] = s.text
        ret['start_time'] = s.start
        ret['end_time'] = s.end
        roar.append(ret)
    print(str(roar))
    with open(transpath, "w") as f:
        f.write(json.dumps(roar))
    return roar




if __name__ == "__main__":
    transcribe_audio("/home/erik/Downloads/narco13.mp3")