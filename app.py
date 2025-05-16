# app.py
import streamlit as st
import os
from utils.audio_processor import (
    get_volume_envelope,
    get_chorus_intervals,
    process_audio,
    plot_envelope_with_chorus
)

st.set_page_config(page_title="Music Remixer", layout="centered", page_icon="🎵")
st.markdown("<h1 style='text-align:center;color:#4B0082;'>🎵 AI Music Remixer</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a song (MP3 only)", type=["mp3"])
style = st.selectbox("Choose remix style:", ["Hip-Hop", "Reggae", "Rock"])

if uploaded_file:
    song_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())

    # Display original volume envelope
    st.subheader("Volume Envelope (Original)")
    envelope, sr = get_volume_envelope(song_path)
    chorus_times = get_chorus_intervals(song_path)
    plot_envelope_with_chorus(envelope, sr, chorus_times, title="Original Song Envelope")

    if st.button("Remix 🔄"):
        with st.spinner("Remixing in progress..."):
            audio_output_path, envelope_after = process_audio(song_path, style, chorus_times)

        st.success("Remix complete!")

        # Show remixed envelope
        st.subheader("Volume Envelope (Remixed)")
        plot_envelope_with_chorus(envelope_after, sr, chorus_times, title="Remixed Song Envelope")

        audio_file = open(audio_output_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')

        st.download_button("Download Remixed Song", audio_bytes, file_name="remixed_song.mp3")
