import os
import mysql.connector
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2
import json
import io

def get_mp3_title(file_path):
    try:
        # Try to load ID3 tags
        audio = ID3(file_path)
        
        # Check if the title tag exists
        if 'TIT2' in audio:
            return audio['TIT2'].text[0]
        else:
            return "Title not found in ID3 tags"
    
    except:
        # If ID3 tags are not present, try to get the filename
        try:
            audio = MP3(file_path)
            return os.path.splitext(os.path.basename(file_path))[0]
        except:
            return "Unable to read the file"


def get_db_connection():
    db = mysql.connector.connect(
        host="localhost",                                                            
        user="erik",                                                                 
        password="ninjadogs",                                                        
        database='language'                                                          
    )
    cursor = db.cursor()
    return db,cursor

def close_db_connect(db,cursor):
    cursor.close()
    db.close()
    
def add_transcription(audio_file_id, transcription_content, comment):
    db,cursor  = get_db_connection()
    sql = """INSERT INTO transcription_data 
             (imported_audio_files_id, content, comment) 
             VALUES (%s, %s, %s)"""
    
    # Convert the Python dictionary to a JSON string
    content_json = json.dumps(transcription_content)    
    values = (audio_file_id, content_json, comment)    
    cursor.execute(sql, values)
    db.commit()
    new_id = cursor.lastrowid
    close_db_connect(db,cursor)
    print(f"Added transcription data for audio file {audio_file_id}")
    return new_id

import shutil

import subprocess

def add_mp3_to_database(file_path): 
    # Database connection setup
    print("Here comes the add_mp3_to_database")
    print("type of filename is " + str(type(file_path)))
    db,cursor  = get_db_connection()
    # Get the file name from the path
    file_name = os.path.basename(file_path)    
    # Get MP3 metadata
    title = get_mp3_title(file_path)
    duration = int(1000)
    # Define the destination directory
    dest_dir = "/opt/shared_audio"
    # Create the destination directory if it doesn't exist
    # Copy the file to the destination directory
    print(file_path)
    f = open(file_path,'rb')
    binarydata = f.read()
    f.close()
    f = open(dest_dir+"/"+file_name,'wb')
    f.write(binarydata)
    f.close()
    
    # Insert metadata into the database
    sql = """INSERT INTO imported_audio_files 
             (file_name, file_path, title, duration) 
             VALUES (%s, %s, %s, %s)"""
    values = (file_name, dest_dir+"/"+file_name, title, duration)    
    cursor.execute(sql, values)
    db.commit()
    new_id = cursor.lastrowid
    print(f"Added {file_name} to the database.")
    close_db_connect(db,cursor)
    return new_id

        
def get_audio_files_list():
    db,cursor  = get_db_connection()    
    sql = """SELECT id, title, file_path 
             FROM audio_files 
             ORDER BY id"""    
    cursor.execute(sql)
    results = cursor.fetchall()
    audio_files = []
    for row in results:     
        audio_files.append({
            'id': row['id'],
            'title': row['title'],
            'file_path': row['file_path']
        })
    close_db_connect(db,cursor)
    return audio_files

def add_word_timestamp(db,cursor,mp3_name, start_time, end_time, word, eng_word):
    sql = """INSERT INTO word_timestamps 
             (mp3_name, start_time, end_time, word, eng_word) 
             VALUES (%s, %s, %s, %s, %s)"""
    
    values = (mp3_name, start_time, end_time, word, eng_word)    
    cursor.execute(sql, values)
    new_id = cursor.lastrowid    
    print(f"Added word timestamp with ID {new_id}")
    return new_id


def add_processed_mp3(file_path,jsoncontent,comment):
    newid = add_mp3_to_database(file_path)
    add_transcription(newid,jsoncontent,comment)    
    db,cursor  = get_db_connection()    
    data = jsoncontent
    results = data['results']
    file_name = os.path.basename(file_path)
    for r in results:
        add_word_timestamp(db,cursor,file_name, r['start_time'], r['end_time'], r['alternatives'][0]['content'], '')
    db.commit()
    close_db_connect(db,cursor)


def explode_file(filename):
    shutil.copy2("/opt/shared_audio/"+filename,"/var/www/html/mp3")
    sql = """SELECT id, word, start_time,end_time 
             FROM word_timestamps where mp3_name = '""" + filename + """' 
             ORDER BY start_time"""    
    print(sql)
    db,cursor  = get_db_connection()
    cursor.execute(sql)
    results = cursor.fetchall()
    words = []
    for row in results:     
        words.append({
            'word': row[1],
            'start_time': row[2],
            'end_time': row[3]
        })
    close_db_connect(db,cursor)
    text =''
    for i in words:
        text = text + i['word']
        if i['word']=='。' or i['word']=='？':
            text = text + '\n'
    f = open('/var/www/html/mp3/'+filename+".hint",'w',encoding='utf-8')
    f.write(text)
    f.close()
    