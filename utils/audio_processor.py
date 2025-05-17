import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import streamlit as st

def load_audio(path, sr=22050):
    y, sr = librosa.load(path, sr=sr)
    return y, sr

def save_audio(y, sr, path):
    sf.write(path, y, sr)

def get_chorus_intervals(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    path_sim = librosa.segment.path_enhance(similarity, window=7)
    repeat_scores = path_sim.sum(axis=1)
    peaks = librosa.util.peak_pick(repeat_scores, 16, 16, 16, 16, 0.9, 5)
    beat_times = librosa.frames_to_time(peaks, sr=sr)
    intervals = [(t, t + 5.0) for t in beat_times]  # each chorus segment lasts 5 seconds
    return intervals

def plot_envelope_with_chorus(y, sr, chorus_times, title="Volume Envelope"):
    hop_length = 512
    frame_length = 1024
    envelope = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    
    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label='Envelope')
    for start, end in chorus_times:
        plt.axvspan(start, end, color='red', alpha=0.3)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()

def insert_loops(y, sr, main_loop_path, chorus_loop_path, chorus_intervals, loop_db):
    loop_main, _ = librosa.load(main_loop_path, sr=sr)
    loop_chorus, _ = librosa.load(chorus_loop_path, sr=sr)

    loop_main *= librosa.db_to_amplitude(loop_db)
    loop_chorus *= librosa.db_to_amplitude(loop_db)

    output = np.copy(y)
    total_samples = len(output)

    for i in range(0, total_samples, len(loop_main)):
        end = min(i + len(loop_main), total_samples)
        output[i:end] += loop_main[:end - i]

    for start_time, end_time in chorus_intervals:
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        loop_len = end_sample - start_sample
        chorus_loop_section = np.tile(loop_chorus, int(np.ceil(loop_len / len(loop_chorus))))[:loop_len]
        output[start_sample:end_sample] += chorus_loop_section

    envelope = librosa.feature.rms(y=output, frame_length=1024, hop_length=512)[0]
    return output, envelope
