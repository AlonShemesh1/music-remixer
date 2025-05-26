import streamlit as st
import librosa
import matplotlib.pyplot as plt
import numpy as np
import os
from utils.audio_processor import remix_audio, detect_chorus_intervals, get_volume_envelope
import soundfile as sf

st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎵 Music Remixer App")

uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])

if uploaded_file and style:
    with open("input_song.mp3", "wb") as f:
        f.write(uploaded_file.read())
    song_path = "input_song.mp3"

    y, sr = librosa.load(song_path, sr=None)
    st.subheader("🔍 Original Volume Envelope")
    original_env = get_volume_envelope(y, sr)
    times = np.linspace(0, len(y) / sr, num=len(original_env))

    chorus_times = detect_chorus_intervals(y, sr)

    fig, ax = plt.subplots()
    ax.plot(times, original_env, label="Envelope")
    for start, end in chorus_times:
        ax.axvspan(start, end, color='orange', alpha=0.3, label='Chorus')
    ax.set_title("Volume Envelope with Chorus Highlighted")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    st.pyplot(fig)

    if st.button("🎛 Remix"):
        with st.spinner("Remixing..."):
            output_path = remix_audio(song_path, style, chorus_times)
            st.success("Remix complete!")
            st.audio(output_path)
            
            # Show new envelope
            y_remix, sr_remix = librosa.load(output_path, sr=None)
            remixed_env = get_volume_envelope(y_remix, sr_remix)
            times_remix = np.linspace(0, len(y_remix) / sr_remix, num=len(remixed_env))

            st.subheader("🎚 Remixed Volume Envelope")
            fig2, ax2 = plt.subplots()
            ax2.plot(times_remix, remixed_env, label="Envelope")
            for start, end in chorus_times:
                ax2.axvspan(start, end, color='orange', alpha=0.3)
            ax2.set_title("Remixed Envelope with Chorus")
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Volume")
            st.pyplot(fig2)
