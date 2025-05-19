import streamlit as st
import os
from utils.audio_processor import (
    compute_volume_envelope,
    get_chorus_intervals,
    remix_audio
)
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Music Remixer", layout="centered")

st.title("🎛️ Music Remixer")
st.markdown("Upload a song and remix it with a different style loop for the chorus!")

uploaded_file = st.file_uploader("Upload a song (mp3 or wav)", type=["mp3", "wav"])

style = st.selectbox("Choose a style for remixing:", ["hiphop", "reggae", "rock"])

if uploaded_file:
    song_path = f"uploaded/{uploaded_file.name}"
    os.makedirs("uploaded", exist_ok=True)
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())

    # Show original envelope
    st.subheader("Original Volume Envelope")
    times, envelope = compute_volume_envelope(song_path)
    chorus_times = get_chorus_intervals(song_path)

    fig, ax = plt.subplots()
    ax.plot(times, envelope, label="Envelope")
    for start, end in chorus_times:
        ax.axvspan(start, end, color='red', alpha=0.3, label='Chorus')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title("Original Envelope with Chorus Highlighted")
    st.pyplot(fig)

    if st.button("🔁 Remix"):
        with st.spinner("Remixing..."):
            output_path = remix_audio(song_path, style, chorus_times)

            # Show remixed envelope
            st.subheader("Remixed Volume Envelope")
            times2, envelope2 = compute_volume_envelope(output_path)
            fig2, ax2 = plt.subplots()
            ax2.plot(times2, envelope2, label="Remixed")
            for start, end in chorus_times:
                ax2.axvspan(start, end, color='green', alpha=0.3, label='Chorus')
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Volume")
            ax2.set_title("Remixed Envelope with Chorus Highlighted")
            st.pyplot(fig2)

            st.audio(output_path, format='audio/wav')
            st.success("Remix complete!")
