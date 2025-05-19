import streamlit as st
import os
import random
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from utils.audio_processor import (
    get_chorus_intervals,
    apply_loops_to_song,
    get_volume_envelope,
    save_audio
)

st.set_page_config(page_title="Music Remixer", layout="wide")
st.title("🎧 Music Remixer")

style = st.selectbox("Choose a remix style:", ["Hip-Hop", "Reggae", "Rock"])

uploaded_file = st.file_uploader("Upload a song (MP3 format)", type=["mp3"])

if uploaded_file:
    song_path = os.path.join("uploads", uploaded_file.name)
    with open(song_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.audio(song_path)

    st.subheader("Original Volume Envelope")
    original_env, sr = get_volume_envelope(song_path)
    times = np.linspace(0, len(original_env)/sr, num=len(original_env))
    chorus_times = get_chorus_intervals(song_path)

    fig, ax = plt.subplots()
    ax.plot(times, original_env, label='Volume')
    for start, end in chorus_times:
        ax.axvspan(start, end, color='red', alpha=0.3)
    ax.set_title("Original Volume Envelope with Chorus Highlighted")
    st.pyplot(fig)

    if st.button("Remix"):
        with st.spinner("Remixing in progress..."):
            loop_numbers = random.sample([1, 2, 3, 4], 2)
            verse_loop_path = f"beats/{style.lower()}_loop_{loop_numbers[0]}.mp3"
            chorus_loop_path = f"beats/{style.lower()}_loop_{loop_numbers[1]}.mp3"

            output_path = apply_loops_to_song(
                song_path,
                verse_loop_path,
                chorus_loop_path,
                chorus_times
            )

            st.subheader("Remixed Volume Envelope")
            remixed_env, _ = get_volume_envelope(output_path)
            remixed_times = np.linspace(0, len(remixed_env)/sr, num=len(remixed_env))
            fig2, ax2 = plt.subplots()
            ax2.plot(remixed_times, remixed_env, label='Volume')
            for start, end in chorus_times:
                ax2.axvspan(start, end, color='green', alpha=0.3)
            ax2.set_title("Remixed Volume Envelope with Chorus Highlighted")
            st.pyplot(fig2)

            st.success("Remix complete!")
            st.audio(output_path)
            with open(output_path, "rb") as f:
                st.download_button("Download Remixed Song", f, file_name="remixed_song.mp3")
