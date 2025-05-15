from pydub import AudioSegment
import numpy as np
import librosa
import matplotlib.pyplot as plt
import streamlit as st
import io


def load_audio(file_path):
    return AudioSegment.from_file(file_path)


def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")


def detect_chorus_intervals(file_path):
    y, sr = librosa.load(file_path)
    oenv = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    seg = librosa.segment.agglomerative(chroma, k=4)
    bounds = librosa.segment.boundaries(seg)
    times = librosa.frames_to_time(bounds, sr=sr)

    chorus_start = float(times[1]) if len(times) > 2 else float(times[0])
    chorus_end = float(times[2]) if len(times) > 2 else chorus_start + 15.0
    return [(chorus_start, chorus_end)]


def mix_with_beats_and_chorus(song, main_loop_path, chorus_loop_path, chorus_times, loop_gain_db=0):
    main_loop = AudioSegment.from_file(main_loop_path) + loop_gain_db
    chorus_loop = AudioSegment.from_file(chorus_loop_path) + loop_gain_db

    output = AudioSegment.silent(duration=0)
    current = 0

    for (start_sec, end_sec) in chorus_times:
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)

        verse = song[current:start_ms]
        chorus = song[start_ms:end_ms]

        verse_loop = (main_loop * (len(verse) // len(main_loop) + 1))[:len(verse)]
        chorus_looped = (chorus_loop * (len(chorus) // len(chorus_loop) + 1))[:len(chorus)]

        output += verse.overlay(verse_loop)
        output += chorus.overlay(chorus_looped)
        current = end_ms

    # Add the rest of the song with main loop
    remaining = song[current:]
    if len(remaining) > 0:
        remaining_loop = (main_loop * (len(remaining) // len(main_loop) + 1))[:len(remaining)]
        output += remaining.overlay(remaining_loop)

    return output


def plot_volume_envelope_with_chorus(audio, chorus_times):
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
    ax.plot(time, envelope, label="Volume")

    for (start, end) in chorus_times:
        ax.axvspan(start, end, color='orange', alpha=0.3, label='Chorus')

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title("Volume Envelope with Chorus Highlighted")
    ax.legend()
    st.pyplot(fig)
