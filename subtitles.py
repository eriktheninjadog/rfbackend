#subtitles.py
import ffmpeg
import textprocessing
import os


mp3cache = '/home/erik/mp3cache'


def is_line_time_segment(line):
    if (line.find(',end') != -1):
        return True
    else:
        return False

def time_since_start(atime):
    popit = atime.split(':')
    hour = float(popit[0])
    minute = float(popit[1])
    second = float(popit[2])
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
    filepath = mp3cache + '/' + 'spokenarticle#'+ get_filename_without_extension(vttfile) +"#"+ chosennumber + '.mp3'
    filepath = filepath.replace(" ","#")
    filepath = filepath.replace("_","#")    
    export_audio(mp4file,filepath,start_in_seconds,end_in_seconds)

    f = open(vttfile,'r',encoding='utf-8')
    ctx = parse_vtt(f.readlines())
    f.close()
    output_vtt = export_vtt(ctx,start_in_seconds,end_in_seconds)
    output_vtt = textprocessing.make_sure_traditional(output_vtt)
    output_vtt = get_filename_without_extension(vttfile) + "\n" + output_vtt
    pop = textprocessing.split_text(output_vtt)
    f = open(filepath+'.hint.json','w',encoding='utf-8')
    f.write(json.dumps(pop))
    f.close()
    
    scpcommand = "scp " + filepath + "* chinese.eriktamm.com:/var/www/html/mp3"
    subprocess.run(scpcommand,shell=True,capture_output=True,text=True)        
    scpcommand = "scp " + filepath + '.hint.json'" chinese.eriktamm.com:/var/www/html/mp3"   
    subprocess.run(scpcommand,shell=True,capture_output=True,text=True)    
    None


def process_movie(name):
    for i in range(0,120,2):
        x = i * 60
        print("density " +str(i) + " " + str( characters_per_minute('/home/erik/Downloads/'+ name+'.vtt',x,120)))
        if characters_per_minute('/home/erik/Downloads/'+name+'.vtt',x,120) > 80:
            pop = "" + str(int(i/60))+":"+str(int(i%60))+":00"
            cutout('/home/erik/Downloads/'+name +'.mp4','/home/erik/Downloads/'+name+'.vtt',pop,120)   
        
if __name__ == "__main__":
    """
    process_movie('wildwest')
    process_movie('dino')
    process_movie('fistoflegend')
    process_movie('beautyandthebeast')
    process_movie('teacherpet1')
    process_movie('rocketeer')
    process_movie('druglords')
    process_movie('harrypotter1')
    process_movie('whitestorm')

    process_movie('monsterinc')
"""
    process_movie('stained1')


