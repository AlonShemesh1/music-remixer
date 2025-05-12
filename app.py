import streamlit as st
import os
from pydub import AudioSegment
from utils.audio_processor import (
    load_audio,
    mix_with_beat,
    save_audio,
    plot_volume_envelope
)

st.set_page_config(page_title="🎵 Remix with Chorus Loop", layout="centered")
st.title("🎵 Remix with Different Chorus Loop")

uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose music style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

# Chorus timing input
chorus_start_sec = st.number_input("Chorus Start Time (seconds)", min_value=0, value=40)
chorus_duration_sec = st.number_input("Chorus Duration (seconds)", min_value=5, value=20)

if uploaded_file:
    try:
        song = load_audio(uploaded_file)
        st.audio(uploaded_file, format="audio/mp3")
        st.success("✅ Song loaded successfully!")

        # Calculate start and end times in milliseconds
        chorus_start = chorus_start_sec * 1000
        chorus_end = chorus_start + (chorus_duration_sec * 1000)

        if len(song) < chorus_end:
            st.error("❌ The chorus section is longer than the song length.")
        else:
            # Split the song
            intro = song[:chorus_start]
            chorus = song[chorus_start:chorus_end]
            outro = song[chorus_end:]

            # Loop file paths
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

            # Check if loops exist
            if not os.path.exists(main_loop):
                st.error(f"❌ Main loop not found: {main_loop}")
            elif not os.path.exists(chorus_loop):
                st.error(f"❌ Chorus loop not found: {chorus_loop}")
            else:
                # Mix parts with their loops
                intro_mixed = mix_with_beat(intro, main_loop, loop_gain_db=loop_volume)
                chorus_mixed = mix_with_beat(chorus, chorus_loop, loop_gain_db=loop_volume)
                outro_mixed = mix_with_beat(outro, main_loop, loop_gain_db=loop_volume)

                # Combine into one track
                final_mix = intro_mixed + chorus_mixed + outro_mixed

                # Save output
                os.makedirs("output", exist_ok=True)
                output_path = "output/remixed_with_chorus.mp3"
                save_audio(final_mix, output_path)

                st.success("🎉 Remix created successfully!")
                st.audio(output_path, format="audio/mp3")
                st.download_button("📥 Download Remix", open(output_path, "rb"), file_name="remixed_with_chorus.mp3")

                # Display volume chart
                st.subheader("Volume Envelope")
                plot_volume_envelope(final_mix)

    except Exception as e:
        st.error(f"Error: {e}")
