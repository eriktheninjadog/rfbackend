import wave
import webrtcvad
import scipy

def remove_nonspeech_parts(input_file, output_file, aggressive_level=1):
    # Load the audio file
    with wave.open(input_file, 'r') as wav:
        params = wav.getparams()
        frames = wav.readframes(wav.getnframes())

    # Initialize the VAD
    vad = webrtcvad.Vad(aggressive_level)

    # Detect speech segments
    speech_segments = []
    sample_rate = params.framerate
    frame_duration_ms = 10  # 10ms per frame
    frame_size = int(sample_rate * (frame_duration_ms / 1000))  # Number of samples per frame

    start = None
    for i in range(0, len(frames), frame_size):
        frame = frames[i:i + frame_size]
        
        is_speech = vad.is_speech(frame, sample_rate)
        if is_speech and start is None:
            start = i
        elif not is_speech and start is not None:
            end = i
            speech_segments.append((start, end))
            start = None

    # Extract the speech segments
    speech_frames = b''.join(frames[start:end] for start, end in speech_segments)

    # Save the processed audio
    with wave.open(output_file, 'w') as wav:
        wav.setparams(params)
        wav.writeframes(speech_frames)

# Example usage
if __name__ == "__main__":
    remove_nonspeech_parts('/home/erik/Downloads/paddington.wav', '/home/erik/Downloads/paddington-voice.wav')