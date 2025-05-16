# app.py
import streamlit as st
import os
from utils.audio_processor import (
    get_volume_envelope,
    get_chorus_intervals,
    plot_envelope_with_chorus,
    process_audio
)
import time

st.set_page_config(page_title="Music Remixer", layout="wide", page_icon="🎵")
st.markdown("""
    <style>
        .main { background-color: #ffffff; }
        .stButton>button {
            color: white;
            background-color: #4CAF50;
            font-size: 18px;
            padding: 10px 24px;
            border-radius: 12px;
        }
        .stProgress > div > div {
            background-color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Music Remixer")
st.markdown("Upload a song, select a style, and remix it with special loops during the chorus!")

uploaded_file = st.file_uploader("Upload your song (MP3)", type=["mp3"])
style = st.selectbox("Choose remix style:", ["Hip-Hop", "Reggae", "Rock"])

if uploaded_file:
    song_path = f"uploaded_song.mp3"
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())

    st.audio(song_path)
    
    sr = 22050
    envelope = get_volume_envelope(song_path, sr)
    chorus_times = get_chorus_intervals(song_path)

    st.subheader("Original Volume Envelope")
    plot_envelope_with_chorus(envelope, sr, chorus_times, title="Original Song Envelope")

    if st.button("Remix", type="primary"):
        with st.spinner("Remixing..."):
            progress = st.progress(0)
            for i in range(1, 101):
                time.sleep(0.01)
                progress.progress(i)
            output_path, envelope_after = process_audio(song_path, style, chorus_times)

        st.success("Remix complete!")
        st.audio(output_path)

        st.subheader("Remixed Volume Envelope")
        plot_envelope_with_chorus(envelope_after, sr, chorus_times, title="Remixed Song Envelope")
