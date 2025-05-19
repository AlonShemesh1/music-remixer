import os
import librosa
import numpy as np
import soundfile as sf
import random

def detect_chorus_intervals(y, sr):
    # מחשבים תכונות כרומטיות
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    # מחלקים את השיר ל-4 קטעים ע"י Agglomerative Clustering
    boundaries = librosa.segment.agglomerative(chroma.T, k=4)
    boundaries = np.pad(boundaries, (0,1), mode='constant', constant_values=chroma.shape[1])

    segments = []
    for i in range(len(boundaries)-1):
        start = librosa.frames_to_time(boundaries[i], sr=sr)
        end = librosa.frames_to_time(boundaries[i+1], sr=sr)
        segments.append((start, end))

    # מחזירים את הקטע הארוך ביותר כ"פזמון"
    chorus = max(segments, key=lambda x: x[1]-x[0])
    return [chorus]


def remix_audio(song_path, style, chorus_times):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # תיקיית utils
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # תיקיית הפרויקט (מעל utils)
    beat_folder = os.path.join(ROOT_DIR, "beats", style)

    if not os.path.exists(beat_folder):
        raise FileNotFoundError(f"Directory {beat_folder} not found.")

    beat_files = [f for f in os.listdir(beat_folder) if f.endswith(".wav")]
    if len(beat_files) < 4:
        raise ValueError("You must have at least 4 loops per style")

    y, sr = librosa.load(song_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    selected = random.sample(beat_files, 2)
    verse_loop, chorus_loop = [librosa.load(os.path.join(beat_folder, f), sr=sr)[0] for f in selected]

    beat_track = np.zeros_like(y)
    for t in range(0, len(y), len(verse_loop)):
        beat_track[t:t+len(verse_loop)] += verse_loop[:min(len(verse_loop), len(y)-t)]

    for start, end in chorus_times:
        start_i = int(start * sr)
        end_i = int(end * sr)
        for t in range(start_i, end_i, len(chorus_loop)):
            beat_track[t:t+len(chorus_loop)] = chorus_loop[:min(len(chorus_loop), end_i - t)]

    combined = y + 0.5 * beat_track

    output_dir = os.path.join(ROOT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "remixed.wav")

    sf.write(out_path, combined.astype(np.float32), sr)
    return out_path


def get_volume_envelope(path):
    y, sr = librosa.load(path)
    hop_length = 512
    envelope = np.abs(librosa.stft(y, hop_length=hop_length)).mean(axis=0)
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return times, envelope
