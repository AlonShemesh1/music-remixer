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
from utils.audio_processor import load_audio, mix_with_beat, save_audio, plot_volume_envelope
import os

st.set_page_config(page_title="Music Remixer", layout="centered")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
st.title("🎵 Music Remixer")

style = st.selectbox("Select a beat style to add:", ["hiphop", "rock", "reggae"])
loop_volume = st.slider("Loop Volume (dB)", min_value=-20, max_value=10, value=0)
uploaded_file = st.file_uploader("Upload a WAV or MP3 file", type=["wav", "mp3"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

if uploaded_file:
if uploaded_file is not None:
    try:
        song = load_audio(uploaded_file)
        st.audio(uploaded_file)
        st.success("Original audio loaded successfully!")
        st.audio(uploaded_file, format="audio/mp3")

        # Show volume envelope of original song
        st.subheader("Original Song Volume Envelope")
        # Show volume envelope
        st.subheader("Original Audio Volume Envelope")
        plot_volume_envelope(song)

        # Choose beat path
        if style == "Hip-Hop":
            beat_path = "beats/hiphop_loop.mp3"
        elif style == "Reggae":
            beat_path = "beats/reggae_loop.mp3"
        elif style == "Rock":
            beat_path = "beats/rock_loop.mp3"
    except Exception as e:
    st.error(f"Error: {e}")




        if st.button("Remix it!"):
            remixed = mix_with_beat(song, beat_path, loop_gain_db=loop_volume)
            output_path = "output/remixed_song.mp3"
            save_audio(remixed, output_path)

            st.success("Remix complete!")
            audio_file = open(output_path, "rb")
            st.audio(audio_file.read(), format="audio/mp3")

        else:
            st.error("Unknown style selected.")
            beat_path = None

        # Process the remix
        if beat_path and os.path.exists(beat_path):
            if st.button("Remix it!"):
                remixed = mix_with_beat(song, beat_path, loop_gain_db=loop_volume)
                output_path = "output/remixed_song.mp3"
                os.makedirs("output", exist_ok=True)
                save_audio(remixed, output_path)

                st.success("🎉 Remix complete!")
                st.audio(output_path, format="audio/mp3")

                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed)
        else:
            st.error(f"Loop file not found: {beat_path}")
    except Exception as e:
        st.error(f"Error processing the file: {e}")
