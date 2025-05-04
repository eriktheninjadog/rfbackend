import deepinfra
import mp3helper
import texttoaudio
import os
import newscrawler

def create_filename_for_segment(text):
    padded_text = text + texttoaudio.get_pause_as_ssml_tag()
    filename = texttoaudio.filename_from_string(padded_text)
    return filename


def combined_length(lines):
    cnt = 0
    for l in lines:
        cnt +=len(l)
    return cnt


def pad_time(times):
    start_time = times[0]
    start_time -= 0.5
    end_time = times[1]
    end_time += 0.5
    if start_time < 0:
        start_time = 0
    
    return [start_time,end_time]

import webapi

import remotechineseclient

def process_mp3_file(file_path,filename_addon="work",minlength=10):
    # get the transcription
    transcription = deepinfra.transcribe_audio(file_path)
    sentences = []
    timepoints = []
    current_sentence = ""
    start_time = 0
    end_time = 0
    for segment in transcription:
        text = segment['text']
        current_sentence = current_sentence + text
        if start_time == 0:
            start_time = segment['start_time']
        end_time = segment['end_time']
        if end_time == 0:
            totaltime= mp3helper.get_total_mp3_duration([file_path])
            end_time = totaltime
        if (len(current_sentence) > minlength):
            timepoints.append(pad_time([start_time,end_time]))
            print(f"Segment: {text} (Start: {start_time}, End: {end_time})")
            sentences.append(current_sentence)
            filename = create_filename_for_segment(text)
            part_file_path = texttoaudio.mp3cachedirectory + '/' + filename
            if  os.path.isfile(part_file_path) == False:
                mp3helper.extract_audio_segment(file_path, start_time, end_time, part_file_path)
            current_sentence = ""
            start_time = 0
            end_time = 0

    if len(current_sentence) > 0:
        timepoints.append(pad_time([start_time,end_time-0.5]))
        print(f"Segment: {text} (Start: {start_time}, End: {end_time})")
        sentences.append(current_sentence)
        filename = create_filename_for_segment(text)
        part_file_path = texttoaudio.mp3cachedirectory + '/' + filename

    totaltext = " ".join(sentences)
    #remotechineseclient.access_remote_client("make_c1_examples",{"pattern":" using vocabulary found in this text: \n "+totaltext})

    #done with the mp3 partswords_thats_been_given
    currentpod = []
    pods = []
    start_time = end_time = 0
    cnt = 0
    for s in sentences:
        if combined_length(currentpod) < 500:
            if start_time == 0:                
                start_time = timepoints[cnt][0]
            end_time = timepoints[cnt][1]
            if end_time == 0:
                end_time = start_time + 1
            currentpod.append(s)
        else:
            if end_time == 0:
                end_time = start_time + 1

            pods.append([start_time,end_time,currentpod])
            currentpod = []
            currentpod.append(s)
            start_time = end_time = 0
        cnt+=1
    pods.append([start_time,end_time,currentpod])
    words_thats_been_given = []
    cnt = 0
    for bagofsentences in pods:
        # lets cut out the real audio
        start_time = bagofsentences[0]
        end_time = bagofsentences[1]
        mp3helper.extract_audio_segment(file_path,start_time,end_time,str(cnt) + "prepostfixtmp.mp3")
        clean_text, sml_text = texttoaudio.make_sml_from_chinese_sentences(words_thats_been_given,bagofsentences[2],include_prepostfix=False)
        newscrawler.make_and_upload_audio_from_sml(clean_text, sml_text,filename_addon+str(cnt),postprefixaudio=str(cnt) + "prepostfixtmp.mp3")
        cnt+=1
    

import subprocess    

def handle_local_mp3(name):
    file ="/home/erik/Downloads/"+name+".mp3"
    command = "ffmpeg -y -loglevel verbose -analyzeduration 2000 -probesize 10000000 -i " + file+ " tmp.wav"
    subprocess.run(command, shell=True)
    command = "ffmpeg -y -loglevel verbose -i tmp.wav tmp.mp3"
    subprocess.run(command, shell=True)
    process_mp3_file("tmp.mp3",filename_addon=name)
    

if __name__ == "__main__":
    #handle_local_mp3("flight11")
    #handle_local_mp3("doctor1")
    handle_local_mp3("news2")
    #handle_local_mp3("narco13")

#process_mp3_file("/home/erik/Downloads/ethree1.mp3",filename_addon="three1")
#process_mp3_file("/home/erik/Downloads/three2.mp3",filename_addon="three2")
