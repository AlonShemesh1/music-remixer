# app.py
import streamlit as st
import os
from utils.audio_processor import (
    load_audio,
    save_audio,
    mix_with_loops,
    detect_chorus,
    plot_volume_envelope
)
import tempfile

st.set_page_config(page_title="Music Remixer 🎵", layout="centered")
st.title("🎧 Auto-Remix Your Song")

uploaded_song = st.file_uploader("Upload your song (MP3/WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose Remix Style", ["Hip-Hop", "Electronic", "Reggae"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

if uploaded_song:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_input:
        temp_input.write(uploaded_song.read())
        temp_input_path = temp_input.name

    st.audio(temp_input_path)

    loop_paths = {
        "Hip-Hop": {
            "main": "beats/hiphop_main.mp3",
            "chorus": "beats/hiphop_chorus.mp3"
        },
        "Electronic": {
            "main": "beats/electro_main.mp3",
            "chorus": "beats/electro_chorus.mp3"
        },
        "Reggae": {
            "main": "beats/reggae_main.mp3",
            "chorus": "beats/reggae_chorus.mp3"
        }
    }

    if st.button("🎶 Remix Song"):
        try:
            song = load_audio(temp_input_path)
            chorus_start, chorus_end = detect_chorus(temp_input_path)
            st.success(f"Chorus detected at {chorus_start / 1000:.2f}s - {chorus_end / 1000:.2f}s")

            remixed = mix_with_loops(
                song,
                main_loop_path=loop_paths[style]["main"],
                chorus_loop_path=loop_paths[style]["chorus"],
                chorus_start=chorus_start,
                chorus_end=chorus_end,
                loop_gain_db=loop_volume
            )

            st.subheader("Volume Envelope")
            plot_volume_envelope(remixed)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_output:
                output_path = temp_output.name
            save_audio(remixed, output_path)

            st.subheader("Remixed Audio")
            st.audio(output_path)
            with open(output_path, "rb") as f:
                st.download_button("⬇️ Download Remixed Song", f, file_name="remixed.mp3")

        except Exception as e:
            st.error(f"Error: {e}")
