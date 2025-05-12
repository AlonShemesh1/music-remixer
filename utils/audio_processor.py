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
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = np.dot(chroma.T, chroma)

    # Find repeated section (naive thresholding)
    chorus_start = 0
    chorus_end = 0
    max_score = 0
    frame_duration = librosa.frames_to_time(1, sr=sr)

    for i in range(similarity.shape[0] - 50):  # minimum length 50 frames (~2s)
        for j in range(i + 30, similarity.shape[1] - 50):
            score = np.sum(similarity[i:i + 50, j:j + 50])
            if score > max_score:
                max_score = score
                chorus_start = i
                chorus_end = i + 50

    # Convert frame indices to milliseconds
    start_time = int(librosa.frames_to_time(chorus_start, sr=sr) * 1000)
    end_time = int(librosa.frames_to_time(chorus_end, sr=sr) * 1000)
    return start_time, end_time

