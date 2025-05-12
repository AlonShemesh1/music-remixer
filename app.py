import streamlit as st
from utils.audio_processor import (
    load_audio, save_audio, mix_with_beat, get_bpm, plot_volume_envelope
)
import tempfile
import os

st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_song:
        temp_song.write(uploaded_file.read())
        song_path = temp_song.name

    try:
        st.subheader("Original Song")
        song = load_audio(song_path)
        st.audio(song_path)

        bpm = get_bpm(song_path)
        st.write(f"Detected BPM: {bpm}")

        style
        style = st.selectbox("Select Loop Style", ["Hip-Hop", "Electronic", "Funky"])
        loop_file_map = {
            "Hip-Hop": "beats/hiphop_beat.mp3",
            "Electronic": "beats/electro_beat.mp3",
            "Funky": "beats/funky_beat.mp3"
        }

        beat_path = loop_file_map[style]
        beat_bpm = 100  # adjust to match your beat's original BPM

        remixed = mix_with_beat(song, beat_path, bpm, beat_bpm, loop_gain_db=loop_volume)

        st.subheader("Volume Envelope")
        plot_volume_envelope(remixed)

        st.subheader("Remixed Song")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_output:
            output_path = temp_output.name
        save_audio(remixed, output_path)
        st.audio(output_path)

        with open(output_path, "rb") as f:
            st.download_button("Download Remixed Song", f, file_name="remixed.mp3")

    except Exception as e:
        st.error(f"Error processing the file: {e}")
    finally:
        os.remove(song_path)
        if os.path.exists(output_path):
            os.remove(output_path)
