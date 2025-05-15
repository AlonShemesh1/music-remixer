import streamlit as st
import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os
from io import BytesIO
from pydub import AudioSegment
from utils.audio_processor import (
    get_chorus_intervals,
    apply_loops,
    plot_volume_envelope,
)

st.set_page_config(page_title="Music Remixer", layout="wide")
st.title("🎵 Music Remixer App")

st.sidebar.header("Choose Remix Style")
style = st.sidebar.selectbox("Style", ("Hip-Hop", "Reggae", "Rock"))

style_loops = {
    "Hip-Hop": {
        "main": "beats/hiphop_main.mp3",
        "chorus": "beats/hiphop_chorus.mp3",
    },
    "Reggae": {
        "main": "beats/reggae_main.mp3",
        "chorus": "beats/reggae_chorus.mp3",
    },
    "Rock": {
        "main": "beats/rock_main.mp3",
        "chorus": "beats/rock_chorus.mp3",
    },
}

uploaded_file = st.file_uploader("Upload a song (MP3)", type=["mp3"])

if uploaded_file:
    st.audio(uploaded_file, format='audio/mp3')

    with st.spinner("Analyzing the song and detecting chorus..."):
        song_path = f"temp/{uploaded_file.name}"
        os.makedirs("temp", exist_ok=True)
        with open(song_path, "wb") as f:
            f.write(uploaded_file.read())

        y, sr = librosa.load(song_path)
        chorus_times = get_chorus_intervals(song_path)

        st.subheader("Original Volume Envelope")
        fig_before = plot_volume_envelope(y, sr, chorus_times, title="Before Remix")
        st.pyplot(fig_before)

        if st.button("Remix"):  # Only remix on click
            with st.spinner("Applying remix with loops..."):
                loop_main = style_loops[style]["main"]
                loop_chorus = style_loops[style]["chorus"]

                remixed_audio = apply_loops(song_path, loop_main, loop_chorus, chorus_times)

                remixed_path = "output/remixed_song.wav"
                os.makedirs("output", exist_ok=True)
                sf.write(remixed_path, remixed_audio, sr)

                y_remixed, _ = librosa.load(remixed_path)

                st.success("Remix complete!")

                st.subheader("Remixed Volume Envelope")
                fig_after = plot_volume_envelope(y_remixed, sr, chorus_times, title="After Remix")
                st.pyplot(fig_after)

                st.audio(remixed_path, format="audio/wav")
