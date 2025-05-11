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



