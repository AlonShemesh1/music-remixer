import librosa
import numpy as np
import os
import random
import soundfile as sf

def get_volume_envelope(y, sr, frame_size=2048, hop_length=512):
    rms = librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_length)[0]
    return rms

def detect_chorus_intervals(y, sr):
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    recurrence = librosa.segment.recurrence_matrix(chroma, mode='affinity', sym=True)
    laplacian = librosa.segment.laplacian(recurrence, norm=True)
    segments = librosa.segment.agglomerative(laplacian, k=4)

    boundaries = np.flatnonzero(np.diff(segments)) * (512 / sr)
    boundaries = np.concatenate([[0], boundaries, [len(y) / sr]])

    durations = np.diff(boundaries)
    max_idx = np.argmax(durations)
    chorus_start = boundaries[max_idx]
    chorus_end = boundaries[max_idx + 1]
    return [(chorus_start, chorus_end)]

def remix_audio(input_path, style, chorus_intervals):
    y, sr = librosa.load(input_path, sr=None)

    beat_folder = "beats"
    all_beats = [f for f in os.listdir(beat_folder) if f.endswith(".mp3") and style.lower() in f.lower()]
    if len(all_beats) < 2:
        raise ValueError("At least 2 beats per style required.")

    selected_beats = random.sample(all_beats, 2)
    verse_loop, chorus_loop = [librosa.load(os.path.join(beat_folder, b), sr=sr)[0] for b in selected_beats]

    output = np.array([], dtype=np.float32)
    last = 0

    for start, end in chorus_intervals:
        start_sample = int(start * sr)
        end_sample = int(end * sr)

        verse_part = y[last:start_sample]
        chorus_part = y[start_sample:end_sample]

        # Loop the selected beats to match durations
        verse_repeated = np.tile(verse_loop, int(np.ceil(len(verse_part) / len(verse_loop))))[:len(verse_part)]
        chorus_repeated = np.tile(chorus_loop, int(np.ceil(len(chorus_part) / len(chorus_loop))))[:len(chorus_part)]

        mixed_verse = 0.5 * verse_part + 0.5 * verse_repeated
        mixed_chorus = 0.5 * chorus_part + 0.5 * chorus_repeated

        output = np.concatenate((output, mixed_verse, mixed_chorus))
        last = end_sample

    if last < len(y):
        verse_part = y[last:]
        verse_repeated = np.tile(verse_loop, int(np.ceil(len(verse_part) / len(verse_loop))))[:len(verse_part)]
        mixed_verse = 0.5 * verse_part + 0.5 * verse_repeated
        output = np.concatenate((output, mixed_verse))

    out_path = "remixed_output.wav"
    sf.write(out_path, output, sr)
    return out_path
