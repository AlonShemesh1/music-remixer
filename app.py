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

def get_bpm(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)

def get_chorus_intervals(path, sr=22050, k=4):
    y, _ = librosa.load(path, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    boundaries = librosa.segment.agglomerative(chroma, k=k)
    times = librosa.frames_to_time(boundaries, sr=sr)
    return [(times[i], times[i+1]) for i in range(len(times)-1)]

def mix_with_chorus_loop(song_path, main_loop_path, chorus_loop_path, chorus_times, bpm, volume_db, sr=22050):
    y, _ = librosa.load(song_path, sr=sr)
    loop_main, _ = librosa.load(main_loop_path, sr=sr)
    loop_chorus, _ = librosa.load(chorus_loop_path, sr=sr)

    loop_main = librosa.util.fix_length(loop_main, len(y))
    output = np.copy(y)

    gain = 10 ** (volume_db / 20.0)

    for start, end in chorus_times:
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        loop = loop_chorus
        loop = np.tile(loop, int(np.ceil((end_sample - start_sample) / len(loop))))
        loop = loop[:end_sample - start_sample]
        output[start_sample:end_sample] += gain * loop

    # Add main loop to non-chorus parts
    full_loop = np.tile(loop_main, int(np.ceil(len(y) / len(loop_main))))
    full_loop = full_loop[:len(y)]
    output += gain * full_loop

    return output

def plot_volume_envelope(y, sr=22050):
    hop_length = 512
    envelope = np.abs(librosa.stft(y, hop_length=hop_length)).mean(axis=0)
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)

    plt.figure(figsize=(10, 3))
    plt.plot(times, envelope, label="Volume Envelope")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Volume Envelope")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()
