from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt



def load_audio(file):
    # Auto-detects format
    return AudioSegment.from_file(file)

def mix_with_beat(song, beat, loop_gain_db=-3):
    # Loop beat to match the length of the song
    looped_beat = beat * (len(song) // len(beat) + 1)
    looped_beat = looped_beat[:len(song)]
    # Adjust the beat volume
    looped_beat = looped_beat + loop_gain_db  # Increase/decrease volume
    # Overlay the beat onto the song
    mixed = song.overlay(looped_beat)
    return mixed


def save_audio(audio_segment, output_path):
    audio_segment.export(output_path, format="mp3")

def plot_volume_envelope(audio_segment, chunk_ms=500, title="Volume Envelope"):
    loudness = []
    times = []
    for i in range(0, len(audio_segment), chunk_ms):
        chunk = audio_segment[i:i+chunk_ms]
        loudness.append(chunk.dBFS)
        times.append(i / 1000)  # seconds

    # plt.figure(figsize=(10, 4))
    # plt.plot(times, loudness)
    # plt.title(title)
    # plt.xlabel("Time (s)")
    # plt.ylabel("Volume (dBFS)")
    # plt.tight_layout()
    return plt
def plot_volume_envelope(audio_segment, chunk_ms=500, title="Volume Envelope", cursor_sec=None):
    loudness = []
    times = []
    for i in range(0, len(audio_segment), chunk_ms):
        chunk = audio_segment[i:i+chunk_ms]
        loudness.append(chunk.dBFS)
        times.append(i / 1000)  # seconds

