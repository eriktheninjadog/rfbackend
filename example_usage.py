import os
from local_transcriber import RunPodWhisperClient

def transcribe_cantonese_files():
    """Example usage of the Cantonese transcription service"""
    
    # Initialize client
    api_key = os.getenv("RUNPOD_API_KEY")
    client = RunPodWhisperClient(api_key)
    
    try:
        # Create pod
        print("Creating RunPod instance...")
        client.create_pod()
        
        # List of Cantonese audio files to transcribe
        audio_files = [
            "capture_20250902_212311.wav",
            "capture_20250903_144732.wav",
            # Add more files as needed
        ]
        
        results = {}
        
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                print(f"\nProcessing: {audio_file}")
                try:
                    transcription = client.transcribe_audio(audio_file)
                    results[audio_file] = transcription
                    print(f"✓ Transcription completed: {transcription[:100]}...")
                except Exception as e:
                    print(f"✗ Error processing {audio_file}: {e}")
                    results[audio_file] = f"Error: {e}"
        
        # Save results
        with open("transcription_results.txt", "w", encoding="utf-8") as f:
            for file, result in results.items():
                f.write(f"File: {file}\n")
                f.write(f"Transcription: {result}\n")
                f.write("-" * 50 + "\n")
        
        print(f"\nAll transcriptions completed! Results saved to transcription_results.txt")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        print("Cleaning up...")
        client.terminate_pod()

if __name__ == "__main__":
    transcribe_cantonese_files()