# utils/audio_processor.py
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import streamlit as st

def load_audio(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    return y

def save_audio(y, path, sr=22050):
    sf.write(path, y, sr)

def get_chorus_intervals(path, sr=22050, k=4):
    y, _ = librosa.load(path, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    boundaries = librosa.segment.agglomerative(chroma, k=k)
    times = librosa.frames_to_time(boundaries, sr=sr)
    chorus_times = [(times[i], times[i+1]) for i in range(0, len(times)-1, 2)]
    return chorus_times

def plot_volume_envelope(y, sr=22050):
    frame_size = 1024
    hop_size = 512
    envelope = np.array([np.max(np.abs(y[i:i+frame_size])) for i in range(0, len(y), hop_size)])
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_size)
    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label="Volume Envelope")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Volume Envelope")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()

def get_bpm(path):
    y, sr = librosa.load(path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)

def mix_with_chorus_loop(song, main_loop_path, chorus_loop_path, chorus_times, bpm, volume_db, sr=22050):
    song_length = len(song)
    output = np.zeros_like(song)

    loop_main, _ = librosa.load(main_loop_path, sr=sr)
    loop_chorus, _ = librosa.load(chorus_loop_path, sr=sr)

    gain = 10 ** (volume_db / 20)
    loop_main *= gain
    loop_chorus *= gain

    beat_duration = 60 / bpm
    samples_per_beat = int(beat_duration * sr)

    chorus_samples = [(int(start * sr), int(end * sr)) for start, end in chorus_times]

    i = 0
    while i < song_length:
        in_chorus = any(start <= i < end for start, end in chorus_samples)
        loop = loop_chorus if in_chorus else loop_main
        end = min(i + len(loop), song_length)
        output[i:end] += loop[:end-i]
        i += samples_per_beat

    mixed = song + output
    return mixed
