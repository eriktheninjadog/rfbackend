import os
import time
import subprocess
import requests
import deepinfra

import os
import time
import subprocess
import requests
import logging
import shutil # For moving files

# New imports for pydub and paramiko
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import paramiko # For SFTP uploads

# we will use huggingface
import huggingface

from huggingface_hub import InferenceClient

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration (Loaded from Environment Variables) ---
M3U8_URL = "https://rthkradio1-live.akamaized.net/hls/live/2035313/radio1/master.m3u8"  # Or get from command-line arguments
TRANSCRIPTION_API_URL = os.getenv("TRANSCRIPTION_API_URL")
TRANSCRIPTION_API_KEY = os.getenv("TRANSCRIPTION_API_KEY")
UPLOAD_USER = "erik"
UPLOAD_HOST = "chinese.eriktamm.com"
UPLOAD_PATH = "/var/www/html/mp3"

CHUNK_DIR = "chunks"
PROCESSED_DIR = "processed"

CHUNK_DIR = "chunks"
PROCESSED_DIR = "processed"
FAILED_DIR = "failed_chunks" # For chunks that consistently fail

# --- Utility Functions ---

def format_srt_time(seconds):
    """Formats a float of seconds into SRT timecode format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds * 1000) % 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

# --- Core Processor Functions ---

def convert_to_mp3(ts_file_path):
    """Converts a .ts video chunk to an .mp3 audio file using pydub."""
    mp3_file_path = os.path.splitext(ts_file_path)[0] + ".mp3"
    logging.info(f"Converting {ts_file_path} to {mp3_file_path} using pydub...")
    
    try:
        audio = AudioSegment.from_file(ts_file_path)
        audio.export(mp3_file_path, format="mp3", bitrate="128k") # Adjust bitrate as needed
        logging.info("Conversion successful via pydub.")
        return mp3_file_path
    except CouldntDecodeError as e:
        logging.error(f"Pydub couldn't decode {ts_file_path}. It might be corrupted or incomplete: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during MP3 conversion for {ts_file_path}: {e}", exc_info=True)
        return None
    
import textprocessing
def transcribe_audio(mp3_file_path):
    """
    client = InferenceClient(
        api_key=os.environ["HUGGINGFACE_KEY"],
        headers={"Authorization": f"Bearer {os.environ['HUGGINGFACE_KEY']}", "Content-Type": "audio/flac","Content-Language":"Yue"},     
        
    )
    
    #convert mp3 to flac file
    flac_file_path = os.path.splitext(mp3_file_path)[0] + ".flac"
    try:
        audio = AudioSegment.from_file(mp3_file_path)
        audio.export(flac_file_path, format="flac")
    except CouldntDecodeError as e: 
        logging.error(f"Pydub couldn't decode {mp3_file_path}. It might be corrupted or incomplete: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during FLAC conversion for {mp3_file_path}: {e}", exc_info=True)
        return None
    output = client.automatic_speech_recognition(flac_file_path, model="openai/whisper-large-v3")  
    result = textprocessing.make_sure_traditional(output.text)
    print(result)
    return None
    """
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


def upload_files_sftp(mp3_path, srt_path):
    """Uploads the MP3 and SRT files to the remote server using SFTP (paramiko)."""
    logging.info(f"Uploading {os.path.basename(mp3_path)} and {os.path.basename(srt_path)} via SFTP...")
    
    if not all([UPLOAD_USER, UPLOAD_HOST, UPLOAD_PATH]):
        logging.error("Upload server details not fully set in environment variables. Skipping upload.")
        return False

    try:
        # Create an SSH client
        with paramiko.SSHClient() as client:
            client.load_system_host_keys() # Load known_hosts
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Or better: paramiko.RejectPolicy() for production

            # Authenticate with key
            client.connect(hostname=UPLOAD_HOST, username=UPLOAD_USER)

            # Open an SFTP client
            with client.open_sftp() as sftp:
                # Ensure the remote directory exists
                try:
                    sftp.stat(UPLOAD_PATH)
                except FileNotFoundError:
                    logging.warning(f"Remote upload path {UPLOAD_PATH} does not exist. Creating it.")
                    sftp.mkdir(UPLOAD_PATH) # Will fail if parent dirs don't exist

                remote_mp3_path = os.path.join(UPLOAD_PATH, os.path.basename(mp3_path))
                remote_srt_path = os.path.join(UPLOAD_PATH, os.path.basename(srt_path))

                sftp.put(mp3_path, remote_mp3_path)
                sftp.put(srt_path, remote_srt_path)
            
            logging.info("Upload successful via SFTP.")
            return True
    except paramiko.AuthenticationException:
        logging.error(f"SFTP Authentication failed. Check username, host, and SSH key permissions for {UPLOAD_USER}@{UPLOAD_HOST}.")
        return False
    except paramiko.SSHException as e:
        logging.error(f"Could not establish SFTP connection: {e}")
        return False
    except FileNotFoundError:
        logging.error(f"SSH key not found at {SSH_KEY_PATH}. Please ensure it exists and has correct permissions.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during SFTP upload: {e}", exc_info=True)
        return False


def main():
    """Main function to run the producer-consumer pipeline."""
    processed_files = set()
    failed_attempts = {} # Track failed attempts per file for retries

    # --- Start the Producer (ffmpeg) ---
    ffmpeg_command = [
        "ffmpeg", "-i", M3U8_URL,
        "-c", "copy", "-f", "segment", "-segment_time", "300",
        "-reset_timestamps", "1", "-strftime", "1",
        os.path.join(CHUNK_DIR, "chunk_%Y-%m-%d_%H-%M-%S.ts")
    ]
    
    logging.info("Starting ffmpeg stream downloader in the background...")
    # Redirect stdout and stderr to DEVNULL to avoid I/O buffering issues
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # --- Start the Consumer (File Watcher) ---
    try:
        while True:
            # Check if ffmpeg is still running
            ffmpeg_return_code = ffmpeg_process.poll()
            if ffmpeg_return_code is not None:
                logging.error(f"ffmpeg process has terminated with exit code {ffmpeg_return_code}. Exiting main loop.")
                # You might want logic here to try restarting ffmpeg or notifying
                break

            # Find unprocessed .ts files in the chunk directory
            # Sort them to process in order of creation.
            chunk_files = sorted([f for f in os.listdir(CHUNK_DIR) if f.endswith('.ts')])
            
            ready_to_process = []
            for i, ts_filename in enumerate(chunk_files):
                ts_filepath = os.path.join(CHUNK_DIR, ts_filename)
                
                # Heuristic: Avoid processing the very last file (ffmpeg might still be writing to it)
                # And ensure it hasn't been fully processed already.
                is_potentially_ready = (i < len(chunk_files) - 1) and (ts_filename not in processed_files)
                
                if is_potentially_ready:
                    # Robust check: Check if file size is stable
                    try:
                        initial_size = os.path.getsize(ts_filepath)
                        time.sleep(1) # Wait a moment
                        current_size = os.path.getsize(ts_filepath)

                        if current_size == initial_size and current_size > 0: # Ensure not empty
                            ready_to_process.append(ts_filename)
                        else:
                            logging.debug(f"File {ts_filename} still growing or empty. Skipping for now.")
                    except FileNotFoundError:
                        logging.warning(f"File {ts_filename} not found during size check. Might have been moved or deleted.")
                        # If file disappeared, remove from tracked failures
                        failed_attempts.pop(ts_filename, None)
                        processed_files.add(ts_filename) # Mark as processed to stop future checks
                    except Exception as e:
                        logging.error(f"Error checking size of {ts_filename}: {e}")

            for ts_filename in ready_to_process:
                # If already processed or failed max attempts, skip
                if ts_filename in processed_files:
                    continue
                
                # Track attempts to prevent infinite retries on truly bad chunks
                failed_attempts[ts_filename] = failed_attempts.get(ts_filename, 0) + 1
                MAX_RETRIES = 3 
                if failed_attempts[ts_filename] > MAX_RETRIES:
                    logging.error(f"Chunk {ts_filename} failed after {MAX_RETRIES} attempts. Moving to {FAILED_DIR} and skipping.")
                    try:
                        shutil.move(os.path.join(CHUNK_DIR, ts_filename), os.path.join(FAILED_DIR, ts_filename))
                    except Exception as e:
                        logging.error(f"Could not move failed chunk {ts_filename} to {FAILED_DIR}: {e}")
                    processed_files.add(ts_filename) # Mark as processed (failed)
                    continue

                logging.info(f"\n--- Processing chunk: {ts_filename} (Attempt {failed_attempts[ts_filename]}) ---")
                ts_filepath = os.path.join(CHUNK_DIR, ts_filename)
                
                mp3_filepath = None
                srt_filepath = None

                try:
                    # 1. Convert to MP3
                    mp3_filepath = convert_to_mp3(ts_filepath)
                    if not mp3_filepath:
                        logging.warning(f"Skipping further processing for {ts_filename} due to MP3 conversion failure.")
                        # Don't mark as processed yet to allow retry
                        continue

                    # 2. Transcribe
                    srt_filepath = transcribe_audio(mp3_filepath)
                    if not srt_filepath:
                        logging.warning(f"Skipping further processing for {ts_filename} due to transcription failure.")
                        # Clean up the mp3 if transcription fails immediately
                        if os.path.exists(mp3_filepath): os.remove(mp3_filepath)
                        continue

                    # 3. Upload
                    if upload_files_sftp(mp3_filepath, srt_filepath):
                        # 4. Move successfully processed files for archival
                        logging.info(f"Moving processed files for {ts_filename} to {PROCESSED_DIR}")
                        try:
                            # Use shutil.move for robustness across filesystems
                            shutil.move(ts_filepath, os.path.join(PROCESSED_DIR, os.path.basename(ts_filepath)))
                            shutil.move(mp3_filepath, os.path.join(PROCESSED_DIR, os.path.basename(mp3_filepath)))
                            shutil.move(srt_filepath, os.path.join(PROCESSED_DIR, os.path.basename(srt_filepath)))
                            processed_files.add(ts_filename) # Mark as fully processed
                            failed_attempts.pop(ts_filename, None) # Clear successful attempt count
                        except Exception as e:
                            logging.error(f"Error moving files for {ts_filename} to {PROCESSED_DIR}: {e}", exc_info=True)
                            # If move fails, don't mark as processed to retry moving later
                    else:
                        logging.warning(f"Upload failed for {ts_filename}. It will be retried.")
                        # Don't mark as processed to allow retry
                except Exception as e:
                    logging.critical(f"Unhandled error during processing of {ts_filename}: {e}", exc_info=True)
                    # Clean up any intermediate files on unhandled error
                    if mp3_filepath and os.path.exists(mp3_filepath): os.remove(mp3_filepath)
                    if srt_filepath and os.path.exists(srt_filepath): os.remove(srt_filepath)
                    # Don't mark as processed to allow retry


            # Wait before checking for new files again
            time.sleep(10) # Adjust as needed

    except KeyboardInterrupt:
        logging.info("\nInterruption detected. Shutting down...")
    finally:
        # Ensure ffmpeg process is terminated when the script exits
        if ffmpeg_process.poll() is None:
            logging.info("Terminating ffmpeg process...")
            ffmpeg_process.terminate()
            ffmpeg_process.wait(timeout=10) # Give it some time to exit
            if ffmpeg_process.poll() is None: # Still alive?
                logging.warning("ffmpeg process did not terminate gracefully. Killing it.")
                ffmpeg_process.kill()
        logging.info("ffmpeg process ensured terminated. Script finished.")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(CHUNK_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FAILED_DIR, exist_ok=True)
    main()


