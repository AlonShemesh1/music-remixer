# app.py

import streamlit as st
from utils.audio_processor import (
    load_audio,
    save_audio,
    plot_volume_envelope,
    detect_chorus,
    apply_loops
)
import tempfile
import os
from time import sleep

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload a song (MP3/WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_input:
        temp_input.write(uploaded_file.read())
        song_path = temp_input.name

    try:
        st.subheader("Original Song")
        song = load_audio(song_path)
        st.audio(song_path)

        st.subheader("Original Volume Envelope")
        plot_volume_envelope(song)

        main_loops = {
            "Hip-Hop": "beats/hiphop_main.mp3",
            "Reggae": "beats/reggae_main.mp3",
            "Rock": "beats/rock_main.mp3"
        }

        chorus_loops = {
            "Hip-Hop": "beats/hiphop_chorus.mp3",
            "Reggae": "beats/reggae_chorus.mp3",
            "Rock": "beats/rock_chorus.mp3"
        }

        main_loop_path = main_loops[style]
        chorus_loop_path = chorus_loops[style]

        if st.button("Remix"):
            with st.spinner("Detecting chorus and remixing..."):
                for i in range(1, 101, 10):
                    sleep(0.1)
                    st.progress(i)
                chorus_start, chorus_duration = detect_chorus(song_path)
                chorus_end = chorus_start + chorus_duration

                remixed = apply_loops(
                    song,
                    main_loop_path,
                    chorus_loop_path,
                    chorus_start,
                    chorus_end,
                    loop_gain_db=loop_volume
                )

                st.success("🎉 Remix complete!")
                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_output:
                    output_path = temp_output.name
                    save_audio(remixed, output_path)
                    st.audio(output_path)
                    with open(output_path, "rb") as f:
                        st.download_button("Download Remixed Song", f, "remixed.mp3")

    except Exception as e:
        st.error(f"Error processing the file: {e}")
    finally:
        os.remove(song_path)
