import librosa
import numpy as np
import soundfile as sf
import random
import os

def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    similarity = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    similarity_enhanced = similarity.copy()
    boundaries = librosa.segment.agglomerative(similarity_enhanced, k=4)
    intervals = librosa.frames_to_time(boundaries, sr=sr)
    return [(intervals[i], intervals[i+1]) for i in range(len(intervals)-1)]

def compute_volume_envelope(audio_path):
    y, sr = librosa.load(audio_path, mono=True)
    hop_length = 512
    envelope = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return times, envelope

def remix_audio(song_path, style, chorus_segments):
    y, sr = librosa.load(song_path, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    # Select random loops
    base_loop_path = f'beats/{style}_loop_{random.randint(1, 4)}.mp3'
    chorus_loop_path = f'beats/{style}_loop_{random.randint(1, 4)}.mp3'

    base_loop, _ = librosa.load(base_loop_path, sr=sr)
    chorus_loop, _ = librosa.load(chorus_loop_path, sr=sr)

    # Prepare loop overlays
    loop_overlay = np.zeros_like(y)
    for i in range(0, len(y), len(base_loop)):
        segment = base_loop[:min(len(base_loop), len(y) - i)]
        loop_overlay[i:i+len(segment)] += segment

    # Add chorus loop on top during chorus segments
    for start, end in chorus_segments:
        s = int(start * sr)
        e = int(end * sr)
        seg_len = e - s
        chorus_audio = np.tile(chorus_loop, int(np.ceil(seg_len / len(chorus_loop))))[:seg_len]
        loop_overlay[s:e] += chorus_audio

    # Combine original audio with loops
    combined = y + loop_overlay

    # Normalize to prevent clipping
    max_amp = np.max(np.abs(combined))
    if max_amp > 1.0:
        combined = combined / max_amp

    out_path = "output/remixed.wav"
    sf.write(out_path, combined, sr)
    return out_path

def compute_volume_envelope_from_array(audio_array, sr):
    hop_length = 512
    envelope = librosa.feature.rms(y=audio_array, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return times, envelope
