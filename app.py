# app.py
import streamlit as st
import os
import tempfile

from utils.audio_processor import (
    load_audio,
    mix_with_beat,
    save_audio,
    plot_volume_envelope
    plot_volume_envelope,
    get_bpm,
    plot_waveform
)
import os

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer")
@@ -16,16 +20,24 @@
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_song:
        temp_song.write(uploaded_file.read())
        song_path = temp_song.name

    try:
        # Load original song
        song = load_audio(uploaded_file)
        st.audio(uploaded_file)
        song = load_audio(song_path)
        st.audio(song_path)
        st.success("Original audio loaded successfully!")

        bpm = get_bpm(song_path)
        st.write(f"Estimated BPM: {bpm} BPM")

        st.subheader("Original Volume Envelope")
        plot_volume_envelope(song)

        # Choose beat path
        st.subheader("Original Waveform")
        plot_waveform(song_path)

        beat_path = None
        if style == "Hip-Hop":
            beat_path = "beats/hiphop_loop.mp3"
@@ -39,7 +51,7 @@
        else:
            if st.button("Remix it!"):
                remixed = mix_with_beat(song, beat_path, loop_gain_db=loop_volume)
                

                os.makedirs("output", exist_ok=True)
                output_path = "output/remixed_song.mp3"
                save_audio(remixed, output_path)
@@ -48,8 +60,10 @@
                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed)

                with open(output_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                    st.download_button("Download Remix", audio_file, file_name="remixed_song.mp3")
                st.audio(output_path, format="audio/mp3")
                with open(output_path, "rb") as f:
                    st.download_button("Download Remix", f, file_name="remixed_song.mp3")
    except Exception as e:
        st.error(f"Error processing the file: {e}")
    finally:
        os.remove(song_path)
