import streamlit as st
import os
from utils.audio_processor import (
    process_audio,
    get_volume_envelope,
    get_chorus_intervals,
    plot_envelope_with_chorus
)

st.set_page_config(page_title="🎵 Music Remixer", layout="wide", page_icon="🎶")
st.markdown("""
    <style>
        .title-text {
            color: #4B8BBE;
            font-size: 42px;
            font-weight: bold;
        }
        .sub-header {
            font-size: 18px;
            color: #666;
        }
        .stProgress > div > div > div > div {
            background-color: #4B8BBE;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-text'>Music Remixer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload a song, choose a style, and remix it with highlighted chorus!</div>", unsafe_allow_html=True)

song_file = st.file_uploader("Upload your song", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])

if song_file:
    song_path = os.path.join("uploads", song_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(song_path, "wb") as f:
        f.write(song_file.read())

    st.audio(song_path, format="audio/mp3")

    st.markdown("### Original Volume Envelope")
    envelope_before = get_volume_envelope(song_path)
    chorus_times = get_chorus_intervals(song_path)
    fig_before = plot_envelope_with_chorus(envelope_before, chorus_times)
    st.plotly_chart(fig_before, use_container_width=True)

    if st.button("🎛 Remix"):
        with st.spinner("Processing remix..."):
            audio_output_path, envelope_after = process_audio(song_path, style, chorus_times)

        st.success("Remix complete!")
        st.audio(audio_output_path, format="audio/mp3")

        st.markdown("### Remixed Volume Envelope")
        fig_after = plot_envelope_with_chorus(envelope_after, chorus_times)
        st.plotly_chart(fig_after, use_container_width=True)
