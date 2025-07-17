import os
import time
import subprocess
import requests
import deepinfra

# --- Configuration (Loaded from Environment Variables) ---
M3U8_URL = "https://rthkradio1-live.akamaized.net/hls/live/2035313/radio1/master.m3u8"  # Or get from command-line arguments
TRANSCRIPTION_API_URL = os.getenv("TRANSCRIPTION_API_URL")
TRANSCRIPTION_API_KEY = os.getenv("TRANSCRIPTION_API_KEY")
UPLOAD_USER = "erik"
UPLOAD_HOST = "chinese.eriktamm.com"
UPLOAD_PATH = "/var/www/html/mp3"

CHUNK_DIR = "chunks"
PROCESSED_DIR = "processed"

def convert_to_mp3(ts_file_path):
    """Converts a .ts video chunk to an .mp3 audio file."""
    mp3_file_path = os.path.splitext(ts_file_path)[0] + ".mp3"
    print(f"Converting {ts_file_path} to {mp3_file_path}...")
    
    command = [ 
        "ffmpeg",
        "-i", ts_file_path,
        "-vn",  # No video
        "-acodec", "libmp3lame", # Use LAME MP3 encoder
        "-q:a", "2", # Good quality VBR
        mp3_file_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Conversion successful.")
        return mp3_file_path
    except subprocess.CalledProcessError as e:
        print(f"Error during MP3 conversion for {ts_file_path}:")
        print(e.stderr)
        return None

def transcribe_audio(mp3_file_path):
    """Calls a transcription API and saves the resulting SRT file."""
    srt_file_path = os.path.splitext(mp3_file_path)[0] + ".srt"
    print(f"Transcribing {mp3_file_path}...")    
    try:
        srt_file_path = mp3_file_path + ".srt" if not srt_file_path.endswith(".srt") else srt_file_path
        deepinfra.write_srt_from_audio(mp3_file_path, output_srt_path=srt_file_path)
            
        print(f"Transcription successful. SRT saved to {srt_file_path}")
        return srt_file_path
    except requests.exceptions.RequestException as e:
        print(f"Error calling transcription API for {mp3_file_path}: {e}")
        return None

def upload_files(mp3_path, srt_path):
    """Uploads the MP3 and SRT files to the remote server using scp."""
    print(f"Uploading {os.path.basename(mp3_path)} and {os.path.basename(srt_path)}...")
    
    if not all([UPLOAD_USER, UPLOAD_HOST, UPLOAD_PATH]):
        print("Error: Upload server details not set in environment variables.")
        return False

    destination = f"{UPLOAD_USER}@{UPLOAD_HOST}:{UPLOAD_PATH}"
    command = ["scp", mp3_path, srt_path, destination]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Upload successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error uploading files:")
        print(e.stderr)
        return False

def main():
    """Main function to run the producer-consumer pipeline."""
    processed_files = set()

    # --- Start the Producer (ffmpeg) ---
    ffmpeg_command = [
        "ffmpeg", "-i", M3U8_URL,
        "-c", "copy", "-f", "segment", "-segment_time", "300",
        "-reset_timestamps", "1", "-strftime", "1",
        os.path.join(CHUNK_DIR, "chunk_%Y-%m-%d_%H-%M-%S.ts")
    ]
    
    print("Starting ffmpeg stream downloader in the background...")
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # --- Start the Consumer (File Watcher) ---
    try:
        while True:
            # Check if ffmpeg is still running
            if ffmpeg_process.poll() is not None:
                print("ffmpeg process has terminated. Exiting.")
                break

            # Find unprocessed .ts files in the chunk directory
            # Sort them to process in order
            chunk_files = sorted([f for f in os.listdir(CHUNK_DIR) if f.endswith('.ts')])
            
            # Find the latest fully written chunk (heuristic: it's not the very last one)
            # This prevents us from grabbing a file that ffmpeg is still writing to.
            if len(chunk_files) > 1:
                # The chunks to process are all but the last one
                to_process = [f for f in chunk_files[:-1] if f not in processed_files]
            else:
                to_process = []
            
            for ts_filename in to_process:
                print(f"\n--- Found new chunk: {ts_filename} ---")
                ts_filepath = os.path.join(CHUNK_DIR, ts_filename)
                
                # 1. Convert to MP3
                mp3_filepath = convert_to_mp3(ts_filepath)
                if not mp3_filepath:
                    continue  # Skip to next file on failure

                # 2. Transcribe
                srt_filepath = transcribe_audio(mp3_filepath)
                if not srt_filepath:
                    # Clean up the mp3 if transcription fails
                    os.remove(mp3_filepath)
                    continue

                # 3. Upload
                if upload_files(mp3_filepath, srt_filepath):
                    # 4. Move processed files for archival
                    print(f"Moving processed files to {PROCESSED_DIR}")
                    os.rename(ts_filepath, os.path.join(PROCESSED_DIR, os.path.basename(ts_filepath)))
                    os.rename(mp3_filepath, os.path.join(PROCESSED_DIR, os.path.basename(mp3_filepath)))
                    os.rename(srt_filepath, os.path.join(PROCESSED_DIR, os.path.basename(srt_filepath)))
                    processed_files.add(ts_filename) # Mark as processed
                else:
                    print("Upload failed. Will retry on next loop.")

            # Wait before checking for new files again
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nInterruption detected. Shutting down ffmpeg...")
    finally:
        # Ensure ffmpeg process is terminated when the script exits
        if ffmpeg_process.poll() is None:
            ffmpeg_process.terminate()
            ffmpeg_process.wait()
            print("ffmpeg process terminated.")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(CHUNK_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    main()