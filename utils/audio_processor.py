# utils/audio_processor.py
from pydub import AudioSegment
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import librosa


def load_audio(file):
    return AudioSegment.from_file(file)


def mix_with_beat(song, beat_path, loop_gain_db=0):
    beat = AudioSegment.from_file(beat_path)
    beat = beat + loop_gain_db  # Adjust loop volume
    looped_beat = beat * (len(song) // len(beat) + 1)
    looped_beat = looped_beat[:len(song)]
    mixed = song.overlay(looped_beat)
    return mixed


def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")


def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

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


def get_bpm(file):
    y, sr = librosa.load(file, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)


def plot_waveform(file):
    y, sr = librosa.load(file, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    time = np.linspace(0, duration, num=len(y))

    fig, ax = plt.subplots()
    ax.plot(time, y, linewidth=0.5)
    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")

    st.pyplot(fig)
