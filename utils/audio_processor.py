# utils/audio_processor.py

from pydub import AudioSegment
import numpy as np
import librosa
import matplotlib.pyplot as plt
import streamlit as st

def load_audio(file_path):
    return AudioSegment.from_file(file_path)

def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")

def get_bpm(file_path):
    y, sr = librosa.load(file_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)

def get_chorus_intervals(file_path, sr=22050, k=4):
    y, _ = librosa.load(file_path, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    segments = librosa.segment.agglomerative(chroma, k=k)
    times = librosa.frames_to_time(segments, sr=sr)
    return times.tolist()

def match_loop_to_bpm(loop, original_bpm, target_bpm):
    rate = target_bpm / original_bpm
    loop = loop._spawn(loop.raw_data, overrides={"frame_rate": int(loop.frame_rate * rate)})
    return loop.set_frame_rate(loop.frame_rate)

def mix_with_chorus_loop(song, main_loop_path, chorus_loop_path, chorus_times, bpm, loop_gain_db=0):
    main_loop = AudioSegment.from_file(main_loop_path)
    chorus_loop = AudioSegment.from_file(chorus_loop_path)

    main_loop = match_loop_to_bpm(main_loop, 100, bpm)
    chorus_loop = match_loop_to_bpm(chorus_loop, 100, bpm)

    main_loop += loop_gain_db
    chorus_loop += loop_gain_db

    segment_duration = 0
    remixed = AudioSegment.empty()
    total_duration = len(song)

    if not chorus_times:
        return song.overlay(main_loop * (total_duration // len(main_loop) + 1))[:total_duration]

    chorus_starts = [int(t * 1000) for t in chorus_times]
    chorus_starts.append(total_duration)

    for i in range(len(chorus_starts) - 1):
        start = chorus_starts[i]
        end = chorus_starts[i + 1]
        segment = song[start:end]
        loop = chorus_loop if i % 2 == 1 else main_loop
        looped = (loop * (len(segment) // len(loop) + 1))[:len(segment)]
        remixed += segment.overlay(looped)

    return remixed

def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    window_size = 1000
    pad_size = window_size - (len(samples) % window_size)
    samples = np.pad(samples, (0, pad_size), mode='constant')

    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=len(envelope))

    fig, ax = plt.subplots()
    ax.plot(time, envelope)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title("Volume Envelope")
    st.pyplot(fig)
