import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import streamlit as st


def load_audio(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    return y


def save_audio(y, path, sr=22050):
    sf.write(path, y, sr)


def get_bpm(audio_path):
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    path_sim = librosa.segment.path_enhance(similarity, window=7)
    segment_boundaries = librosa.segment.agglomerative(path_sim, k=4)

    # נניח שהקטע שחוזר הכי הרבה הוא הקורוס
    intervals = []
    duration = librosa.get_duration(y=y, sr=sr)
    segment_times = librosa.frames_to_time(segment_boundaries, sr=sr)

    for i in range(len(segment_times) - 1):
        start = segment_times[i]
        end = segment_times[i + 1]
        if end - start > 5:  # מסנן קטעים קצרים מאוד
            intervals.append((start, end))

    return intervals


def mix_with_chorus_loop(song, main_loop_path, chorus_loop_path, chorus_times, bpm, volume_db=-6):
    sr = 22050
    main_loop, _ = librosa.load(main_loop_path, sr=sr)
    chorus_loop, _ = librosa.load(chorus_loop_path, sr=sr)

    output = np.zeros_like(song)

    frame_size = len(main_loop)
    position = 0
    for i in range(len(song) // frame_size + 1):
        start_time = position / sr
        is_chorus = any(start <= start_time <= end for (start, end) in chorus_times)
        loop = chorus_loop if is_chorus else main_loop

        end = position + len(loop)
        if end > len(song):
            loop = loop[:len(song) - position]

        output[position:position + len(loop)] += loop
        position += len(loop)

    gain = 10 ** (volume_db / 20)
    mixed = song + output * gain
    return librosa.util.normalize(mixed)


def plot_volume_envelope(audio, title="Volume Envelope", chorus_times=[]):
    hop_length = 512
    frame_length = 1024
    envelope = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=22050, hop_length=hop_length)

    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label="Envelope", color="white")
    for start, end in chorus_times:
        plt.axvspan(start, end, color='orange', alpha=0.4, label="Chorus")
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()
