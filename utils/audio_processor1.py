from pydub import AudioSegment

def load_audio(file):
    # Auto-detects format
    return AudioSegment.from_file(file)

def mix_with_beat(song, beat, gain_during_overlay=-3):
    # Loop beat to match the length of the song
    looped_beat = beat * (len(song) // len(beat) + 1)
    looped_beat = looped_beat[:len(song)]
    # Overlay the beat onto the song
    mixed = song.overlay(looped_beat, gain_during_overlay=gain_during_overlay)
    return mixed

def save_audio(audio_segment, output_path):
    audio_segment.export(output_path, format="mp3")
