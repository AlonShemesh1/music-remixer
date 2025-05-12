import streamlit as st
import os
import tempfile
from utils.audio_processor import (
    load_audio,
    save_audio,
    mix_with_beat,
    detect_chorus,
    plot_volume_envelope
)

st.set_page_config(page_title="Auto Chorus Remixer", layout="centered")
st.title("🎵 Auto-Remix with Detected Chorus")

uploaded_file = st.file_uploader("Upload a song (MP3/WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose Music Style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        song = load_audio(tmp_path)
        st.audio(tmp_path, format="audio/mp3")

        st.subheader("Analyzing song structure...")
        chorus_start, chorus_end = detect_chorus(tmp_path)
        st.success(f"Chorus detected at {chorus_start//1000}s to {chorus_end//1000}s")

        # Split the song
        intro = song[:chorus_start]
        chorus = song[chorus_start:chorus_end]
        outro = song[chorus_end:]

        # Define loop paths
        loop_paths = {
            "Hip-Hop": {
                "main": "beats/hiphop_loop.mp3",
                "chorus": "beats/hiphop_chorus_loop.mp3"
            },
            "Reggae": {
                "main": "beats/reggae_loop.mp3",
                "chorus": "beats/reggae_chorus_loop.mp3"
            },
            "Rock": {
                "main": "beats/rock_loop.mp3",
                "chorus": "beats/rock_chorus_loop.mp3"
            }
        }

        main_loop = loop_paths[style]["main"]
        chorus_loop = loop_paths[style]["chorus"]

        # Mix each part
        intro_mixed = mix_with_beat(intro, main_loop, loop_gain_db=loop_volume)
        chorus_mixed = mix_with_beat(chorus, chorus_loop, loop_gain_db=loop_volume)
        outro_mixed = mix_with_beat(outro, main_loop, loop_gain_db=loop_volume)

        # Merge
        final_mix = intro_mixed + chorus_mixed + outro_mixed

        # Save and play
        os.makedirs("output", exist_ok=True)
        output_path = "output/remixed_chorus.mp3"
        save_audio(final_mix, output_path)

        st.success("✅ Remix complete with detected chorus!")
        st.audio(output_path, format="audio/mp3")
        st.download_button("📥 Download Remix", open(output_path, "rb"), file_name="remixed_chorus.mp3")

        st.subheader("Volume Envelope")
        plot_volume_envelope(final_mix)

    except Exception as e:
        st.error(f"Error: {e}")
