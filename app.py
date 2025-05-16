import streamlit as st
import os
from utils.audio_processor import (
    detect_chorus_sections,
    apply_remix_with_chorus_loop,
    plot_volume_envelope
)
import time

st.set_page_config(page_title="Music Remixer", layout="wide")
st.title("🎵 Music Remixing App")

style = st.selectbox("Choose a style:", ["Hip-Hop", "Reggae", "Rock"])
uploaded_file = st.file_uploader("Upload your MP3 file", type=["mp3"])

if uploaded_file:
    song_path = f"temp_uploads/{uploaded_file.name}"
    os.makedirs("temp_uploads", exist_ok=True)
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())

    st.audio(song_path, format="audio/mp3")

    # Show original volume graph
    st.subheader("🔊 Original Volume Envelope")
    chorus_times = detect_chorus_sections(song_path)
    plot_volume_envelope(song_path, chorus_times)

    if st.button("🎛️ Remix"):
        with st.spinner("Remixing in progress..."):
            progress_bar = st.progress(0)
            for pct in range(0, 100, 10):
                time.sleep(0.1)
                progress_bar.progress(pct + 10)

            main_loop = f"beats/{style.lower()}_main.mp3"
            chorus_loop = f"beats/{style.lower()}_chorus.mp3"

            try:
                remixed_path = apply_remix_with_chorus_loop(song_path, main_loop, chorus_loop, chorus_times)
                st.success("✅ Remix complete!")
                st.audio(remixed_path, format="audio/mp3")

                st.subheader("🎶 Remixed Volume Envelope")
                plot_volume_envelope(remixed_path, chorus_times)

            except Exception as e:
                st.error(f"Error during remixing: {e}")
