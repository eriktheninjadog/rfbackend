from pydub import AudioSegment
import webrtcvad
import collections

# Function to split audio into frames
def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * frame_duration_ms / 1000.0) * 2
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n <= len(audio.raw_data):
        yield audio.raw_data[offset:offset + n]
        timestamp += duration
        offset += n

# Function to collect voiced frames
def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []

    for frame in frames:
        is_speech = vad.is_speech(frame, sample_rate)
        if not triggered:
            ring_buffer.append(frame)
            if sum([vad.is_speech(f, sample_rate) for f in ring_buffer]) > 0.9 * num_padding_frames:
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            if sum([not vad.is_speech(f, sample_rate) for f in ring_buffer]) > 0.9 * num_padding_frames:
                triggered = False
                yield b''.join(voiced_frames)
                ring_buffer.clear()
                voiced_frames = []

    if voiced_frames:
        yield b''.join(voiced_frames)

# Load and preprocess the audio file
audio = AudioSegment.from_mp3('/home/erik/Downloads/test2.mp3')
audio = audio.set_frame_rate(16000).set_channels(1)
sample_rate = audio.frame_rate

vad = webrtcvad.Vad(3)  # Aggressiveness levels 0-3
frames = frame_generator(30, audio, sample_rate)
segments = vad_collector(sample_rate, 30, 300, vad, frames)

# Reconstruct audio from voiced frames
voiced_audio = b''.join(segments)
output_audio = AudioSegment(
    data=voiced_audio,
    sample_width=audio.sample_width,
    frame_rate=sample_rate,
    channels=1
)

# Export the result
output_audio.export('output.mp3', format='mp3')
