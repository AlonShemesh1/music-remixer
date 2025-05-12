from pydub import AudioSegment
import librosa
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import tempfile


def load_audio(file):
    return AudioSegment.from_file(file)

def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")

def match_loop_to_bpm(beat, original_bpm, target_bpm):
    rate = target_bpm / original_bpm
    beat = beat._spawn(beat.raw_data, overrides={
        "frame_rate": int(beat.frame_rate * rate)
    })
    return beat.set_frame_rate(beat.frame_rate)

def get_bpm(file_path):
    y, sr = librosa.load(file_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)

def detect_chorus_intervals(file_path, top_db=30):
    y, sr = librosa.load(file_path)
    intervals = librosa.effects.split(y, top_db=top_db)
    segment_durations = [end - start for start, end in intervals]
    chorus_index = np.argmax(segment_durations)
    chorus_start = intervals[chorus_index][0] / sr * 1000  # to ms
    chorus_end = intervals[chorus_index][1] / sr * 1000
    return int(chorus_start), int(chorus_end)

def mix_loops(song, main_loop, chorus_loop, chorus_start, chorus_end, gain_db=0):
    main_loop = main_loop + gain_db
    chorus_loop = chorus_loop + gain_db

    main_section = song[:chorus_start]
    chorus_section = song[chorus_start:chorus_end]
    outro_section = song[chorus_end:]

    main_looped = (main_loop * (len(main_section) // len(main_loop) + 1))[:len(main_section)]
    chorus_looped = (chorus_loop * (len(chorus_section) // len(chorus_loop) + 1))[:len(chorus_section)]
    outro_looped = (main_loop * (len(outro_section) // len(main_loop) + 1))[:len(outro_section)]

    full_loop = main_looped + chorus_looped + outro_looped
    return song.overlay(full_loop)

def plot_volume_envelope(audio, chorus_start=None, chorus_end=None):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

    window_size = 1000
    if len(samples) % window_size != 0:
        padding = window_size - len(samples) % window_size
        samples = np.pad(samples, (0, padding), 'constant')

    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=len(envelope))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time, envelope, label="Volume")

    if chorus_start and chorus_end:
        ax.axvspan(chorus_start / 1000, chorus_end / 1000, color="orange", alpha=0.3, label="Chorus")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title("Volume Envelope with Chorus Highlight")
    ax.legend()
    st.pyplot(fig)
