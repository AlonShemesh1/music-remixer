from pydub import AudioSegment
import numpy as np
import librosa
import matplotlib.pyplot as plt
import streamlit as st
import io

def load_audio(file):
    return AudioSegment.from_file(file)

def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")

def get_chorus_intervals(file_path, sr=22050):
    y, _ = librosa.load(file_path, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    segments = librosa.segment.agglomerative(similarity, 2)  # 2 segments: verse/chorus
    boundaries = librosa.segment.boundaries(segments)
    times = librosa.frames_to_time(boundaries, sr=sr)
    return times.tolist()

def insert_loops(song, main_loop, chorus_loop, chorus_times):
    combined = AudioSegment.silent(duration=0)
    current_ms = 0
    for start_time in chorus_times:
        start_ms = int(start_time * 1000)
        if start_ms > current_ms:
            verse_part = song[current_ms:start_ms]
            looped_main = loop_audio_to_match(verse_part, main_loop)
            combined += looped_main.overlay(verse_part)
            current_ms = start_ms

    if current_ms < len(song):
        chorus_part = song[current_ms:]
        looped_chorus = loop_audio_to_match(chorus_part, chorus_loop)
        combined += looped_chorus.overlay(chorus_part)

    return combined

def loop_audio_to_match(segment, loop):
    looped = loop * (len(segment) // len(loop) + 1)
    return looped[:len(segment)]

def plot_volume_envelope(audio, title="Volume Envelope"):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    window_size = 1000
    padded_length = len(samples) + (-len(samples) % window_size)
    samples = np.pad(samples, (0, padded_length - len(samples)), mode='constant')

    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=len(envelope))

    fig, ax = plt.subplots()
    ax.plot(time, envelope)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title(title)
    st.pyplot(fig)
