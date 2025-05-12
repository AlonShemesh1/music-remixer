# app.py
import streamlit as st
from utils.audio_processor import (
    load_audio,
    mix_with_beat,
    save_audio,
    plot_volume_envelope
)

st.set_page_config(page_title="Music Remixer")
st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])

style = st.selectbox("Select a beat style to add:", ["hiphop", "rock", "reggae"])
loop_volume = st.slider("Loop Volume (dB)", min_value=-20, max_value=10, value=0)

if uploaded_file:
    try:
        song = load_audio(uploaded_file)
        st.audio(uploaded_file)

        # Show volume envelope of original song
        st.subheader("Original Song Volume Envelope")
        plot_volume_envelope(song)

    if style == "Hip-Hop":
    beat_path = "beats/hiphop_loop.mp3"
elif style == "Reggae":
    beat_path = "beats/reggae_loop.mp3"
elif style == "Rock":
    beat_path = "beats/rock_loop.mp3"


        if st.button("Remix it!"):
            remixed = mix_with_beat(song, beat_path, loop_gain_db=loop_volume)
            output_path = "output/remixed_song.mp3"
            save_audio(remixed, output_path)

            st.success("Remix complete!")
            audio_file = open(output_path, "rb")
            st.audio(audio_file.read(), format="audio/mp3")

    except Exception as e:
        st.error(f"Error processing the file: {e}")
