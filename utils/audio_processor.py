import librosa
import numpy as np
import soundfile as sf
import os
import random

def detect_chorus_intervals(y, sr):
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    recurrence = librosa.segment.recurrence_matrix(chroma, mode='affinity', sym=True)

    # נשתמש בלפלסיאן ישירות בלי matrix_filter
    laplacian = librosa.segment.linalg.laplacian(recurrence, norm=True)

    _, segments = librosa.segment.agglomerative(laplacian, k=4)
    segments = np.pad(segments, (0, 1), mode='constant', constant_values=chroma.shape[1])
    times = librosa.frames_to_time(segments, sr=sr)
    intervals = [(times[i], times[i + 1]) for i in range(len(times) - 1)]

    # נניח שהחלק הארוך ביותר הוא הפזמון
    chorus = max(intervals, key=lambda x: x[1] - x[0])
    return [chorus]

def remix_audio(song_path, style, chorus_times):
    os.makedirs("output", exist_ok=True)

    y, sr = librosa.load(song_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    beat_folder = "beats"
    beat_files = [f for f in os.listdir(beat_folder)
                  if f.lower().startswith(style.lower()) and f.endswith(".mp3")]
    if len(beat_files) < 2:
        raise ValueError(f"You must have at least 2 MP3 loops for style '{style}' in the 'beats' folder.")

    selected = random.sample(beat_files, 2)
    verse_loop_path = os.path.join(beat_folder, selected[0])
    chorus_loop_path = os.path.join(beat_folder, selected[1])

    # Load loops
    verse_loop, _ = librosa.load(verse_loop_path, sr=sr)
    chorus_loop, _ = librosa.load(chorus_loop_path, sr=sr)

    beat_track = np.zeros_like(y)
    for t in range(0, len(y), len(verse_loop)):
        beat_track[t:t + len(verse_loop)] += verse_loop[:min(len(verse_loop), len(y) - t)]

    for start, end in chorus_times:
        start_i = int(start * sr)
        end_i = int(end * sr)
        for t in range(start_i, end_i, len(chorus_loop)):
            beat_track[t:t + len(chorus_loop)] = chorus_loop[:min(len(chorus_loop), end_i - t)]

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
