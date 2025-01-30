#whispertosrt.py
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
import torch
from datetime import timedelta
from pydub import AudioSegment
import numpy as np
import os
import math

class AudioChunkProcessor:
    def __init__(self, chunk_duration=30, overlap_duration=2):
        """
        Initialize the processor with chunk settings
        chunk_duration: length of each chunk in seconds
        overlap_duration: overlap between chunks in seconds
        """
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize Whisper
        print("Loading Whisper model...")
        model_name = "alvanlii/whisper-small-cantonese"
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.model = self.model.to(self.device)

    def split_audio(self, input_file):
        """Split audio file into overlapping chunks"""
        print(f"Loading audio file: {input_file}")
        audio = AudioSegment.from_file(input_file)
        
        # Convert durations to milliseconds
        chunk_length = self.chunk_duration * 1000
        overlap_length = self.overlap_duration * 1000
        
        chunks = []
        offset = 0
        counter = 0
        
        while offset < len(audio):
            start = max(0, offset - overlap_length) if offset > 0 else 0
            end = min(len(audio), offset + chunk_length + overlap_length)
            
            chunk = audio[start:end]
            chunk_name = f"temp_chunk_{counter}.wav"
            chunk.export(chunk_name, format="wav")
            
            chunks.append({
                'file': chunk_name,
                'start': start / 1000,  # Convert to seconds
                'end': end / 1000,
                'offset': offset / 1000
            })
            
            offset += chunk_length
            counter += 1
            
        return chunks

    def process_chunk(self, chunk_info):
        """Process a single audio chunk"""
        try:
            # Load and process audio
            speech_array, sampling_rate = librosa.load(chunk_info['file'], sr=16000)
            inputs = self.processor(speech_array, sampling_rate=sampling_rate, return_tensors="pt")
            input_features = inputs.input_features.to(self.device)

            # Generate transcription
            predicted_ids = self.model.generate(
                input_features,
                return_timestamps=True,
                max_length=448
            )

            # Decode and adjust timestamps
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=False)
            segments = self.parse_timestamps(transcription[0], chunk_info['offset'])
            
            return segments
            
        finally:
            # Clean up temporary file
            if os.path.exists(chunk_info['file']):
                os.remove(chunk_info['file'])

    def parse_timestamps(self, transcription, offset):
        """Parse timestamp tokens and adjust for chunk offset"""
        timestamp_tokens = transcription.split()
        segments = []
        current_segment = {"start": 0, "end": 0, "text": []}

        for token in timestamp_tokens:
            if token.startswith("<|") and token.endswith("|>"):
                if token == "<|notimestamps|>":
                    continue
                try:
                    time_value = float(token.replace("<|", "").replace("|>", ""))
                    time_value += offset  # Adjust timestamp for chunk offset
                    
                    if not current_segment["text"]:
                        current_segment["start"] = time_value
                    else:
                        current_segment["end"] = time_value
                        if current_segment["text"]:
                            segments.append({
                                "start": current_segment["start"],
                                "end": current_segment["end"],
                                "text": " ".join(current_segment["text"]).strip()
                            })
                        current_segment = {"start": time_value, "end": 0, "text": []}
                except ValueError:
                    continue
            else:
                current_segment["text"].append(token)

        return segments

    def merge_segments(self, all_segments):
        """Merge segments from different chunks and handle overlaps"""
        # Flatten all segments
        flat_segments = []
        for segments in all_segments:
            flat_segments.extend(segments)
            
        # Sort by start time
        flat_segments.sort(key=lambda x: x['start'])
        
        # Merge overlapping segments
        merged = []
        if not flat_segments:
            return merged
            
        current = flat_segments[0]
        for segment in flat_segments[1:]:
            if segment['start'] - current['end'] < self.overlap_duration:
                # Merge overlapping segments
                current['end'] = max(current['end'], segment['end'])
                current['text'] = current['text'] + " " + segment['text']
            else:
                merged.append(current)
                current = segment
                
        merged.append(current)
        return merged
    

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    td = timedelta(seconds=float(seconds))
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")

def split_long_lines(text, max_length=42):
    """Split long lines to improve readability"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)

    
def save_as_srt(segments, output_file):
    """Save transcription as SRT file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            f.write(f"{i}\n")
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{split_long_lines(segment['text'])}\n\n")


def process_audio_file(input_file, output_file, chunk_duration=30, overlap_duration=2):
    """Process complete audio file with chunking"""
    processor = AudioChunkProcessor(chunk_duration, overlap_duration)
    
    # Split audio into chunks
    print("Splitting audio into chunks...")
    chunks = processor.split_audio(input_file)
    
    # Process each chunk
    print(f"Processing {len(chunks)} chunks...")
    all_segments = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        segments = processor.process_chunk(chunk)
        all_segments.append(segments)
    
    # Merge segments
    print("Merging segments...")
    merged_segments = processor.merge_segments(all_segments)
    
    # Save as SRT
    print("Saving SRT file...")
    save_as_srt(merged_segments, output_file)
    
    return merged_segments

# [Previous helper functions (format_timestamp, save_as_srt, split_long_lines, filter_segments) remain the same]

if __name__ == "__main__":
    input_file = "path/to/your/audio.wav"
    output_file = "transcription.srt"
    
    try:
        # Process with specific chunk duration and overlap
        segments = process_audio_file(
            input_file,
            output_file,
            chunk_duration=30,  # 30 seconds per chunk
            overlap_duration=2   # 2 seconds overlap
        )
        
        print(f"\nTranscription saved as SRT file: {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
