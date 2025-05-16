import streamlit as st
import os
import tempfile
import librosa
import numpy as np

from utils.audio_processor import (
    load_audio,
    save_audio,
    mix_with_chorus_loop,
    get_bpm,
    get_chorus_intervals,
    plot_volume_envelope,
    insert_loops
)

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer with Chorus Detection")

uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(uploaded_file.read())
        song_path = temp_file.name

    song = load_audio(song_path)
    st.audio(song_path)
    st.subheader("Original Song Volume Envelope")
    plot_volume_envelope(song)

    loop_paths = {
        "Hip-Hop": {
            "main": "beats/hiphop_main.mp3",
            "chorus": "beats/hiphop_chorus.mp3"
        },
        "Reggae": {
            "main": "beats/reggae_main.mp3",
            "chorus": "beats/reggae_chorus.mp3"
        },
        "Rock": {
            "main": "beats/rock_main.mp3",
            "chorus": "beats/rock_chorus.mp3"
        }
    }

    main_path = loop_paths[style]["main"]
    chorus_path = loop_paths[style]["chorus"]

    if not os.path.exists(main_path) or not os.path.exists(chorus_path):
        st.error(f"Missing loop files for {style}")
    else:
        with st.spinner("Detecting chorus and remixing..."):
            bpm = get_bpm(song_path)
            st.write(f"Detected BPM: {bpm}")
            chorus_times = get_chorus_intervals(song_path)

            main_loop = load_audio(main_path)
            chorus_loop = load_audio(chorus_path)

            remixed = mix_with_chorus_loop(song, main_loop, chorus_loop, chorus_times, bpm, loop_volume)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                output_path = out_file.name
                save_audio(remixed, output_path)

            st.success("✅ Remix complete!")
            st.subheader("Remixed Volume Envelope")
            plot_volume_envelope(remixed)
            st.audio(output_path, format="audio/mp3")

            with open(output_path, "rb") as f:
                st.download_button("Download Remixed Song", f, file_name="remixed_song.mp3")

    os.remove(song_path)
