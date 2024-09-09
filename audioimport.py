#audioimport.py

import os
import mysql.connector
from mutagen.mp3 import MP3


def add_mp3_to_database(file_path):
# Database connection setup
    db = mysql.connector.connect(
        host="localhost",                                                            
        user="erik",                                                                 
        password="ninjadogs",                                                        
        database='language'                                                          
    )
    cursor = db.cursor()
    # Get the file name from the path
    file_name = os.path.basename(file_path)    
    # Get MP3 metadata
    audio = MP3(file_path)
    # Extract metadata (adjust as needed based on your MP3 files)
    title = audio.get('TIT2', ['Unknown Title'])[0]
    duration = int(audio.info.length)
    # Define the destination directory
    dest_dir = "/opt/shared_audio"
    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)    
    # Copy the file to the destination directory
    dest_path = os.path.join(dest_dir, file_name)
    os.system(f"cp '{file_path}' '{dest_path}'")    
    # Insert metadata into the database
    sql = """INSERT INTO imported_audio_files 
             (file_name, file_path, title, duration) 
             VALUES (%s, %s, %s, %s)"""
    values = (file_name, dest_path, title, artist, album, duration)    
    cursor.execute(sql, values)
    db.commit()
    print(f"Added {file_name} to the database.")
    cursor.close()
    db.close()

# Example usage
#mp3_file = "/path/to/your/mp3/file.mp3"
#add_mp3_to_database(mp3_file)

# Close the database connection
