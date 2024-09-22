from TTS.api import TTS

def mozilla_tts(text, filename, model_name="tts_models/en/ljspeech/tacotron2-DDC", language=None):
    # Initialize TTS
    tts = TTS(model_name=model_name)
    
    # Generate speech
    tts.tts_to_file(text=text, file_path=filename, language=language)
    
    print(f"Speech saved to {filename}")

# Example usage
text = "Mozilla TTS provides high-quality speech synthesis using deep learning models."
mozilla_tts(text, "mozilla_tts_output.wav")