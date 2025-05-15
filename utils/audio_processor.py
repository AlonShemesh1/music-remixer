import os
import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pydub import AudioSegment

def get_chorus_intervals(y, sr):
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    similarity = np.corrcoef(chroma)
    mean_similarity = np.mean(similarity, axis=1)
    peaks, _ = find_peaks(mean_similarity, distance=sr//2, prominence=0.1)

    intervals = []
    for peak in peaks:
        start = peak * 512 / sr
        end = start + 8  # assuming chorus lasts around 8 seconds
        intervals.append((start, end))
    return intervals

def plot_volume_envelope(y, sr, chorus_intervals=None, title="Volume Envelope"):
    frame_length = 2048
    hop_length = 512
    envelope = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)

    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label='Volume')
    if chorus_intervals:
        for start, end in chorus_intervals:
            plt.axvspan(start, end, color='red', alpha=0.3, label='Chorus')
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Volume')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"/tmp/{title}.png")
    plt.close()
    return f"/tmp/{title}.png"

def apply_loops(song_path, main_loop_path, chorus_loop_path, chorus_intervals, output_path):
    song = AudioSegment.from_file(song_path)
    main_loop = AudioSegment.from_file(main_loop_path)
    chorus_loop = AudioSegment.from_file(chorus_loop_path)

    final = AudioSegment.silent(duration=0)
    position = 0

    for interval in chorus_intervals:
        start_ms = int(interval[0] * 1000)
        end_ms = int(interval[1] * 1000)

        if start_ms > position:
            segment = song[position:start_ms]
            looped = loop_audio_to_duration(main_loop, len(segment))
            final += mix_audio(segment, looped)

        chorus_segment = song[start_ms:end_ms]
        chorus_looped = loop_audio_to_duration(chorus_loop, len(chorus_segment))
        final += mix_audio(chorus_segment, chorus_looped)

        position = end_ms

    if position < len(song):
        last_segment = song[position:]
        last_looped = loop_audio_to_duration(main_loop, len(last_segment))
        final += mix_audio(last_segment, last_looped)

    final.export(output_path, format="mp3")
    return output_path

def loop_audio_to_duration(loop, target_duration_ms):
    looped = AudioSegment.empty()
    while len(looped) < target_duration_ms:
        looped += loop
    return looped[:target_duration_ms]

def mix_audio(a, b):
    return a.overlay(b)
