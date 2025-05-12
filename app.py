import streamlit as st
from utils.audio_processor import (
    load_audio, save_audio, plot_volume_envelope, apply_loops_with_chorus
)
import os
import tempfile

st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Electronic", "Funky"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

main_loops = {
    "Hip-Hop": "beats/hiphop_loop.mp3",
    "Electronic": "beats/electro_loop.mp3",
    "Funky": "beats/funky_loop.mp3"
}

chorus_loops = {
    "Hip-Hop": "beats/hiphop_chorus.mp3",
    "Electronic": "beats/electro_chorus.mp3",
    "Funky": "beats/funky_chorus.mp3"
}

if uploaded_file:
    st.subheader("Original Song")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_song:
        temp_song.write(uploaded_file.read())
        song_path = temp_song.name

    song = load_audio(song_path)
    st.audio(song_path)
    plot_volume_envelope(song)

    if st.button("Remix"):
        with st.spinner("Remixing in progress..."):
            st.info("Applying loops...")
            main_loop = main_loops[style]
            chorus_loop = chorus_loops[style]

            remixed = apply_loops_with_chorus(
                song,
                main_loop_path=main_loop,
                chorus_loop_path=chorus_loop,
                loop_gain_db=loop_volume
            )

            progress = st.progress(0)
            for i in range(100):
                progress.progress(i + 1)

            st.success("Remix complete
