import streamlit as st
import os
from utils.audio_processor import (
    get_volume_envelope,
    get_chorus_intervals,
    process_audio,
    plot_envelope_with_chorus,
)

st.set_page_config(page_title="Music Remixer", layout="wide")

st.title("🎧 Music Remixer with Chorus Detection")

uploaded_file = st.file_uploader("Upload a song (MP3)", type=["mp3"])
style = st.selectbox("Choose a remix style", ["Hip-Hop", "Reggae", "Rock"])

if uploaded_file:
    song_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())

    st.audio(song_path, format="audio/mp3")

    with st.spinner("Analyzing song and detecting chorus..."):
        sr = 22050
        envelope = get_volume_envelope(song_path, sr)
        chorus_times = get_chorus_intervals(song_path)

    st.subheader("📊 Original Volume Envelope")
    plot_envelope_with_chorus(envelope, sr, chorus_times, title="Original Song Envelope")

    if st.button("🎛 Remix"):
        with st.spinner("Remixing in progress..."):
            audio_output_path, envelope_after = process_audio(song_path, style, chorus_times)

        st.success("Remix complete!")

        st.subheader("📊 Remixed Volume Envelope")
        plot_envelope_with_chorus(envelope_after, sr, chorus_times, title="Remixed Song Envelope")

        st.audio(audio_output_path, format="audio/mp3")
