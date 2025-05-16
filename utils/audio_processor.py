import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from pydub import AudioSegment

def load_audio(path, sr=22050):
    y, _ = librosa.load(path, sr=sr)
    return y

def save_audio(audio, path, sr=22050):
    sf.write(path, audio, sr)

def get_bpm(path):
    y, sr = librosa.load(path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)

def get_chorus_intervals(path):
    y, sr = librosa.load(path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    sim_matrix = np.dot(chroma.T, chroma)
    sim_matrix = sim_matrix / np.max(sim_matrix)

    # Auto-detect repeated segments (simple peak detection)
    repeat_scores = np.sum(sim_matrix, axis=0)
    peaks = librosa.util.peak_pick(repeat_scores, 16, 16, 16, 16, 0.9, 5)

    times = librosa.frames_to_time(peaks, sr=sr)
    durations = np.diff(times, prepend=0)

    # Take 2–3 longest repeated parts as "chorus"
    segments = list(zip(times, durations))
    segments.sort(key=lambda x: x[1], reverse=True)
    chorus_times = [(round(s[0], 2), round(s[0] + 8, 2)) for s in segments[:2]]  # 8s each
    return chorus_times

def insert_loops(song, loop_path, bpm, duration, start_time, sr=22050, volume_db=0):
    loop_audio = AudioSegment.from_file(loop_path)
    beat_ms = 60000 / bpm
    loop_ms = duration * 1000
    looped = AudioSegment.silent(duration=0)
    while len(looped) < loop_ms:
        looped += loop_audio
    looped = looped[:int(loop_ms)].apply_gain(volume_db)

    song_segment = AudioSegment.silent(duration=len(song) * 1000 / sr)
    song_segment = song_segment.overlay(looped, position=int(start_time * 1000))
    samples = np.array(song_segment.get_array_of_samples()).astype(np.float32) / (2**15)
    return samples[:len(song)]

def mix_with_chorus_loop(song, main_loop_path, chorus_loop_path, chorus_times, bpm, volume_db=0, sr=22050):
    duration = librosa.get_duration(y=song, sr=sr)
    output = np.zeros_like(song)

    # Fill whole song with main loop
    full_loop = insert_loops(song, main_loop_path, bpm, duration, 0, sr, volume_db - 5)

    # Add chorus loop at chorus intervals
    chorus_overlay = np.zeros_like(song)
    for start, end in chorus_times:
        segment = insert_loops(song, chorus_loop_path, bpm, end - start, start, sr, volume_db)
        start_sample = int(start * sr)
        end_sample = start_sample + len(segment)
        chorus_overlay[start_sample:end_sample] += segment[:end_sample - start_sample]

    output = full_loop + chorus_overlay
    return output / np.max(np.abs(output))  # Normalize

def plot_volume_envelope(audio, title="Audio", chorus_times=None, sr=22050):
    hop_length = 512
    frame_length = 2048
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    plt.figure(figsize=(10, 3))
    plt.plot(times, rms, label="Volume", color='gray')

    if chorus_times:
        for start, end in chorus_times:
            plt.axvspan(start, end, color='red', alpha=0.3, label='Chorus')

    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("RMS Energy")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()
