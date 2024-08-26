#subtitles.py
import ffmpeg
import textprocessing
import os



import speech_recognition as sr
from pydub import AudioSegment



mp3cache = '/home/erik/mp3cache'


def is_line_time_segment(line):
    if (line.find('-->') != -1):
        return True
    else:
        return False

def time_since_start(atime):
    popit = atime.split(':')
    if len(popit) == 3:
        hour = float(popit[0])
        minute = float(popit[1])
        second = float( popit[2].replace(",","."))
        totalsec = (hour*3600)+(minute*60) + second
        return totalsec
    else:
        hour = 0.0
        minute = float(popit[0])
        second = float(popit[1])
        totalsec = (hour*3600)+(minute*60) + second
        return totalsec
        


def parse_time(line):
    parts = line.split(' ')
    start_at = time_since_start(parts[0])
    end_at = time_since_start(parts[2])
    return [start_at,end_at]


def handle_waiting_for_talk(ctx,line):
    if (len(line.strip()) > 0):
        ctx[3].append(line.strip())
        return ctx
    else:
        ctx[1].append([ctx[2],ctx[3]])
        ctx[2] = None
        ctx[3] = []
        ctx[0] = 'init'
    return ctx


def handle_init(ctx,line):
    if is_line_time_segment(line):
        ctx[0] = 'waiting_for_talk'
        ctx[2] = parse_time(line)
    return ctx


def handle_vtt_line(ctx,line):
    state = ctx[0]
    if state == 'init':
        return handle_init(ctx,line)
    elif state == 'waiting_for_talk':
        return handle_waiting_for_talk(ctx,line)
    return ctx


import openrouter


def split_into_sentences(txt):
    return openrouter.do_open_opus_questions("Sp;it this text into proper sentences:\n"  + txt)

def export_audio(mp4file,outputfile,start_time,end_time):
    # Input MP4 file
    input_file = mp4file
    # Output audio file
    output_file = outputfile
    # Load the input video file
    stream = ffmpeg.input(input_file)
    # Extract the audio stream
    audio = stream.audio
    # Trim the audio stream to the desired start and end time
    trimmed_audio = audio.filter('atrim', start=start_time, end=end_time)
    # Write the trimmed audio to the output file
    ffmpeg.output(trimmed_audio, output_file).run()


def cut_out_audio(mp3file,outputfile,start_time,end_time):
    # Load the audiotfile
    audio = AudioSegment.from_file(mp3file, format="mp3")
    # Trim the audio stream to the desired start and end time
    trimmed_audio = audio[start_time*1000:end_time*1000]
    # Write the trimmed audio to the output file
    trimmed_audio.export(outputfile, format="mp3")




def export_vtt(ctx,start_time,end_time):
    lines = ctx[1]
    output = ''
    for l in lines:
        start = l[0][0]
        end = l[0][1]
        if start > start_time and end < end_time:
            for i in l[1]:
               output += i + '\n'
    return output


def export_vtt_for_time_codes(ctx,start_time,end_time):
    lines = ctx[1]
    returnlines = []
    totalseconds = 0
    for l in lines:
        start = l[0][0]
        end = l[0][1]
        if start > start_time and end < end_time:
            wholeline = ''
            for i in l[1]:
               wholeline += i + ' '
            tokens = textprocessing.split_text(wholeline)
            duration = end-start            
            returnlines.append([tokens,'***',totalseconds,duration])
            totalseconds+=duration 
    return returnlines
    


def parse_vtt(lines):
    ctx = ['init',[],None,[]]
    for l in lines:
        ctx = handle_vtt_line(ctx,l)
    return ctx

import random
import json
import subprocess

def get_filename_without_extension(filepath):
  """Extracts the filename without extension from a filepath.

  Args:
    filepath: The path to the file.

  Returns:
    The filename without extension.
  """

  # Get the base filename (with extension) from the filepath.
  basename = os.path.basename(filepath)
  # Split the basename by '.' and return the first element (filename).
  return os.path.splitext(basename)[0]


def characters_per_minute(vttfile,start_time,duration):
    f = open(vttfile,'r',encoding='utf-8')
    ctx = parse_vtt(f.readlines())
    f.close()
    output = export_vtt(ctx,start_time,start_time+duration)
    len_output = len(output)
    return float(len_output) / float(duration/60.0)
    

def cutout(mp4file,vttfile,start_time,duration):
    start_in_seconds = time_since_start(start_time)
    end_in_seconds = start_in_seconds + duration
    chosennumber = str(start_time)+"_"+str(duration)     
    filepath = mp3cache + '/' + 'spokenarticle'+ get_filename_without_extension(vttfile) +"."+ chosennumber + '.mp3'
    filepath = filepath.replace(" ",".")
    filepath = filepath.replace("_",".")
    if mp4file.find('mp3') != -1:
        cut_out_audio(mp4file,filepath,start_in_seconds,end_in_seconds)
    else:
        export_audio(mp4file,filepath,start_in_seconds,end_in_seconds)
        
    f = open(vttfile,'r',encoding='utf-8')
    ctx = parse_vtt(f.readlines())
    f.close()
    output_vtt = export_vtt(ctx,start_in_seconds,end_in_seconds)
    output_vtt = textprocessing.make_sure_traditional(output_vtt)
    output_vtt = output_vtt    
    pop = textprocessing.split_text(output_vtt)
    f = open(filepath+'.hint.json','w',encoding='utf-8')
    f.write(json.dumps(pop))
    f.close()
    
    timelines = export_vtt_for_time_codes(ctx,start_in_seconds,end_in_seconds)
    f = open(filepath+'.times.json','w',encoding='utf-8')
    f.write(json.dumps(timelines))
    f.close()
    
    
    # a raw file
    f = open('time.txt','w',encoding='utf-8')
    f.write(output_vtt)
    f.close()
    
    
    output = "aws polly synthesize-speech --output-format mp3 --voice-id \"Hiujin\" --engine neural --text \"" + output_vtt + "\" " + filepath + ".simple.mp3"
    result = subprocess.run(output,shell=True,capture_output=True,text=True)
    print(result)
    f = open(filepath+'.simple.mp3.hint.json','w',encoding='utf-8')
    f.write(json.dumps(pop))
    f.close()

   
    scpcommand = "scp " + filepath + "* chinese.eriktamm.com:/var/www/html/mp3"
    subprocess.run(scpcommand,shell=True,capture_output=True,text=True)        
    scpcommand = "scp " + filepath + '.hint.json'" chinese.eriktamm.com:/var/www/html/mp3"   
    subprocess.run(scpcommand,shell=True,capture_output=True,text=True)    


import re

def srt_to_vtt(srt_file_path, vtt_file_path):
    def convert_time(time_string):
        """Convert SRT time format to VTT time format."""
        # Replace comma with dot for milliseconds
        return time_string.replace(',', '.')
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.read()
        # Add WEBVTT header
        vtt_content = "WEBVTT\n\n"

        # Use regex to find and process each subtitle block
        subtitle_blocks = re.findall(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:(?!\n\n).|\n)*)', srt_content, re.DOTALL)

        for block in subtitle_blocks:
            # Convert time format
            start_time = convert_time(block[1])
            end_time = convert_time(block[2])
            
            # Add the converted block to VTT content
            vtt_content += f"{start_time} --> {end_time}\n{block[3]}\n\n"

        # Write the VTT content to file
        with open(vtt_file_path, 'w', encoding='utf-8') as vtt_file:
            vtt_file.write(vtt_content)

        print(f"Conversion complete. VTT file saved as {vtt_file_path}")

    except FileNotFoundError:
        print(f"Error: The file {srt_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
# srt_to_vtt('path/to/your/input.srt', 'path/to/your/output.vtt')


def makeVTT_flle_path_and_name(name):
    return '/home/erik/Downloads/'+ name+'.vtt'

def makeSRT_flle_path_and_name(name):
    return '/home/erik/Downloads/'+ name+'.srt'


def process_movie(name):
    for i in range(0,120,2):
        x = i * 60
        print("density " +str(i) + " " + str( characters_per_minute('/home/erik/Downloads/'+ name+'.vtt',x,120)))
        if characters_per_minute('/home/erik/Downloads/'+name+'.vtt',x,120) > 80:
            pop = "" + str(int(i/60))+":"+str(int(i%60))+":00"
            cutout('/home/erik/Downloads/'+name +'.mp4','/home/erik/Downloads/'+name+'.vtt',pop,120)   


def process_mp3(name):
    for i in range(0,120,2):
        x = i * 60
        srt_to_vtt(makeSRT_flle_path_and_name(name),makeVTT_flle_path_and_name(name))
        print("density " +str(i) + " " + str( characters_per_minute( makeVTT_flle_path_and_name(name)  ,x,120)))
        if characters_per_minute('/home/erik/Downloads/'+name+'.vtt',x,120) > 80:
            pop = "" + str(int(i/60))+":"+str(int(i%60))+":00"
            cutout('/home/erik/Downloads/'+name +'.mp3','/home/erik/Downloads/'+name+'.vtt',pop,120)   

 
import webrtcvad
import wave
import contextlib
from pydub import AudioSegment
from pydub.utils import make_chunks       

def convert_mp4_to_mp3(mp4_file, mp3_file):
    # Output audio file
    output_file = mp3_file
    # Load the input video file
    stream = ffmpeg.input(mp4_file)
    # Extract the audio stream
    audio = stream.audio
    # Trim the audio stream to the desired start and end time
    trimmed_audio = audio.filter('atrim')
    # Write the trimmed audio to the output file
    ffmpeg.output(trimmed_audio, output_file).run()


def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate
    

def extract_segments(input_file, segments, output_file):
    # Load the audio file
    audio = AudioSegment.from_mp3(input_file)    
    # Initialize an empty audio segment for the output
    output_audio = AudioSegment.empty()    
    # Extract and concatenate the specified segments
    for start, end in segments:
        # Convert time to milliseconds
        start_ms = int(start * 1000.0)
        end_ms = int(end * 1000.0)        
        # Extract the segment and add it to the output audio
        segment = audio[start_ms:end_ms]
        output_audio += segment    
    # Export the result to a new MP3 file
    output_audio.export(output_file, format="mp3")
    
    print(f"Extracted segments saved to {output_file}")


def detect_speech(audio_file, frame_duration_ms=30, padding_duration_ms=300, aggressiveness=2):
    if audio_file.find('mp4') != -1:
        convert_mp4_to_mp3(audio_file,audio_file+".mp3")
        audio_file = audio_file+".mp3"
    audio = AudioSegment.from_mp3(audio_file)
    audio = audio.set_channels(1)  # Convert to mono
    audio = audio.set_frame_rate(16000)  # Set sample rate to 16kHz

    vad = webrtcvad.Vad(aggressiveness)

    # Convert audio to raw PCM
    raw_data = audio.raw_data
    sample_rate = audio.frame_rate

    # Create frames
    frame_length = int(sample_rate * (frame_duration_ms / 1000.0))
    frames = make_chunks(audio, frame_duration_ms)

    speech_segments = []
    is_speech = False
    start_time = 0

    for i, frame in enumerate(frames):
        is_speech_frame = vad.is_speech(frame.raw_data, sample_rate)

        if is_speech_frame and not is_speech:
            is_speech = True
            start_time = i * frame_duration_ms / 1000.0
        elif not is_speech_frame and is_speech:
            end_time = i * frame_duration_ms / 1000.0
            if end_time - start_time >= padding_duration_ms / 1000.0:
                speech_segments.append((start_time, end_time))
            is_speech = False

    # Handle the case where speech continues to the end of the file
    if is_speech:
        end_time = len(frames) * frame_duration_ms / 1000.0
        if end_time - start_time >= padding_duration_ms / 1000.0:
            speech_segments.append((start_time, end_time))
            
    extract_segments(audio_file,speech_segments,audio_file+".sp.mp3")
    return speech_segments


        

if __name__ == "__main__":
    """
    process_movie('wildwest')
    process_movie('dino')
    process_movie('fistoflegend')
    process_movie('beautyandthebeast')
    process_movie('teacherpet1')
    process_movie('rocketeer')
    process_movie('druglords')
    process_movie('incredibles1')
    process_movie('stained2')
    process_movie('stained3')
    process_movie('whitestorm')
    process_movie('harrypotter1')
    detect_speech('/home/erik/Downloads/_bolt.mp4')
    process_movie('whitestorm')
    process_movie('bolt')
    process_movie('monsterinc')
    
    process_movie('whitestorm')home
    process_movie('nemo')
    process_movie('pjspeedcat_spoken')
    process_movie('electionspoken')
    process_movie('deathnotice1')

    process_mp3('JackmanPomato')

    process_mp3('breakingyourself_br')    
    process_mp3('theonething_br')
    process_mp3('sparksine')

    process_mp3('bakbingEP73')

    process_mp3('hkbookfair')
    process_mp3('hkoffice')
    process_mp3('hkpopulation')
    process_mp3('hkcourtjimmy')    
    process_movie('aberdeen')

    process_mp3('chopchoplady_sr')    
    process_mp3('ladies12')
    process_mp3('ladies160')

    process_mp3('ngaihimjanmat4')

    process_mp3('ladies164')

    process_mp3('ladies163')

    process_mp3('ladies161_001')
    process_mp3('ladies161_002')

    process_mp3('buddha5_part2')

    """
        
    process_movie('coldwar')


