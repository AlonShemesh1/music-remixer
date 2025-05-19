import streamlit as st
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
from utils.audio_processor import remix_audio, detect_chorus_intervals, get_volume_envelope
import numpy as np

st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎵 AI Music Remixer")

uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
style = st.selectbox("Choose Remix Style", ["Hip-Hop", "Reggae", "Rock"])

if st.button("Remix") and uploaded_file:
    with st.spinner("Processing..."):
        os.makedirs("uploads", exist_ok=True)
        song_path = os.path.join("uploads", uploaded_file.name)
        with open(song_path, "wb") as f:
            f.write(uploaded_file.read())

        y, sr = librosa.load(song_path)
        chorus_times = detect_chorus_intervals(y, sr)

        st.subheader("Original Volume Envelope")
        times, envelope = get_volume_envelope(song_path)
        fig, ax = plt.subplots()
        ax.plot(times, envelope)
        for start, end in chorus_times:
            ax.axvspan(start, end, color='orange', alpha=0.3)
        ax.set_title("Original Song")
        st.pyplot(fig)

        output_path = remix_audio(song_path, style, chorus_times)

        st.subheader("Remixed Volume Envelope")
        times2, envelope2 = get_volume_envelope(output_path)
        fig2, ax2 = plt.subplots()
        ax2.plot(times2, envelope2)
        for start, end in chorus_times:
            ax2.axvspan(start, end, color='green', alpha=0.3)
        ax2.set_title("Remixed Song")
        st.pyplot(fig2)

        st.success("Remix complete!")
        st.audio(output_path)
