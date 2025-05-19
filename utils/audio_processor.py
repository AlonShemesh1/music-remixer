import librosa
import numpy as np
import soundfile as sf
import random
import os

def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    # Use enhanced similarity matrix manually (instead of librosa.segment.path_enhance)
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
    base_loop = f'beats/{style}_loop_{random.randint(1, 4)}.mp3'
    chorus_loop = f'beats/{style}_loop_{random.randint(1, 4)}.mp3'

    base_loop_audio, _ = librosa.load(base_loop, sr=sr)
    chorus_loop_audio, _ = librosa.load(chorus_loop, sr=sr)

    loop_duration = librosa.get_duration(y=base_loop_audio, sr=sr)

    # Build new remix
    new_audio = np.zeros_like(y)

    for i in range(0, len(y), len(base_loop_audio)):
        new_audio[i:i+len(base_loop_audio)] = base_loop_audio[:min(len(base_loop_audio), len(y)-i)]

    for start, end in chorus_segments:
        s = int(start * sr)
        e = int(end * sr)
        seg_len = e - s
        chorus_audio = np.tile(chorus_loop_audio, int(np.ceil(seg_len / len(chorus_loop_audio))))
        new_audio[s:e] = chorus_audio[:seg_len]

    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)

    out_path = "output/remixed.wav"
    sf.write(out_path, new_audio, sr, format='WAV')  # explicitly define format
    return out_path

