import streamlit as st
import time
import matplotlib.pyplot as plt
import numpy as np
from utils.audio_processor import process_audio, get_volume_envelope, get_chorus_intervals, plot_envelope_with_chorus

# Initialize session state
if "processing_times" not in st.session_state:
    st.session_state.processing_times = {}

st.title("🎧 Music Remixer with Timeline")

uploaded_file = st.file_uploader("Upload a song (MP3)", type=["mp3"])

style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")
    
    # Measure timing
    t0 = time.time()
    song_path = f"/tmp/{uploaded_file.name}"
    with open(song_path, "wb") as f:
        f.write(uploaded_file.read())
    t_load = time.time()

    st.markdown("### 🔊 Volume Envelope Before Remix")
    envelope_before = get_volume_envelope(song_path)
    chorus_times = get_chorus_intervals(song_path)
    fig_before = plot_envelope_with_chorus(envelope_before, chorus_times)
    st.pyplot(fig_before)
    t_plot = time.time()

    if st.button("🎛️ Remix"):
        with st.spinner("Remixing..."):
            audio_output_path, envelope_after = process_audio(song_path, style, chorus_times)
            t_process = time.time()

            st.success("Remix Complete!")

            st.markdown("### 🔊 Volume Envelope After Remix")
            fig_after = plot_envelope_with_chorus(envelope_after, chorus_times)
            st.pyplot(fig_after)

            st.markdown("### 📈 Processing Time Breakdown")
            times = {
                "Load file": t_load - t0,
                "Plot before": t_plot - t_load,
                "Remix process": t_process - t_plot,
                "Total": t_process - t0
            }

            st.session_state.processing_times = times

            st.write(times)

            # Plot as horizontal bar chart
            fig, ax = plt.subplots()
            labels = list(times.keys())
            values = list(times.values())
            ax.barh(labels, values, color="skyblue")
            ax.set_xlabel("Seconds")
            ax.set_title("Remix Processing Timeline")
            st.pyplot(fig)
