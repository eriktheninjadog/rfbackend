import os
import mysql.connector
from mutagen.mp3 import MP3
import json
import io

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
             (audio_file_id, content, comment) 
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
    db,cursor  = get_db_connection()
    # Get the file name from the path
    file_name = os.path.basename(file_path)    
    # Get MP3 metadata
    title = file_name
    duration = int(1000)
    # Define the destination directory
    dest_dir = "/opt/shared_audio"
    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)    
    # Copy the file to the destination directory
    dest_path = os.path.join(dest_dir, file_name)
    subprocess.run("cp '"+file_path +"' " + dest_dir)    
    # Insert metadata into the database
    sql = """INSERT INTO imported_audio_files 
             (file_name, file_path, title, duration) 
             VALUES (%s, %s, %s, %s)"""
    values = (file_name, dest_path, title, duration)    
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
    db.commit()
    new_id = cursor.lastrowid    
    print(f"Added word timestamp with ID {new_id}")
    return new_id


def add_processed_mp3(file_path,jsoncontent,comment):
    newid = add_mp3_to_database(file_path)
    add_transcription(newid,jsoncontent,comment)    
    db,cursor  = get_db_connection()    
    data = json.loads(jsoncontent)
    results = data['results']
    file_name = os.path.basename(file_path)
    for r in results:
        add_word_timestamp(db,cursor,file_name, r['start_time'], r['end_time'], r['alternatives'][0]['content'], '')
    close_db_connect(db,cursor)
