import streamlit as st
import os
from utils.audio_processor import (
    load_audio,
    save_audio,
    mix_with_beats_and_chorus,
    plot_volume_envelope_with_chorus,
    detect_chorus_intervals
)
from pydub import AudioSegment
import tempfile
import time

st.set_page_config(page_title="🎧 Music Remixer", layout="centered")
st.title("🎵 Music Remixer")

# File upload
uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])

# Style selection
style = st.selectbox("Choose a remix style:", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop volume (dB)", min_value=-20, max_value=10, value=0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(uploaded_file.read())
        song_path = temp_file.name

    try:
        song = load_audio(song_path)
        st.audio(song_path)

        st.subheader("🔊 Original Audio Volume Envelope")
        chorus_intervals = detect_chorus_intervals(song_path)
        plot_volume_envelope_with_chorus(song, chorus_intervals)

        # Map style to loop paths
        style_key = style.lower()
        main_loop_path = f"beats/{style_key}_main.mp3"
        chorus_loop_path = f"beats/{style_key}_chorus.mp3"

        if not os.path.exists(main_loop_path) or not os.path.exists(chorus_loop_path):
            st.error(f"Missing loop files for {style} style.")
        else:
            if st.button("🎛 Remix It!"):
                with st.spinner("Remixing in progress..."):
                    progress_bar = st.progress(0)
                    for i in range(5):
                        time.sleep(0.3)
                        progress_bar.progress((i + 1) * 20)

                    remixed = mix_with_beats_and_chorus(song, main_loop_path, chorus_loop_path, chorus_intervals, loop_volume)

                    os.makedirs("output", exist_ok=True)
                    output_path = "output/remixed_song.mp3"
                    save_audio(remixed, output_path)

                    st.success("✅ Remix complete!")
                    st.audio(output_path, format="audio/mp3")

                    st.subheader("🎨 Remixed Volume Envelope")
                    plot_volume_envelope_with_chorus(remixed, chorus_intervals)

    except Exception as e:
        st.error(f"Error processing the file: {e}")
