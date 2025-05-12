import streamlit as st
from utils.audio_processor import load_audio, mix_with_beat, save_audio, plot_volume_envelope
import os
from pydub import AudioSegment

st.set_page_config(page_title="🎵 Dual Loop Remixer", layout="centered")
st.title("🎵 Dual Loop Remixer")

# Upload
uploaded_file = st.file_uploader("Upload your full song (MP3/WAV)", type=["mp3", "wav"])
style = st.selectbox("Select remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

if uploaded_file:
    try:
        # Load song
        song = load_audio(uploaded_file)
        st.audio(uploaded_file, format="audio/mp3")
        st.success("✅ Song loaded successfully!")

        # Segment song
        duration_ms = len(song)
        ditty_duration = 10000  # First 10 seconds
        house_duration = 10000  # Last 10 seconds

        if duration_ms < (ditty_duration + house_duration):
            st.error("Song must be at least 20 seconds long to apply both loops.")
        else:
            intro = song[:ditty_duration]
            middle = song[ditty_duration:-house_duration]
            outro = song[-house_duration:]

            # Loop paths
            ditty_path = f"beats/{style.lower()}_ditty_loop.mp3"
            house_path = f"beats/{style.lower()}_house_loop.mp3"

            # Check if loop files exist
            if not os.path.exists(ditty_path):
                st.error(f"Missing Ditty loop: {ditty_path}")
            elif not os.path.exists(house_path):
                st.error(f"Missing House loop: {house_path}")
            else:
                # Remix intro and outro
                remixed_intro = mix_with_beat(intro, ditty_path, loop_gain_db=loop_volume)
                remixed_outro = mix_with_beat(outro, house_path, loop_gain_db=loop_volume)

                # Combine segments
                final_mix = remixed_intro + middle + remixed_outro

                # Save and output
                os.makedirs("output", exist_ok=True)
                output_path = "output/remixed_song.mp3"
                save_audio(final_mix, output_path)

                st.success("🎉 Remix complete!")
                st.audio(output_path, format="audio/mp3")
                st.download_button("Download Remixed Song", open(output_path, "rb"), file_name="remixed_song.mp3")

                # Show volume envelope
                st.subheader("Volume Envelope")
                plot_volume_envelope(final_mix)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
