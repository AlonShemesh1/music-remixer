import streamlit as st
from utils.audio_processor import (
    load_audio, save_audio, mix_with_beat, get_bpm, plot_volume_envelope
)
import tempfile
import os

st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_song:
        temp_song.write(uploaded_file.read())
        song_path = temp_song.name

    try:
        st.subheader("Original Song")
        song = load_audio(song_path)
        st.audio(song_path)

        bpm = get_bpm(song_path)
        st.write(f"Detected BPM: {bpm}")

        style
