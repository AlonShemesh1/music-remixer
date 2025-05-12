from pydub import AudioSegment
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


def load_audio(file):
    return AudioSegment.from_file(file)


def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")


def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())

    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    window_size = 1000
    num_windows = len(samples) // window_size

    if num_windows == 0:
        st.warning("Audio too short to show volume plot.")
        return

    samples = samples[:num_windows * window_size]
    envelope = np.abs(samples).reshape(num_windows, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=num_windows)

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(time, envelope, color='blue')
    ax.set_title("Volume Envelope")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)


def apply_loops_with_chorus(song, main_loop_path, chorus_loop_path, loop_gain_db=0):
    main_loop = AudioSegment.from_file(main_loop_path) + loop_gain_db
    chorus_loop = AudioSegment.from_file(chorus_loop_path) + loop_gain_db

    song_duration = len(song)

    # Simulated chorus section (from 30s to 45s)
    chorus_start = 30_000  # ms
    chorus_end = 45_000    # ms

    part1 = song[:chorus_start]
    part2 = song[chorus_start:chorus_end]
    part3 = song[chorus_end:]

    loop1 = main_loop * (len(part1) // len(main_loop) + 1)
    loop2 = chorus_loop * (len(part2) // len(chorus_loop) + 1)
    loop3 = main_loop * (len(part3) // len(main_loop) + 1)

    remixed = (
        part1.overlay(loop1[:len(part1)]) +
        part2.overlay(loop2[:len(part2)]) +
        part3.overlay(loop3[:len(part3)])
    )

    return remixed
