import os
import random
import librosa
import numpy as np
import soundfile as sf
from scipy.sparse import csgraph

def get_volume_envelope(y, frame_size=2048, hop_size=512):
    envelope = []
    for i in range(0, len(y), hop_size):
        frame = y[i:i+frame_size]
        envelope.append(np.sqrt(np.mean(frame**2)))
    return np.array(envelope)

def detect_chorus_intervals(y, sr):
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    recurrence = librosa.segment.recurrence_matrix(chroma, mode='affinity', sym=True)
    
    # מחשבים Laplacian באמצעות scipy
    laplacian = csgraph.laplacian(recurrence, normed=True)
    
    # מבצעים clustering
    segments = librosa.segment.agglomerative(laplacian, k=4)
    boundaries = np.flatnonzero(np.diff(segments)) * (512 / sr)
    boundaries = np.concatenate([[0], boundaries, [len(y) / sr]])

    durations = np.diff(boundaries)
    max_idx = np.argmax(durations)
    chorus_start = boundaries[max_idx]
    chorus_end = boundaries[max_idx + 1]
    return [(chorus_start, chorus_end)]

def remix_audio(song_path, style, chorus_times):
    y, sr = librosa.load(song_path, sr=None)
    beat_folder = "beats"

    if not os.path.exists(beat_folder):
        raise FileNotFoundError(f"Directory {beat_folder} not found.")

    # Normalize style string to match filenames
    style_prefix = style.lower().replace("-", "").replace(" ", "")
    beat_files = [f for f in os.listdir(beat_folder) 
                  if f.lower().endswith(".mp3") and style_prefix in f.lower()]
    
    if len(beat_files) < 2:
        raise ValueError(f"Need at least 2 beat files for style '{style}'.")

    # Pick 2 random loops: one for verse, one for chorus
    verse_loop_file, chorus_loop_file = random.sample(beat_files, 2)
    verse_loop, _ = librosa.load(os.path.join(beat_folder, verse_loop_file), sr=sr)
    chorus_loop, _ = librosa.load(os.path.join(beat_folder, chorus_loop_file), sr=sr)

    chorus_start, chorus_end = chorus_times[0]
    chorus_start_sample = int(chorus_start * sr)
    chorus_end_sample = int(chorus_end * sr)

    before_chorus = y[:chorus_start_sample]
    chorus = y[chorus_start_sample:chorus_end_sample]
    after_chorus = y[chorus_end_sample:]

    def apply_loop(section, loop):
        loop = np.tile(loop, int(np.ceil(len(section) / len(loop))))
        loop = loop[:len(section)]
        return 0.6 * section + 0.4 * loop[:len(section)]

    before_remixed = apply_loop(before_chorus, verse_loop)
    chorus_remixed = apply_loop(chorus, chorus_loop)
    after_remixed = apply_loop(after_chorus, verse_loop)

    combined = np.concatenate([before_remixed, chorus_remixed, after_remixed])
    out_path = "output_remix.wav"
    sf.write(out_path, combined, sr)
    return out_path

