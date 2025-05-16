# app.py
import streamlit as st
import os
from utils.audio_processor import (
    get_volume_envelope,
    get_chorus_intervals,
    process_audio,
    plot_envelope_with_chorus
)

st.set_page_config(page_title="Music Remixer", layout="wide")
st.title("🎵 Music Remixer App")

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

uploaded_file = st.file_uploader("Upload a song (MP3)", type=["mp3"])
style = st.selectbox("Choose a remix style", ["Hip-Hop", "Reggae", "Rock"])

if uploaded_file:
    song_path = os.path.join("uploads", uploaded_file.name)

    # Save the uploaded file safely
    with open(song_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Confirm file exists before continuing
    if not os.path.exists(song_path):
        st.error("❌ Failed to save the uploaded file.")
    else:
        st.audio(song_path)

        sr = 22050
        envelope = get_volume_envelope(song_path, sr)
        chorus_times = get_chorus_intervals(song_path)

        st.subheader("🔍 Original Volume Envelope")
        plot_envelope_with_chorus(envelope, sr, chorus_times, title="Original Envelope")

        if st.button("🎛 Remix"):
            with st.spinner("Processing remix..."):
                try:
                    audio_output_path, envelope_after = process_audio(song_path, style, chorus_times)
                    st.success("Remix complete!")
                    st.audio(audio_output_path)

                    st.subheader("🎚 Remixed Volume Envelope")
                    plot_envelope_with_chorus(envelope_after, sr, chorus_times, title="Remixed Envelope")
                except FileNotFoundError as e:
                    st.error(f"❌ Missing loop file: {e}")
                except Exception as e:
                    st.error(f"❌ An error occurred during remixing: {e}")
