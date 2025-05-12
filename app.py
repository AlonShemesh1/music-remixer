import streamlit as st
import os
import tempfile
from utils.audio_processor import (
    load_audio, save_audio, match_loop_to_bpm, get_bpm,
    detect_chorus_intervals, mix_loops, plot_volume_envelope
)
from pydub import AudioSegment
import time

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎶 Auto Chorus Remixer")

uploaded_file = st.file_uploader("Upload a song (MP3/WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

# Map style to main and chorus loops
loop_map = {
    "Hip-Hop": {
        "main": "beats/hiphop_main.mp3",
        "chorus": "beats/hiphop_ditty.mp3"
    },
    "Reggae": {
        "main": "beats/reggae_main.mp3",
        "chorus": "beats/reggae_ditty.mp3"
    },
    "Rock": {
        "main": "beats/rock_main.mp3",
        "chorus": "beats/rock_ditty.mp3"
    }
}

# Preview the loops
st.subheader("🎧 Loop Preview")
main_loop_audio = loop_map[style]["main"]
chorus_loop_audio = loop_map[style]["chorus"]
st.audio(main_loop_audio, format="audio/mp3", start_time=0)
st.audio(chorus_loop_audio, format="audio/mp3", start_time=0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_song:
        temp_song.write(uploaded_file.read())
        song_path = temp_song.name

    try:
        song = load_audio(song_path)
        st.audio(song_path, format="audio/mp3")

        st.subheader("Original Volume Envelope")
        plot_volume_envelope(song)

        bpm = get_bpm(song_path)
        st.write(f"Detected BPM: `{bpm} BPM`")

        chorus_start, chorus_end = detect_chorus_intervals(song_path)
        st.success(f"Chorus estimated at {chorus_start/1000:.2f}s to {chorus_end/1000:.2f}s")

        if st.button("🎛️ Remix"):
            with st.spinner("Remixing..."):
                # Show a fake progress bar
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress.progress(i + 1)

                main_loop = match_loop_to_bpm(AudioSegment.from_file(main_loop_audio), 100, bpm)
                chorus_loop = match_loop_to_bpm(AudioSegment.from_file(chorus_loop_audio), 100, bpm)

                remixed = mix_loops(song, main_loop, chorus_loop, chorus_start, chorus_end, gain_db=loop_volume)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                    output_path = out_file.name
                save_audio(remixed, output_path)

                st.success("Remix complete! 🎉")
                st.audio(output_path)

                st.subheader("🎨 Remixed Volume Envelope")
                plot_volume_envelope(remixed, chorus_start=chorus_start, chorus_end=chorus_end)

                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download Remixed Song", f, file_name="remixed.mp3")

    except Exception as e:
        st.error(f"Error: {e}")
