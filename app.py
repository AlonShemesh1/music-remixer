import streamlit as st
import os
import tempfile
import matplotlib.pyplot as plt

from utils.audio_processor import (
    load_audio,
    mix_with_beat,
    save_audio,
    plot_volume_envelope
)

st.set_page_config(page_title="🎶 Simple Music Remixer", layout="wide")
st.title("🎶 Simple Music Remixer")

# Optional header image
if os.path.exists("piano.jpg"):
    st.image("piano.jpg", use_container_width=True)

# 1️⃣ Upload and settings
uploaded_file = st.file_uploader("Upload your song (MP3/WAV)", type=["mp3", "wav"])
genre = st.selectbox("Choose remix style:", ["Reggae", "Hip-Hop", "Rock"])
loop_volume = st.slider(
    "Loop Beat Volume (dB)",
    min_value=-20,
    max_value=5,
    value=-3,
    help="Adjust how loud the loop beat is mixed with your song."
)

if uploaded_file:
    # Play original
    st.subheader("Original Song")
    st.audio(uploaded_file, format=f"audio/{uploaded_file.type.split('/')[-1]}")
    
    # Load and plot its volume envelope
    song = load_audio(uploaded_file)
    fig_orig = plot_volume_envelope(song, title="Original Song Volume Over Time")
    st.pyplot(fig_orig)
    
    # 2️⃣ Remix button
    if st.button("🎛️ Remix it!"):
        with st.spinner("Processing remix..."):
            # Determine beat file path
            beat_map = {
                "Reggae":   "beats/reggae_loop.mp3",
                "Hip-Hop":  "beats/hiphop_loop.mp3",
                "Rock":     "beats/rock_loop.mp3",
            }
            beat_path = beat_map.get(genre)
            if not beat_path or not os.path.exists(beat_path):
                st.error(f"Loop file not found: {beat_path}")
                st.stop()
            
            # Load beat and debug lengths
            beat = load_audio(beat_path)
            st.write("📏 Original song length (ms):", len(song))
            st.write("📏 Loop beat length (ms):",    len(beat))
            
            # Mix with user-defined loop volume
            remixed = mix_with_beat(song, beat, volume=loop_volume)
            
            # Save, play, download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                save_audio(remixed, tmp.name)
                st.success("✅ Remix ready!")
                st.audio(tmp.name, format="audio/mp3")
                st.download_button(
                    label="💾 Download Remixed Song",
                    data=open(tmp.name, "rb"),
                    file_name=f"remixed_{uploaded_file.name}",
                    mime="audio/mp3"
                )
            
            # Plot volume envelope of the remixed track
            fig_remix = plot_volume_envelope(remixed, title="Remixed Song Volume Over Time")
            st.pyplot(fig_remix)
