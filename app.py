import streamlit as st
import os
import tempfile
from utils.audio_processor import (
    get_volume_envelope,
    get_chorus_intervals,
    remix_song_with_chorus_loop,
    plot_volume_envelope
)

st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎧 Music Remixer with Chorus Loop")

# Upload section
uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose a remix style", ["Hip-Hop", "Reggae", "Rock"])

# File paths for loops
loop_paths = {
    "Hip-Hop": {
        "main": "loops/hiphop_main.mp3",
        "chorus": "loops/hiphop_chorus.mp3"
    },
    "Reggae": {
        "main": "loops/reggae_main.mp3",
        "chorus": "loops/reggae_chorus.mp3"
    },
    "Rock": {
        "main": "loops/rock_main.mp3",
        "chorus": "loops/rock_chorus.mp3"
    },
}

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name

    st.audio(song_path, format="audio/mp3")

    st.subheader("🔍 Original Volume Envelope")
    original_envelope, sr = get_volume_envelope(song_path)
    chorus_times = get_chorus_intervals(song_path)
    plot_volume_envelope(original_envelope, sr, chorus_times, title="Original Song Envelope")

    if st.button("🎶 Remix"):
        with st.spinner("Remixing..."):
            output_path = remix_song_with_chorus_loop(
                song_path,
                loop_paths[style]["main"],
                loop_paths[style]["chorus"],
                chorus_times
            )
            st.success("✅ Remix complete!")

        st.audio(output_path, format="audio/mp3")
        st.subheader("🎚️ Remixed Volume Envelope")
        remixed_envelope, _ = get_volume_envelope(output_path)
        plot_volume_envelope(remixed_envelope, sr, chorus_times, title="Remixed Song Envelope")
