import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import os


def get_volume_envelope(audio_path):
    y, sr = librosa.load(audio_path)
    frame_length = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    return times, rms


def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    recurrence = librosa.segment.recurrence_matrix(chroma, mode='affinity', sym=True)
    path_distance = librosa.segment.path_enhance(recurrence, n=3)
    labels = librosa.segment.agglomerative(path_distance, k=4)
    boundaries = np.flatnonzero(np.diff(labels))
    boundaries = librosa.frames_to_time(boundaries, sr=sr)
    segments = [(start, end) for start, end in zip(boundaries[:-1], boundaries[1:])]
    durations = [end - start for start, end in segments]
    chorus_segments = sorted(zip(segments, durations), key=lambda x: -x[1])[:1]
    return [seg for seg, _ in chorus_segments]


def process_audio(song_path, style, chorus_times):
    y, sr = librosa.load(song_path)

    loop_main_path = f"loops/{style}_main.mp3"
    loop_chorus_path = f"loops/{style}_chorus.mp3"

    if not os.path.exists(loop_main_path) or not os.path.exists(loop_chorus_path):
        raise FileNotFoundError("One of the loop files does not exist.")

    loop_main, _ = librosa.load(loop_main_path, sr=sr)
    loop_chorus, _ = librosa.load(loop_chorus_path, sr=sr)

    output = np.zeros_like(y)
    duration = librosa.get_duration(y=y, sr=sr)
    t = np.linspace(0, duration, num=len(y))

    chorus_mask = np.zeros_like(y)
    for start, end in chorus_times:
        chorus_mask += np.logical_and(t >= start, t <= end)

    i = 0
    while i < len(y):
        loop = loop_chorus if chorus_mask[i] else loop_main
        loop_len = len(loop)
        end_i = min(i + loop_len, len(y))
        loop_cut = loop[:end_i - i]
        output[i:end_i] += loop_cut
        i += loop_len

    output_path = "output/remixed_song.wav"
    sf.write(output_path, output, sr)
    times, envelope = get_volume_envelope(output_path)
    return output_path, (times, envelope)


def plot_envelope_with_chorus(times, envelope, chorus_times, title="Volume Envelope"):
    plt.figure(figsize=(10, 4))
    plt.plot(times, envelope, label='Envelope', color='skyblue')
    for start, end in chorus_times:
        plt.axvspan(start, end, color='orange', alpha=0.3, label='Chorus')
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Volume")
    plt.grid(True)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.tight_layout()
    plt.savefig("output/volume_envelope.png")
    plt.close()
