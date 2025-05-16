import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import tempfile
import os
from pydub import AudioSegment
import streamlit as st

def get_volume_envelope(audio_path):
    y, sr = librosa.load(audio_path)
    frame_length = 2048
    hop_length = 512
    envelope = np.array([
        np.max(np.abs(y[i:i+frame_length]))
        for i in range(0, len(y), hop_length)
    ])
    return envelope, sr

def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = np.dot(chroma.T, chroma)
    lag = librosa.segment.recurrence_to_lag(similarity)
    boundaries = librosa.segment.agglomerative(similarity, k=4)
    durations = librosa.frames_to_time(boundaries, sr=sr)
    if len(durations) >= 2:
        return [(durations[1], durations[2])]
    else:
        return []

def remix_song_with_chorus_loop(song_path, main_loop_path, chorus_loop_path, chorus_intervals):
    original = AudioSegment.from_file(song_path)
    main_loop = AudioSegment.from_file(main_loop_path)
    chorus_loop = AudioSegment.from_file(chorus_loop_path)

    output = AudioSegment.silent(duration=0)
    cursor = 0

    for start_sec, end_sec in chorus_intervals:
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)

        # Add main loop until chorus
        segment = original[cursor:start_ms]
        looped = loop_audio(main_loop, len(segment))
        output += mix_loops(segment, looped)

        # Add chorus loop
        chorus_seg = original[start_ms:end_ms]
        chorus_looped = loop_audio(chorus_loop, len(chorus_seg))
        output += mix_loops(chorus_seg, chorus_looped)

        cursor = end_ms

    # Add remaining part
    if cursor < len(original):
        segment = original[cursor:]
        looped = loop_audio(main_loop, len(segment))
        output += mix_loops(segment, looped)

    output_path = os.path.join(tempfile.gettempdir(), "remixed_output.mp3")
    output.export(output_path, format="mp3")
    return output_path

def loop_audio(loop, duration_ms):
    looped = AudioSegment.silent(duration=0)
    while len(looped) < duration_ms:
        looped += loop
    return looped[:duration_ms]

def mix_loops(original, looped):
    return original.overlay(looped)

def plot_volume_envelope(envelope, sr, chorus_intervals, title="Volume Envelope"):
    fig, ax = plt.subplots(figsize=(10, 4))
    times = np.linspace(0, len(envelope) * 512 / sr, num=len(envelope))
    ax.plot(times, envelope, label="Volume", color="gray")

    for start, end in chorus_intervals:
        ax.axvspan(start, end, color='orange', alpha=0.4, label='Chorus')

    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.legend()
    st.pyplot(fig)
