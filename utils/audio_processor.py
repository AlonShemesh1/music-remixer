import librosa
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import soundfile as sf
import os

def get_volume_envelope(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    hop_length = 512
    envelope = np.abs(librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length))
    return envelope

def get_chorus_intervals(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    if len(beats) < 2:
        return []  # אם אין מספיק ביטים

    # חיתוך לאזור הביטים
    y_sync = librosa.util.sync(y, beats, aggregate=np.median)
    segments = librosa.segment.agglomerative(y_sync, k=4)

    # ודא שאורך הסגמנטים תואם לביטים
    segments = segments[:len(beats)]

    # מצא את הקלאסטר שמופיע הכי הרבה
    chorus_cluster = np.argmax(np.bincount(segments))
    beat_times = librosa.frames_to_time(beats, sr=sr)

    chorus_times = [
        (beat_times[i], beat_times[i+1])
        for i in range(len(beat_times)-1)
        if i < len(segments) and segments[i] == chorus_cluster
    ]
    return chorus_times


def plot_envelope_with_chorus(envelope, sr, chorus_times, title="Envelope"):
    fig, ax = plt.subplots(figsize=(12, 3))
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=512)
    ax.plot(times, envelope, color='white', label="Volume Envelope")
    for start, end in chorus_times:
        ax.axvspan(start, end, color='magenta', alpha=0.3)
    ax.set_title(title, color='white')
    ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white')
    ax.tick_params(colors='white')
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    st.pyplot(fig)

def process_audio(song_path, style, chorus_times, sr=22050):
    y, _ = librosa.load(song_path, sr=sr)

    loop_dir = "loops"
    loop_main_path = os.path.join(loop_dir, f"{style.lower()}_main.mp3")
    loop_chorus_path = os.path.join(loop_dir, f"{style.lower()}_chorus.mp3")

    loop_main, _ = librosa.load(loop_main_path, sr=sr)
    loop_chorus, _ = librosa.load(loop_chorus_path, sr=sr)

    output = np.zeros_like(y)
    segment_length = len(loop_main)

    for i in range(0, len(y), segment_length):
        segment_start = i
        segment_end = min(i + segment_length, len(y))
        segment_time = segment_start / sr

        is_chorus = any(start <= segment_time <= end for start, end in chorus_times)
        loop = loop_chorus if is_chorus else loop_main

        loop_trimmed = loop[:segment_end - segment_start]
        output[segment_start:segment_end] = y[segment_start:segment_end] + loop_trimmed

    output = output / np.max(np.abs(output))
    out_path = f"output/remixed_{os.path.basename(song_path)}"
    os.makedirs("output", exist_ok=True)
    sf.write(out_path, output, sr)

    envelope = get_volume_envelope(out_path, sr)
    return out_path, envelope
