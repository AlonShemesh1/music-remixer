import os
import random
import librosa
import numpy as np
import soundfile as sf

def detect_chorus_intervals(y, sr):
    # ניתוח מבני למציאת הפזמון
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    boundaries = librosa.segment.agglomerative(chroma, k=4)
    boundaries = np.pad(boundaries, (0, 1), mode='constant', constant_values=len(chroma.T))
    segments = [(librosa.frames_to_time(boundaries[i], sr=sr),
                 librosa.frames_to_time(boundaries[i+1], sr=sr))
                for i in range(len(boundaries)-1)]

    chorus = max(segments, key=lambda x: x[1] - x[0])  # הקטע הארוך ביותר
    return [chorus]  # רשימה של פזמונים

def remix_audio(song_path, style, chorus_times):
    os.makedirs("output", exist_ok=True)

    y, sr = librosa.load(song_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    beat_folder = "beats"
    all_files = [f for f in os.listdir(beat_folder) if f.endswith(".wav") or f.endswith(".mp3")]

    style_lower = style.replace("-", "").replace(" ", "").lower()
    beat_files = [f for f in all_files if style_lower in f.replace("-", "").replace(" ", "").lower()]

    if len(beat_files) < 4:
        raise ValueError(f"You must have at least 4 loops for style '{style}' in the beats folder.")

    selected = random.sample(beat_files, 2)
    verse_loop, chorus_loop = [
        librosa.load(os.path.join(beat_folder, f), sr=sr)[0]
        for f in selected
    ]

    beat_track = np.zeros_like(y)

    for t in range(0, len(y), len(verse_loop)):
        beat_track[t:t+len(verse_loop)] += verse_loop[:min(len(verse_loop), len(y)-t)]

    for start, end in chorus_times:
        start_i = int(start * sr)
        end_i = int(end * sr)
        for t in range(start_i, end_i, len(chorus_loop)):
            beat_track[t:t+len(chorus_loop)] = chorus_loop[:min(len(chorus_loop), end_i - t)]

    combined = y + 0.5 * beat_track
    out_path = "output/remixed.wav"
    sf.write(out_path, combined.astype(np.float32), sr)

    return out_path

def get_volume_envelope(path):
    y, sr = librosa.load(path)
    hop_length = 512
    envelope = np.abs(librosa.stft(y, hop_length=hop_length)).mean(axis=0)
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return times, envelope
