#!/usr/bin/env python3
"""
System Audio Capture Tool for Ubuntu
Captures system audio (speaker output) in a rolling 5-minute buffer.
"""

import pyaudio
import wave
import threading
import queue
import time
import os
import sys
import requests
import subprocess
from datetime import datetime
import json
import webbrowser
import deepinfra

import generalcomsystem.client as generalcomsystem
# Configuration
CHANNELS = 2  # Stereo
RATE = 44100  # Sample rate
CHUNK = 1024  # Audio frames per buffer
ROLLING_WINDOW_SECONDS = 300  # 5 minutes
BUFFER_SIZE = int(RATE / CHUNK * ROLLING_WINDOW_SECONDS)
DEFAULT_LANGUAGE = "zh"  # Cantonese/Mandarin language code

class SystemAudioCapture:
    def __init__(self, source_name=None):
        self.buffer = queue.Queue(maxsize=BUFFER_SIZE)
        self.running = True
        self.last_saved_file = None
        self.process = None
        
        if source_name:
            self.source_name = source_name
        else:
            self.source_name = self._select_monitor_source()
            
        if not self.source_name:
            raise Exception("No PulseAudio monitor source selected")
            
        # Start audio capture using parec
        self.capture_thread = threading.Thread(target=self.capture_audio)
        self.capture_thread.start()

    def _list_sources(self):
        """List all available audio sources"""
        try:
            result = subprocess.run(['pactl', 'list', 'sources'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def _get_monitor_sources(self):
        """Get list of available monitor sources"""
        try:
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                  capture_output=True, text=True, check=True)
            
            monitors = []
            for line in result.stdout.split('\n'):
                if '.monitor' in line:
                    source_name = line.split()[1]
                    monitors.append(source_name)
            
            return monitors
        except subprocess.CalledProcessError:
            return []

    def _select_monitor_source(self):
        """Help user select the correct monitor source"""
        print("Detecting audio sources...")
        monitors = self._get_monitor_sources()
        
        if not monitors:
            print("No monitor sources found!")
            print("Make sure PulseAudio is running:")
            print("  pulseaudio --check -v || pulseaudio --start")
            return None
            
        print(f"\nFound {len(monitors)} monitor source(s):")
        for i, source in enumerate(monitors, 1):
            print(f"  {i}. {source}")
            
        # Try to identify the most likely correct source
        default_sink = None
        try:
            result = subprocess.run(['pactl', 'get-default-sink'], 
                                  capture_output=True, text=True, check=True)
            default_sink = result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
            
        recommended = None
        if default_sink:
            for i, source in enumerate(monitors):
                if default_sink + '.monitor' in source:
                    recommended = i
                    break
                    
        print()
        if recommended is not None:
            print(f"Recommended: {recommended + 1} ({monitors[recommended]})")
            choice = input(f"Select source (1-{len(monitors)}) [Enter for recommended]: ").strip()
            if choice == "":
                return monitors[recommended]
        else:
            choice = input(f"Select source (1-{len(monitors)}): ").strip()
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(monitors):
                return monitors[index]
        except ValueError:
            pass
            
        print("Invalid selection, using first monitor source")
        return monitors[0]

    def capture_audio(self):
        """Continuously capture system audio using parec"""
        try:
            # Use parec to capture system audio
            cmd = [
                'parec',
                '-d', self.source_name,  # Device to record from
                '--raw',                 # Raw format (no headers)
                '--format=s16le',        # 16-bit little endian
                '--channels=2',          # Stereo
                '--rate=44100',          # Sample rate
                '--latency-msec=50'
            ]
            
            print(f"Capturing system audio from: {self.source_name}")
            
            # Start parec process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=CHUNK * 4  # Buffer size
            )
            
            # Read audio data from parec
            bytes_per_chunk = CHUNK * 4  # 2 channels * 2 bytes per sample
            while self.running and self.process.poll() is None:
                try:
                    # Read raw audio data
                    data = self.process.stdout.read(bytes_per_chunk)
                    if data and len(data) == bytes_per_chunk:
                        if not self.buffer.full():
                            self.buffer.put(data)
                        else:
                            # Remove oldest chunk to maintain rolling window
                            self.buffer.get()
                            self.buffer.put(data)
                except Exception as e:
                    if self.running:
                        time.sleep(0.01)
                        
        except Exception as e:
            print(f"Failed to initialize audio capture: {e}")
            self.running = False



    def purge(self):
        """Purge the current audio buffer - """
        try:
            
            # Create a new empty buffer
            old_size = self.buffer.qsize()
            with self.buffer.mutex:
                self.buffer.queue.clear()
            print(f"Buffer purged. Cleared {old_size} audio chunks.")
            return True
        except Exception as e:
            print(f"Error purging buffer: {e}")
            return False

    def stop_capture(self):
        """Stop audio capture and cleanup"""
        self.running = False
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)

    def save_current_buffer(self, filename=None):
        """Save current rolling buffer to WAV file"""
        if filename is None:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.wav"
            
        try:
            # Get current buffer contents
            temp_buffer = list(self.buffer.queue)
            
            # Create WAV file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(RATE)
                wf.writeframes(b''.join(temp_buffer))
                
            self.last_saved_file = filename
            print(f"Saved {len(temp_buffer)} chunks ({len(b''.join(temp_buffer))} bytes) to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving buffer: {e}")
            return None

    def replay_audio(self, filename=None):
        """Play back a saved audio file"""
        if filename is None:
            filename = self.last_saved_file
            if filename is None:
                print("No saved file to replay. Use 'save' command first or specify a filename.")
                return
                
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return
            
        try:
            with wave.open(filename, 'rb') as wf:
                # Initialize PyAudio for playback
                play_audio = pyaudio.PyAudio()
                stream = play_audio.open(
                    format=play_audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                print(f"Replaying {filename}...")
                data = wf.readframes(CHUNK)
                while data:
                    stream.write(data)
                    data = wf.readframes(CHUNK)
                    
                stream.stop_stream()
                stream.close()
                play_audio.terminate()
                print("Playback finished")
                
        except Exception as e:
            print(f"Error during playback: {e}")

    def send_audio(self, url, filename=None):
        """Send audio file to remote server"""
        if filename is None:
            filename = self.last_saved_file
            if filename is None:
                print("No saved file to send. Use 'save' command first or specify a filename.")
                return
                
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return
            
        try:
            with open(filename, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, files=files, timeout=30)
                
            print(f"Sent {filename} to {url}")
            print(f"Response status: {response.status_code}")
            if response.text:
                print(f"Response body: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Network error sending file: {e}")
        except Exception as e:
            print(f"Error sending file: {e}")

    def transcribe_audio(self, filename=None, language=DEFAULT_LANGUAGE):
                
        """Transcribe audio file using DeepInfra Whisper API and open result in Chrome"""
        if filename is None:
            filename = self.last_saved_file
            if filename is None:
                print("No saved file to transcribe. Use 'save' command first or specify a filename.")
                return
                
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return
            
        try:
            transcripts = deepinfra.transcribe_audio(filename)
            transcription = ''
            for t in transcripts:
                transcription = transcription +t['text']   
        except Exception as e:
            transcription = f"Error during transcription: {e}"
        html_filename = filename.replace('.wav', '_transcription.html')
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Transcription - {os.path.basename(filename)}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .transcription {{ margin-top: 20px; padding: 20px; background-color: #f9f9f9; 
                                    white-space: pre-wrap; word-wrap: break-word; }}
                .filename {{ font-weight: bold; color: #333; }}
                .language {{ color: #666; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Audio Transcription</h1>
                <p class="filename">File: {os.path.basename(filename)}</p>
                <p class="language">Language: {language or 'auto-detected'}</p>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div class="transcription">
                <h2>Transcription:</h2>
                <p>{transcription}</p>
            </div>
        </body>
        </html>
        """
            
        with open(html_filename, 'w') as f:
            f.write(html_content)
        
        print(f"Transcription saved to {html_filename}")
            
            # Try to open in Chrome
        try:
            webbrowser.get('google-chrome').open(f'file://{os.path.abspath(html_filename)}')
            print("Opened transcription in Chrome")
        except:
            # Fallback to default browser
            webbrowser.open(f'file://{os.path.abspath(html_filename)}')
            print("Opened transcription in default browser")
            
        return html_filename

def check_dependencies():
    """Check if required tools are installed"""
    try:
        subprocess.run(['parec', '--version'], 
                      capture_output=True, check=True)
        print("PulseAudio tools found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PulseAudio tools not found")
        print("Install with: sudo apt-get install pulseaudio-utils")
        return False

def test_source(source_name):
    """Test if a source is working by recording a short sample"""
    print(f"Testing source: {source_name}")
    try:
        cmd = [
            'parec',
            '-d', source_name,
            '--file-format=wav',
            '--channels=2',
            '--rate=44100',
            '-v',  # Verbose
            'test_source.wav'
        ]
        
        print("Recording 5 seconds of audio...")
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        time.sleep(5)
        process.terminate()
        
        if os.path.exists('test_source.wav') and os.path.getsize('test_source.wav') > 0:
            print("✓ Source test successful - audio file created")
            os.remove('test_source.wav')
            return True
        else:
            print("✗ Source test failed - no audio recorded")
            return False
    except Exception as e:
        print(f"✗ Source test failed: {e}")
        return False
        def cmd_help():
            """Show available commands"""
            print("\nSystem audio capture commands:")
            print("  save [filename]              - Save current 5-minute buffer (default filename if none provided)")
            print("  replay [filename]            - Replay saved audio file (default: last saved file)")
            print("  send [filename] <url>        - Send audio file to server (default: last saved file)")
            print("  transcribe [filename] [lang] - Transcribe audio")
            print("  purge                        - Clear the current audio buffer")
            print("  quit                         - Exit program")
            print("-" * 50)


last_sent = None


def on_text_msg(msg_type, content):
        print(f"Text message [{msg_type}]: {content}")
    
def on_file_received(filename, content):
    print(f"File received: {filename} ({len(content)} bytes)")
    with open(f"received_{filename}", 'wb') as f:
        f.write(content)
    with open(last_sent+".srt", 'wb') as f:
        f.write(content)
    subprocess.run(['scp', last_sent+".srt", 'erik@chinese.eriktamm.com:/var/www/html/mp3/'], check=True, capture_output=True)
                               
    
def on_connected():
    print("Connected to server!")

def on_disconnected():
    print("Disconnected from server!")
    

def main():
    global last_sent
    print("System Audio Capture Tool for Ubuntu")
    print("=" * 40)
    
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Capture system audio')
    parser.add_argument('--source', help='Specify monitor source name directly')
    parser.add_argument('--test', action='store_true', help='Test a specific source')
    parser.add_argument('--language', default=DEFAULT_LANGUAGE, 
                       help=f'Language for transcription (default: {DEFAULT_LANGUAGE})')
    args = parser.parse_args()
    
    if args.test and args.source:
        test_source(args.source)
        return
    
    print("Initializing system audio capture...")
    
    try:
        capture = SystemAudioCapture(args.source)
        print("\nSystem audio capture started. Commands:")
        print("  save [filename]              - Save current 5-minute buffer (default filename if none provided)")
        print("  replay [filename]            - Replay saved audio file (default: last saved file)")
        print("  send [filename] <url>        - Send audio file to server (default: last saved file)")
        print(f"  transcribe [filename] [lang] - Transcribe audio (default lang: {args.language})")
        print("  quit                         - Exit program")
        print("-" * 50)
    except Exception as e:
        print(f"Failed to start audio capture: {e}")
        return
    try:
        client = generalcomsystem.MessageClient("chinese.eriktamm.com", 8888)
        client.set_text_message_callback(on_text_msg)
        client.set_file_received_callback(on_file_received)
        client.set_connection_callbacks(on_connected, on_disconnected)
        client.connect()
        while True:
            try:
                    command_input = input("\nEnter command: ").strip()
                    if not command_input:
                        continue
                        
                    command_parts = command_input.split()
                    command = command_parts[0].lower()
                    
                    if command == 'quit':
                        break
                    elif command == 'save':
                        if len(command_parts) >= 2:
                            filename = command_parts[1]
                            capture.save_current_buffer(filename)
                        else:
                            capture.save_current_buffer()  # Use default filename
                    elif command == 'replay':
                        if len(command_parts) >= 2:
                            capture.replay_audio(command_parts[1])
                        else:
                            capture.replay_audio()  # Use last saved file
                    elif command == 'send':
                        if len(command_parts) >= 3:
                            filename = command_parts[1]
                            url = command_parts[2]
                            capture.send_audio(url, filename)
                        elif len(command_parts) >= 2:
                            url = command_parts[1]
                            capture.send_audio(url)  # Use last saved file
                        else:
                            print("Usage: send [filename] <url>")
                    elif command == 'purge':
                        capture.purge()  # Clear the current audio buffer
                    elif command == 'remotetranscribe':
                        #capture.purge()  # Clear the current audio buffer
                        # Save current buffer if not saved already
                        if not capture.last_saved_file:
                            capture.save_current_buffer()

                        if capture.last_saved_file:
                            # Generate MP3 filename
                            mp3_filename = capture.last_saved_file.replace('.wav', '.mp3')
                            
                            print(f"Converting {capture.last_saved_file} to MP3...")
                            try:
                                # Use ffmpeg to convert WAV to MP3
                                subprocess.run([
                                    'ffmpeg', 
                                    '-i', capture.last_saved_file, 
                                    '-codec:a', 'libmp3lame', 
                                    '-ar','16000',  # Set sample rate to 16kHz
                                    '-qscale:a', '2',  # High quality, adjust if needed
                                    '-y',  # Overwrite output file if it exists
                                    mp3_filename
                                ], check=True, capture_output=True)
                                
                                print(f"Conversion successful: {mp3_filename}")
                                subprocess.run([
                                    'scp', 
                                    mp3_filename, 'erik@chinese.eriktamm.com:/var/www/html/mp3/'
                                ], check=True, capture_output=True)
                                print(f"Uploaded: {mp3_filename}")                                
                                # Send the MP3 file instead of WAV
                                print(f"Sending: {mp3_filename} to relay server")                                
                                client.send_file(mp3_filename)
                                print(f"Sent: {mp3_filename} to relay server")                                
                                last_sent = mp3_filename
                                
                            except subprocess.CalledProcessError as e:
                                print(f"Error converting to MP3: {e}")
                                print(f"Sending original WAV file instead")
                                client.send_file(capture.last_saved_file)
                            except Exception as e:
                                print(f"Error: {e}")
                        #client.send_file(capture.last_saved_file)
                    elif command == 'transcribe':
                        # Parse language parameter
                        language = args.language  # Default language
                        filename = None
                        
                        # Handle different parameter combinations
                        if len(command_parts) >= 3:
                            filename = command_parts[1]
                            language = command_parts[2]
                        elif len(command_parts) == 2:
                            # Check if second parameter is a language code or filename
                            param = command_parts[1]
                            if len(param) == 2 and param.isalpha():
                                language = param  # It's a language code
                            else:
                                filename = param  # It's a filename
                        
                        capture.transcribe_audio(filename, language)
                    else:
                        print("Invalid command. Use:")
                        print("  save [filename]")
                        print("  replay [filename]")
                        print("  send [filename] <url>")
                        print("  purge")
                        print(f"  transcribe [filename] [lang]  (default lang: {args.language})")
                        print("  quit")
            except KeyboardInterrupt:
                print("\nReceived interrupt, shutting down...")
                break
            except EOFError:
                print("\nEOF received, shutting down...")
                break
            except Exception as e:
                print(f"Command error: {e}")
                
    finally:
        print("Stopping audio capture...")
        capture.stop_capture()
        print("Audio capture stopped")

if __name__ == "__main__":
    main()
    
    
    
    