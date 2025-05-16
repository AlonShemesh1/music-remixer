# utils/audio_processor.py

import librosa
import numpy as np
import soundfile as sf

def get_volume_envelope(audio_path, hop_length=512):
    y, sr = librosa.load(audio_path, sr=None)
    envelope = np.abs(librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length))
    return envelope

def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    S = np.abs(librosa.stft(y))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    segments = librosa.segment.agglomerative(S_db, k=4)
    boundaries = librosa.segment.agglomerative(S_db, k=4, axis=-1)
    segment_times = librosa.frames_to_time(boundaries, sr=sr)
    chorus_times = [(segment_times[i], segment_times[i+1]) for i in range(1, len(segment_times)-1, 2)]
    return chorus_times

def process_audio(audio_path, style, chorus_times):
    y, sr = librosa.load(audio_path, sr=None)

    if style == "Hip-Hop":
        loop_path = "/mnt/data/hiphop_chorus.mp3"
    elif style == "Reggae":
        loop_path = "/mnt/data/reggae_chorus.mp3"
    elif style == "Rock":
        loop_path = "/mnt/data/rock_chorus.mp3"
    else:
        loop_path = None

    if loop_path:
        loop_audio, _ = librosa.load(loop_path, sr=sr)

    for start, end in chorus_times:
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        segment_len = end_sample - start_sample
        loop_segment = np.tile(loop_audio, int(np.ceil(segment_len / len(loop_audio))))[:segment_len]
        y[start_sample:end_sample] = loop_segment

    output_path = "/mnt/data/remixed_output.mp3"
    sf.write(output_path, y, sr)

    envelope = get_volume_envelope(output_path)
    return output_path, envelope

def plot_envelope_with_chorus(envelope, chorus_times, hop_length=512, sr=22050):
    import matplotlib.pyplot as plt

    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, envelope, label='Volume Envelope', color='blue')
    for start, end in chorus_times:
        ax.axvspan(start, end, color='orange', alpha=0.3, label='Chorus')
    ax.set_title("Volume Envelope with Chorus Highlighted")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.legend()
    return fig
