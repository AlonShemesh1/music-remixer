import librosa
import numpy as np
import soundfile as sf
import os
import random

def remix_audio(song_path, style, chorus_segments):
    # טען את השיר
    y, sr = librosa.load(song_path, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    # טען לופים מהתיקייה
    beat_folder = "beats"
    beat_files = [f for f in os.listdir(beat_folder) if f.startswith(style) and f.endswith(".wav")]

    if len(beat_files) < 2:
        raise ValueError("Need at least two loops for this style")

    # בחר לופ לפסקה ולופ לפזמון
    verse_loop = librosa.load(os.path.join(beat_folder, random.choice(beat_files)), sr=sr)[0]
    chorus_loop = librosa.load(os.path.join(beat_folder, random.choice(beat_files)), sr=sr)[0]

    # בנה רצועת לופים באורך השיר
    loops = np.zeros_like(y)
    for i in range(0, len(y), len(verse_loop)):
        loops[i:i+len(verse_loop)] = verse_loop[:min(len(verse_loop), len(y)-i)]

    # עבור הפזמון – הדבק לופ אחר במקום
    for start, end in chorus_segments:
        s = int(start * sr)
        e = int(end * sr)
        seg_len = e - s
        chorus_fill = np.tile(chorus_loop, int(np.ceil(seg_len / len(chorus_loop))))
        loops[s:e] = chorus_fill[:seg_len]

    # מיזוג בין השיר ללופים
    combined = y + loops
    combined = combined / np.max(np.abs(combined))  # נרמול עוצמה
    combined = combined.astype(np.float32)

    # שמור את הקובץ
    os.makedirs("output", exist_ok=True)
    out_path = "output/remixed.wav"
    sf.write(out_path, combined, sr)
    return out_path
