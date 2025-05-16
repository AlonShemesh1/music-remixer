import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import streamlit as st

def detect_chorus_sections(audio_path):
    y, sr = librosa.load(audio_path, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    mfcc_delta = librosa.feature.delta(mfcc)

    from sklearn.cluster import KMeans
    mfcc_stack = np.vstack((mfcc, mfcc_delta))
    mfcc_stack = mfcc_stack.T

    kmeans = KMeans(n_clusters=3, random_state=0).fit(mfcc_stack)
    labels = kmeans.labels_

    beat_times = librosa.frames_to_time(beats, sr=sr)
    label_sequence = [labels[i] for i in beats if i < len(labels)]
    
    from collections import Counter
    label_counts = Counter(label_sequence)
    chorus_label = label_counts.most_common(1)[0][0]

    chorus_times = [beat_times[i] for i, lbl in enumerate(label_sequence) if lbl == chorus_label]

    # Merge close segments into intervals
    intervals = []
    if chorus_times:
        start = chorus_times[0]
        for i in range(1, len(chorus_times)):
            if chorus_times[i] - chorus_times[i-1] > 5:
                end = chorus_times[i-1] + 2
                intervals.append((start, end))
                start = chorus_times[i]
        intervals.append((start, chorus_times[-1] + 2))
    return intervals

def apply_remix_with_chorus_loop(original_path, main_loop_path, chorus_loop_path, chorus_times):
    y_song, sr = librosa.load(original_path)
    y_main, _ = librosa.load(main_loop_path, sr=sr)
    y_chorus, _ = librosa.load(chorus_loop_path, sr=sr)

    output = np.zeros_like(y_song)

    frame_len = len(y_main)
    song_len = len(y_song)
    chorus_mask = np.zeros(song_len)

    for start_sec, end_sec in chorus_times:
        start_sample = int(start_sec * sr)
        end_sample = int(end_sec * sr)
        chorus_mask[start_sample:end_sample] = 1

    i = 0
    while i < song_len:
        if chorus_mask[i] == 1:
            loop = y_chorus
        else:
            loop = y_main
        seg_len = min(frame_len, song_len - i)
        output[i:i+seg_len] += loop[:seg_len]
        i += seg_len

    remixed_path = "output/remixed_song.mp3"
    os.makedirs("output", exist_ok=True)
    sf.write(remixed_path, output, sr)
    return remixed_path

def plot_volume_envelope(audio_path, chorus_times):
    y, sr = librosa.load(audio_path)
    frame_length = 2048
    hop_length = 512
    envelope = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, envelope, label="Volume Envelope")
    for start, end in chorus_times:
        ax.axvspan(start, end, color='orange', alpha=0.4, label="Chorus")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Volume Envelope with Chorus Highlight")
    ax.legend()
    st.pyplot(fig)
