# app.py
import streamlit as st
from utils.audio_processor import (
    load_audio,
    mix_with_beat,
    save_audio,
    plot_volume_envelope
)
import os

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

if uploaded_file is not None:
    try:
        # Load original song
        song = load_audio(uploaded_file)
        st.audio(uploaded_file)
        st.success("Original audio loaded successfully!")

        st.subheader("Original Volume Envelope")
        plot_volume_envelope(song)

        # Choose beat path
        beat_path = None
        if style == "Hip-Hop":
            beat_path = "beats/hiphop_loop.mp3"
        elif style == "Reggae":
            beat_path = "beats/reggae_loop.mp3"
        elif style == "Rock":
            beat_path = "beats/rock_loop.mp3"

        if not os.path.exists(beat_path):
            st.error(f"Loop file not found: {beat_path}")
        else:
            if st.button("Remix it!"):
                remixed = mix_with_beat(song, beat_path, loop_gain_db=loop_volume)
                
                os.makedirs("output", exist_ok=True)
                output_path = "output/remixed_song.mp3"
                save_audio(remixed, output_path)

                st.success("🎉 Remix complete!")
                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed)

                with open(output_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                    st.download_button("Download Remix", audio_file, file_name="remixed_song.mp3")
    except Exception as e:
        st.error(f"Error processing the file: {e}")
