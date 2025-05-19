import librosa
import numpy as np
import soundfile as sf
import random
import os

def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    similarity_enhanced = similarity.copy()
    boundaries = librosa.segment.agglomerative(similarity_enhanced, k=4)
    intervals = librosa.frames_to_time(boundaries, sr=sr)
    return [(intervals[i], intervals[i+1]) for i in range(len(intervals)-1)]

def compute_volume_envelope(audio_path):
    y, sr = librosa.load(audio_path, mono=True)
    hop_length = 512
    envelope = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return times, envelope

def remix_audio(song_path, style, chorus_segments):
    y, sr = librosa.load(song_path, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    # Select random loops
    chorus_loop = f'beats/{style}_loop_{random.randint(1, 4)}.mp3'
    chorus_loop_audio, _ = librosa.load(chorus_loop, sr=sr)

    # Start with the original song
    new_audio = y.copy()

    # Replace chorus sections with loop
    for start, end in chorus_segments:
        s = int(start * sr)
        e = int(end * sr)
        seg_len = e - s
        chorus_audio = np.tile(chorus_loop_audio, int(np.ceil(seg_len / len(chorus_loop_audio))))
        new_audio[s:e] = chorus_audio[:seg_len]

    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)

    out_path = "output/remixed.wav"
    sf.write(out_path, new_audio, sr, format='WAV')
    return out_path


def compute_volume_envelope_from_array(audio_array, sr):
    hop_length = 512
    envelope = librosa.feature.rms(y=audio_array, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return times, envelope
