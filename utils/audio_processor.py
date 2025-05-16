# utils/audio_processor.py
import os
import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import streamlit as st


def get_volume_envelope(path, sr):
    y, _ = librosa.load(path, sr=sr)
    envelope = np.abs(librosa.onset.onset_strength(y=y, sr=sr))
    return envelope

def get_chorus_intervals(path):
    y, sr = librosa.load(path)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    from sklearn.cluster import KMeans
    segments = KMeans(n_clusters=2, random_state=0).fit_predict(chroma.T[beats])
    chorus_cluster = max(set(segments), key=list(segments).count)
    chorus_times = [(beat_times[i], beat_times[i+1]) for i in range(len(beats)-1) if segments[i] == chorus_cluster]
    return chorus_times

def plot_envelope_with_chorus(envelope, sr, chorus_times, title="Volume Envelope"):
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr)
    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label='Volume Envelope')
    for start, end in chorus_times:
        plt.axvspan(start, end, color='red', alpha=0.3)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Volume")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()

def process_audio(song_path, style, chorus_times, loops_dir="beats"):
    y, sr = librosa.load(song_path, sr=None)
    output = np.zeros_like(y)

    loop_main_path = os.path.join(loops_dir, f"{style.lower()}_main.wav")
    loop_chorus_path = os.path.join(loops_dir, f"{style.lower()}_chorus.wav")

    loop_main, _ = librosa.load(loop_main_path, sr=sr)
    loop_chorus, _ = librosa.load(loop_chorus_path, sr=sr)

    beat_frames = librosa.beat.beat_track(y=y, sr=sr)[1]
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    is_chorus = np.zeros(len(beat_times), dtype=bool)
    for i, t in enumerate(beat_times):
        for start, end in chorus_times:
            if start <= t <= end:
                is_chorus[i] = True

    for i, t in enumerate(beat_times[:-1]):
        start_sample = int(t * sr)
        end_sample = int(beat_times[i+1] * sr)
        loop = loop_chorus if is_chorus[i] else loop_main
        segment = librosa.util.fix_length(loop, end_sample - start_sample)
        output[start_sample:end_sample] += segment

    output_path = "remixed_output.wav"
    sf.write(output_path, output, sr)
    envelope = np.abs(librosa.onset.onset_strength(y=output, sr=sr))
    return output_path, envelope
