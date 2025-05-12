from pydub import AudioSegment
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

def load_audio(file):
    return AudioSegment.from_file(file)

def save_audio(audio_segment, path):
    audio_segment.export(path, format="mp3")

def mix_with_beat(song, beat_path, loop_gain_db=0):
    beat = AudioSegment.from_file(beat_path)
    beat += loop_gain_db
    looped = beat * (len(song) // len(beat) + 1)
    looped = looped[:len(song)]
    return song.overlay(looped)

def plot_volume_envelope(audio):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)
    window_size = 1000
    envelope = np.abs(samples).reshape(-1, window_size).mean(axis=1)
    time = np.linspace(0, len(audio) / 1000, num=len(envelope))
    fig, ax = plt.subplots()
    ax.plot(time, envelope)
    ax.set_title("Volume Envelope")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

def detect_chorus(file_path):
    y, sr = librosa.load(file_path)
    chroma = librosa.feature.chroma_cens(y=y, sr=sr)
    recurrence = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    sim = librosa.segment.path_enhance(recurrence)
    segments = librosa.segment.agglomerative(sim, k=2)
    bounds = librosa.segment.agglomerative(sim, k=4, axis=1)
    segment_times = librosa.frames_to_time(np.where(np.diff(bounds))[0], sr=sr)

    if len(segment_times) >= 2:
        start = int(segment_times[1] * 1000)
        end = int(segment_times[2] * 1000)
        return start, end
    else:
        return 30000, 50000  # fallback
