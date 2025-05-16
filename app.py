import streamlit as st
import os
import tempfile
import librosa
import numpy as np

def get_chorus_intervals(file_path, sr=22050, k=4):
    y, _ = librosa.load(file_path, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    boundaries = librosa.segment.agglomerative(chroma, k=k)
    times = librosa.frames_to_time(boundaries, sr=sr)
    return times.tolist()

import os
from utils.audio_processor import (
    load_audio, save_audio, get_chorus_intervals,
    insert_loops, plot_volume_envelope
    load_audio,
    save_audio,
    mix_with_chorus_loop,
    get_bpm,
    get_chorus_intervals,
    plot_volume_envelope
)

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer with Chorus Detection")
st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])

uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(uploaded_file.read())
        song_path = temp_file.name

    song = load_audio(song_path)
    st.audio(song_path)
    st.subheader("Original Song Volume")
    plot_volume_envelope(song)

    # Load loops
    loop_files = {
        "Hip-Hop": ("beats/hiphop_main.mp3", "beats/hiphop_chorus.mp3"),
        "Reggae": ("beats/reggae_main.mp3", "beats/reggae_chorus.mp3"),
        "Rock": ("beats/rock_main.mp3", "beats/rock_chorus.mp3")
    }
    with st.spinner("Analyzing song..."):
        song = load_audio(song_path)
        bpm = get_bpm(song_path)
        st.write(f"Detected BPM: {bpm}")

        # Load loop files for the selected style
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

    main_path, chorus_path = loop_files[style]
    if not os.path.exists(main_path) or not os.path.exists(chorus_path):
        st.error(f"Missing loop files for {style}")
    else:
        main_loop = load_audio(main_path) + loop_volume
        chorus_loop = load_audio(chorus_path) + loop_volume
        main_loop = loop_paths[style]["main"]
        chorus_loop = loop_paths[style]["chorus"]

        st.subheader("Original Song Volume Envelope")
        plot_volume_envelope(song)

        if st.button("Remix"):
            with st.spinner("Detecting chorus and remixing..."):
            with st.spinner("Detecting chorus and applying loops..."):
                chorus_times = get_chorus_intervals(song_path)
                remixed = insert_loops(song, main_loop, chorus_loop, chorus_times)

                st.subheader("Remixed Volume")
                plot_volume_envelope(remixed)
                remixed = mix_with_chorus_loop(song, main_loop, chorus_loop, chorus_times, bpm, loop_volume)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
                    output_path = out.name
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                    output_path = out_file.name
                    save_audio(remixed, output_path)

                st.success("🎉 Remix complete!")
                st.audio(output_path)
                st.success("✅ Remix complete!")
                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed)
                st.audio(output_path, format="audio/mp3")

                with open(output_path, "rb") as f:
                    st.download_button("Download Remixed Song", f, "remixed_song.mp3")
                    st.download_button("Download Remixed Song", f, file_name="remixed_song.mp3")

    os.remove(song_path)
