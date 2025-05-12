# utils/audio_processor.py
from pydub import AudioSegment
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import librosa

def load_audio(file):
    return AudioSegment.from_file(file)

def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")

def detect_chorus(file_path):
    y, sr = librosa.load(file_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = np.dot(chroma.T, chroma)

    chorus_start = 0
    chorus_end = 0
    max_score = 0

    for i in range(similarity.shape[0] - 50):
        for j in range(i + 30, similarity.shape[1] - 50):
            score = np.sum(similarity[i:i + 50, j:j + 50])
            if score > max_score:
                max_score = score
                chorus_start = i
                chorus_end = i + 50

    start_ms = int(librosa.frames_to_time(chorus_start, sr=sr) * 1000)
    end_ms = int(librosa.frames_to_time(chorus_end, sr=sr) * 1000)
    return start_ms, end_ms

def mix_with_loops(song, main_loop_path, chorus_loop_path, chorus_start, chorus_end, loop_gain_db=0):
    main_loop = AudioSegment.from_file(main_loop_path) + loop_gain_db
    chorus_loop = AudioSegment.from_file(chorus_loop_path) + loop_gain_db

    before_chorus = song[:chorus_start]
    chorus = song[chorus_start:chorus_end]
    after_chorus = song[chorus_end:]

    main_looped_before = (main_loop * (len(before_chorus) // len(main_loop) + 1))[:len(before_chorus)]
    chorus_looped = (chorus_loop * (len(chorus) // len(chorus_loop) + 1))[:len(chorus)]
    main_looped_after = (main_loop * (len(after_chorus) // len(main_loop) + 1))[:len(after_chorus)]

    mixed = before_chorus.overlay(main_looped_before) + \
            chorus.overlay(chorus_looped) + \
            after_chorus.overlay(main_looped_after)

    return mixed

def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    window_size = 1000
    remainder = len(samples) % window_size
    if remainder != 0:
        padding = window_size - remainder
        samples = np.pad(samples, (0, padding), 'constant')

    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=len(envelope))

    fig, ax = plt.subplots()
    ax.plot(time, envelope)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title("Volume Envelope")
    st.pyplot(fig)
