import streamlit as st
import os
import tempfile
import shutil
from utils.audio_processor import (
    load_audio, save_audio, get_bpm, get_chorus_intervals,
    mix_with_chorus_loop, plot_volume_envelope
)

st.set_page_config(page_title="Music Remixer", layout="centered")

st.title("🎵 Music Remixer")
st.markdown("Upload a song and choose a remix style. Chorus will be detected and looped differently.")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Select remix style", ["Hip-Hop", "Reggae", "Rock"])
remix_button = st.button("🎛️ Remix")

# Map styles to loop files
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

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.subheader("Original Volume Envelope")
        y = load_audio(file_path)
        chorus_times = get_chorus_intervals(file_path)
        plot_volume_envelope(y, title="Original Audio", chorus_times=chorus_times)

        if remix_button:
            with st.spinner("Remixing..."):
                bpm = get_bpm(file_path)
                remixed = mix_with_chorus_loop(
                    song=y,
                    main_loop_path=loop_paths[style]["main"],
                    chorus_loop_path=loop_paths[style]["chorus"],
                    chorus_times=chorus_times,
                    bpm=bpm,
                    volume_db=-3
                )

                output_path = os.path.join(tmpdir, "remixed.wav")
                save_audio(remixed, output_path)

                st.success("✅ Remix complete!")
                st.audio(output_path)

                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed, title="Remixed Audio", chorus_times=chorus_times)
