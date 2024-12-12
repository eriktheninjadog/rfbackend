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

def process_mp3_file(file_path):
    # get the transcription
    transcription = deepinfra.transcribe_audio(file_path)
    sentences = []
    timepoints = []
    for segment in transcription:
        text = segment['text']
        start_time = segment['start_time']
        end_time = segment['end_time']
        timepoints.append([start_time,end_time])
        print(f"Segment: {text} (Start: {start_time}, End: {end_time})")
        sentences.append(text)
        filename = create_filename_for_segment(text)
        part_file_path = texttoaudio.mp3cachedirectory + '/' + filename
        if  os.path.isfile(part_file_path) == False:
            mp3helper.extract_audio_segment(file_path, segment['start_time'], segment['end_time'], part_file_path)
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
            currentpod.append(s)
        else:
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
        newscrawler.make_and_upload_audio_from_sml(clean_text, sml_text,"orgmp3_"+str(cnt),postprefixaudio=str(cnt) + "prepostfixtmp.mp3")
        cnt+=1
    
    
if __name__ == "__main__":
    process_mp3_file("/home/erik/Downloads/horror1.mp3")