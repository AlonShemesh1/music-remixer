# utils/audio_processor.py

from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import librosa
import streamlit as st
import tempfile

def load_audio(file):
    return AudioSegment.from_file(file)

def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")

def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    
    window_size = 1000
    remainder = len(samples) % window_size
    if remainder != 0:
        samples = np.pad(samples, (0, window_size - remainder), 'constant')

    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=len(envelope))

    fig, ax = plt.subplots()
    ax.plot(time, envelope)
    ax.set_title("Volume Envelope")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    st.pyplot(fig)

def detect_chorus(file_path):
    y, sr = librosa.load(file_path, sr=None)
    S = np.abs(librosa.stft(y))
    similarity = np.dot(S.T, S)
    chorus_start = np.argmax(similarity.sum(axis=0)) / sr
    chorus_duration = 15  # seconds
    return int(chorus_start * 1000), int(chorus_duration * 1000)

def apply_loops(song, main_loop_path, chorus_loop_path, chorus_start_ms, chorus_end_ms, loop_gain_db=0):
    main_loop = AudioSegment.from_file(main_loop_path) + loop_gain_db
    chorus_loop = AudioSegment.from_file(chorus_loop_path) + loop_gain_db

    chorus_duration = chorus_end_ms - chorus_start_ms

    main_loop = (main_loop * (len(song) // len(main_loop) + 1))[:len(song)]
    chorus_loop = (chorus_loop * (chorus_duration // len(chorus_loop) + 1))[:chorus_duration]

    remixed = song.overlay(main_loop)
    remixed = remixed.overlay(chorus_loop, position=chorus_start_ms)
    return remixed
