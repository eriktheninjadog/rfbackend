from google.cloud import texttospeech


import math
import os
import io
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment

def split_mp3(mp3_file, output_dir, part_duration=5*60*1000):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file)
    
    # Get the total duration of the audio in milliseconds
    total_duration = len(audio)
    
    # Calculate the number of parts
    num_parts = math.ceil(total_duration / part_duration)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Split the audio into parts
    for i in range(num_parts):
        start_time = i * part_duration
        end_time = min((i + 1) * part_duration, total_duration)
        
        # Extract the audio part
        audio_part = audio[start_time:end_time]
        
        # Generate the output file name
        output_file = os.path.join(output_dir, f"part_{i+1}.mp3")
        
        # Export the audio part as MP3
        audio_part.export(output_file, format="mp3")
        
        print(f"Part {i+1} exported as: {output_file}")
    


def mp3_to_srt(mp3_file, srt_file):
    # Load the MP3 file using pydub
    audio = AudioSegment.from_mp3(mp3_file)
    
    # Get the sample rate of the audio file
    sample_rate = audio.frame_rate
    
    # Convert the audio to WAV format
    wav_file = "temp.wav"
    audio.export(wav_file, format="wav")
    
    client = speech.SpeechClient()

    with io.open(wav_file, 'rb') as audio_file:
        content = audio_file.read()

    with io.open(mp3_file, 'rb') as audio_file:
        content = audio_file.read()


    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=sample_rate,
        language_code='yue-Hant-HK',
        enable_word_time_offsets=True
    )

    response = client.recognize(config=config, audio=audio)

    with open(srt_file, 'w', encoding='utf-8') as srt:
        for i, result in enumerate(response.results, start=1):
            alternative = result.alternatives[0]
            srt.write(f"{i}\n")

            start_time = alternative.words[0].start_time
            end_time = alternative.words[-1].end_time

            start_srt = f"{start_time.seconds:02d}:{start_time.microseconds // 1000:03d}"
            end_srt = f"{end_time.seconds:02d}:{end_time.microseconds // 1000:03d}"

            srt.write(f"{start_srt} --> {end_srt}\n")
            srt.write(f"{alternative.transcript}\n\n")

    print(f"SRT file generated: {srt_file}")


def text_to_speech(text, output_file):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code='yue-HK',
        name='yue-HK-Standard-A',
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_file, 'wb') as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')

# Example usage
#text = "你好，歡迎使用 Google Cloud Text-to-Speech API。"
#output_file = "cantonese_speech.mp3"

#text_to_speech(text, output_file)
split_mp3("spokenarticle_news_u2672.mp3",".",part_duration=59*1000)
mp3_to_srt("part_1.mp3","output.srt")