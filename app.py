import streamlit as st
import os
import time
from utils.audio_processor import (
    detect_chorus,
    apply_remix,
    plot_volume_envelope_with_chorus
)

st.set_page_config(page_title="Music Remixer", layout="wide")

st.title("🎶 AI Music Remixer")
st.markdown("Upload a song and choose a remix style. The app will detect the chorus and apply a different beat loop there.")

uploaded_file = st.file_uploader("Upload your song (MP3 format)", type=["mp3"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])

# File paths for beats
main_loop_path = f"beats/{style.lower()}_main.mp3"
chorus_loop_path = f"beats/{style.lower()}_chorus.mp3"

if uploaded_file:
    song_path = f"uploaded_{uploaded_file.name}"
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())
    st.audio(song_path, format="audio/mp3")

    # Detect chorus and show volume envelope immediately
    try:
        st.subheader("🔊 Volume Envelope with Chorus Highlighted")
        chorus_times = detect_chorus(song_path)
        fig = plot_volume_envelope_with_chorus(song_path, chorus_times)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error analyzing the audio: {e}")
        chorus_times = []

    # Remix button
    if st.button("🎛 Remix It!"):
        if not os.path.exists(main_loop_path) or not os.path.exists(chorus_loop_path):
            st.error("Loop files missing for this style.")
        else:
            with st.spinner("Remixing..."):
                progress = st.progress(0, text="Starting remix...")

                for i in range(5):
                    time.sleep(0.4)
                    progress.progress((i + 1) * 20, text=f"Processing {20*(i+1)}%")

                try:
                    remixed_path = apply_remix(
                        song_path,
                        main_loop_path,
                        chorus_loop_path,
                        chorus_times
                    )
                    st.success("✅ Remix complete!")
                    st.audio(remixed_path, format="audio/mp3")

                except Exception as e:
                    st.error(f"Error during remix: {e}")
