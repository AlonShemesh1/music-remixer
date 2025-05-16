# utils/audio_processor.py
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os
import soundfile as sf

# Load and compute the volume envelope
def get_volume_envelope(audio_path):
    y, sr = librosa.load(audio_path)
    frame_length = 2048
    hop_length = 512
    envelope = np.abs(librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length))
    return envelope, sr

# Simulate chorus detection (returns dummy timestamps for now)
def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
    return [(duration * 0.3, duration * 0.5), (duration * 0.7, duration * 0.85)]

# Plot envelope with chorus highlighted
def plot_envelope_with_chorus(envelope, sr, chorus_times, title=""):
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=512)
    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label='Volume Envelope', color='blue')
    for start, end in chorus_times:
        plt.axvspan(start, end, color='orange', alpha=0.3, label='Chorus')
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()

# Apply loop to chorus regions
def process_audio(audio_path, style, chorus_times):
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)

    loop_main_path = f"loops/{style.lower()}_main.mp3"
    loop_chorus_path = f"loops/{style.lower()}_chorus.mp3"

    loop_main, _ = librosa.load(loop_main_path, sr=sr)
    loop_chorus, _ = librosa.load(loop_chorus_path, sr=sr)

    output = np.copy(y)
    for start, end in chorus_times:
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        segment_len = end_sample - start_sample
        loop_segment = np.resize(loop_chorus, segment_len)
        output[start_sample:end_sample] = 0.5 * output[start_sample:end_sample] + 0.5 * loop_segment

    # Fill the rest with loop_main (very simple blend)
    for i in range(0, len(y), len(loop_main)):
        end_i = min(i + len(loop_main), len(output))
        output[i:end_i] = 0.5 * output[i:end_i] + 0.5 * loop_main[:end_i - i]

    output_path = "outputs/remixed_output.mp3"
    os.makedirs("outputs", exist_ok=True)
    sf.write(output_path, output, sr)
    envelope_after, _ = get_volume_envelope(output_path)
    return output_path, envelope_after
