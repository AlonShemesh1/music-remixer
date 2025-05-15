import librosa
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import os

def detect_chorus(audio_path):
    y, sr = librosa.load(audio_path)
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_dB = librosa.power_to_db(S, ref=np.max)
    segments = librosa.segment.agglomerative(S_dB, k=4)
    chorus_label = np.bincount(segments).argmax()
    times = librosa.times_like(segments, sr=sr)
    chorus_times = [(times[i], times[i+1]) for i in range(len(segments)-1)
                    if segments[i] == chorus_label]
    return chorus_times

def plot_volume_envelope_with_chorus(audio_path, chorus_intervals):
    y, sr = librosa.load(audio_path)
    hop_length = 512
    frame_length = 2048
    envelope = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, envelope, label='Volume Envelope')

    for start, end in chorus_intervals:
        ax.axvspan(start, end, color='red', alpha=0.3, label='Chorus')

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Volume Envelope with Chorus Highlighted")
    ax.legend()
    return fig

def apply_remix(song_path, main_loop_path, chorus_loop_path, chorus_intervals):
    original = AudioSegment.from_file(song_path)
    main_loop = AudioSegment.from_file(main_loop_path)
    chorus_loop = AudioSegment.from_file(chorus_loop_path)

    output = AudioSegment.empty()
    last_pos = 0

    for start, end in chorus_intervals:
        seg_start = int(last_pos * 1000)
        seg_end = int(start * 1000)
        output += original[seg_start:seg_end].overlay(main_loop, loop=True)

        chorus_duration = int((end - start) * 1000)
        chorus_section = chorus_loop[:chorus_duration]
        output += original[seg_end:int(end * 1000)].overlay(chorus_section, loop=True)

        last_pos = end

    # Add the remaining part
    output += original[int(last_pos * 1000):].overlay(main_loop, loop=True)

    out_path = "remixed_output.mp3"
    output.export(out_path, format="mp3")
    return out_path
