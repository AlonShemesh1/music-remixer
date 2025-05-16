# utils/audio_processor.py
import os
import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import streamlit as st

def get_volume_envelope(audio_path, sr=22050):
    y, _ = librosa.load(audio_path, sr=sr)
    hop_length = 512
    frame_length = 1024
    envelope = np.abs(librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length))
    return envelope

def get_chorus_intervals(audio_path, sr=22050):
    y, _ = librosa.load(audio_path, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    if len(beats) < 2:
        return []  # לא מספיק ביטים כדי לזהות פזמון

    beat_times = librosa.frames_to_time(beats, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    # ודא שיש מספיק פריימים לאשכול
    if chroma.shape[1] < 2:
        return []

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, random_state=0).fit(chroma.T)
    labels = kmeans.labels_

    chorus_cluster = np.argmax(np.bincount(labels))
    chorus_times = []

    for i in range(len(labels) - 1):
        if i + 1 < len(beat_times) and labels[i] == chorus_cluster:
            chorus_times.append((beat_times[i], beat_times[i + 1]))

    return chorus_times


def plot_envelope_with_chorus(envelope, sr, chorus_times, title="Volume Envelope"):
    plt.figure(figsize=(10, 3))
    times = np.linspace(0, len(envelope) / sr, num=len(envelope))
    plt.plot(times, envelope, label="Volume Envelope")

    for start, end in chorus_times:
        plt.axvspan(start, end, color='orange', alpha=0.4)

    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    st.pyplot(plt.gcf())
    plt.close()

def process_audio(audio_path, style, chorus_times, loops_dir="beats", sr=22050):
    y, _ = librosa.load(audio_path, sr=sr)

    style_lower = style.lower().replace("-", "")
    loop_main_path = os.path.join(loops_dir, f"{style_lower}_main.wav")
    loop_chorus_path = os.path.join(loops_dir, f"{style_lower}_chorus.wav")

    if not os.path.exists(loop_main_path) or not os.path.exists(loop_chorus_path):
        raise FileNotFoundError(f"Missing loop files for style: {style}")

    loop_main, _ = librosa.load(loop_main_path, sr=sr)
    loop_chorus, _ = librosa.load(loop_chorus_path, sr=sr)

    output = np.zeros_like(y)
    beat_frames = librosa.time_to_frames(np.arange(len(y) / sr), sr=sr)

    chorus_mask = np.zeros(len(y), dtype=bool)
    for start, end in chorus_times:
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        chorus_mask[start_sample:end_sample] = True

    loop_len = len(loop_main)
    for i in range(0, len(y), loop_len):
        end = i + loop_len
        segment = loop_chorus if np.any(chorus_mask[i:end]) else loop_main
        if end > len(y):
            segment = segment[:len(y) - i]
        output[i:i + len(segment)] += segment

    output_path = "remixed_output.wav"
    sf.write(output_path, output, sr)
    envelope_after = get_volume_envelope(output_path, sr)
    return output_path, envelope_after
