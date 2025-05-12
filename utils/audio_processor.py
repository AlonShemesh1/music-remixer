from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import librosa
import io


def load_audio(file):
    return AudioSegment.from_file(file)


def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")


def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())

    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

    window_size = 1000
    if len(samples) < window_size:
        st.warning("Audio too short for volume analysis.")
        return

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


def detect_chorus_segments(audio):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

    window_size = 1000
    if len(samples) < window_size * 2:
        return []

    remainder = len(samples) % window_size
    if remainder != 0:
        samples = np.pad(samples, (0, window_size - remainder), 'constant')

    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)

    threshold = envelope.mean() + envelope.std()
    chorus_indices = np.where(envelope > threshold)[0]

    chorus_segments = []
    for idx in chorus_indices:
        start = int((idx * window_size) / audio.frame_rate * 1000)
        end = start + 4000  # 4 seconds chorus
        if end > len(audio):
            end = len(audio)
        chorus_segments.append((start, end))

    return chorus_segments


def apply_loops_with_chorus(audio, main_loop_path, chorus_loop_path, loop_gain_db=0):
    main_loop = AudioSegment.from_file(main_loop_path) + loop_gain_db
    chorus_loop = AudioSegment.from_file(chorus_loop_path) + loop_gain_db

    chorus_segments = detect_chorus_segments(audio)

    remixed = AudioSegment.silent(duration=0)
    last_index = 0

    for start, end in chorus_segments:
        verse_part = audio[last_index:start]
        chorus_part = audio[start:end]

        looped_main = (main_loop * (len(verse_part) // len(main_loop) + 1))[:len(verse_part)]
        looped_chorus = (chorus_loop * (len(chorus_part) // len(chorus_loop) + 1))[:len(chorus_part)]

        remixed += verse_part.overlay(looped_main)
        remixed += chorus_part.overlay(looped_chorus)
        last_index = end

    if last_index < len(audio):
        remaining = audio[last_index:]
        looped_main = (main_loop * (len(remaining) // len(main_loop) + 1))[:len(remaining)]
        remixed += remaining.overlay(looped_main)

    return remixed
