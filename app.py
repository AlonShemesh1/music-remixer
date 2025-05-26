import streamlit as st
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os
import time

from utils.audio_processor import get_volume_envelope, detect_chorus_intervals, remix_audio

st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎧 Music Remixer App")
st.markdown("Upload a song, choose a style, and remix it with smart chorus detection!")

# קלט קובץ שיר
uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])

# סגנון
style = st.selectbox("Choose remix style", ["Hip-Hop", "Rock", "Reggae"])

# אם הועלה קובץ
if uploaded_file is not None:
    # שמירה זמנית
    song_path = f"temp_song.{uploaded_file.name.split('.')[-1]}"
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())

    # טעינה
    y, sr = librosa.load(song_path, sr=None)
    envelope = get_volume_envelope(y)

    # זיהוי פזמון
    chorus_times = detect_chorus_intervals(y, sr)

    # גרף לפני רמיקס
    st.subheader("🔊 Volume Envelope (Original)")
    fig, ax = plt.subplots()
    times = np.linspace(0, len(y) / sr, num=len(envelope))
    ax.plot(times, envelope, label="Volume")
    for start, end in chorus_times:
        ax.axvspan(start, end, color='red', alpha=0.3, label="Chorus")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume")
    ax.set_title("Original Song Structure")
    ax.legend()
    st.pyplot(fig)

    # כפתור רמיקס
    if st.button("🎛️ Remix"):
        with st.spinner("Remixing in progress..."):
            progress = st.progress(0)
            for i in range(1, 6):
                time.sleep(0.3)
                progress.progress(i * 20)

            output_path = remix_audio(song_path, style, chorus_times)

        st.success("Remix complete! 🎉")
        st.audio(output_path)

        # טעינת שיר מרומקס
        y_remix, _ = librosa.load(output_path, sr=sr)
        envelope_remix = get_volume_envelope(y_remix)

        st.subheader("🎶 Volume Envelope (Remixed)")
        fig2, ax2 = plt.subplots()
        times2 = np.linspace(0, len(y_remix) / sr, num=len(envelope_remix))
        ax2.plot(times2, envelope_remix, label="Volume (Remixed)", color='green')
        for start, end in chorus_times:
            ax2.axvspan(start, end, color='orange', alpha=0.3, label="Chorus")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Volume")
        ax2.set_title("Remixed Song Structure")
        ax2.legend()
        st.pyplot(fig2)
