# app.py
import streamlit as st
import os
from utils.audio_processor import (
    process_audio,
    get_volume_envelope,
    get_chorus_intervals,
    plot_envelope_with_chorus
)

st.set_page_config(page_title="🎵 Music Remixer", layout="wide", page_icon="🎶")
st.title("🎧 AI Music Remixer")
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 18px;
    }
    .stProgress>div>div>div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a song", type=["mp3"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_file = st.file_uploader("Upload chorus loop (mp3)", type=["mp3"], key="chorus")

if uploaded_file and loop_file:
    with st.spinner("Analyzing audio and detecting chorus..."):
        song_path = os.path.join("/mnt/data", uploaded_file.name)
        chorus_loop_path = os.path.join("/mnt/data", loop_file.name)
        with open(song_path, "wb") as f:
            f.write(uploaded_file.read())
        with open(chorus_loop_path, "wb") as f:
            f.write(loop_file.read())

        envelope_before = get_volume_envelope(song_path)
        chorus_times = get_chorus_intervals(song_path)

    st.subheader("🔊 Volume Envelope Before Remix")
    fig_before = plot_envelope_with_chorus(envelope_before, chorus_times)
    st.plotly_chart(fig_before, use_container_width=True)

    if st.button("🎛️ Remix Song"):
        with st.spinner("Remixing in progress..."):
            audio_output_path, envelope_after = process_audio(song_path, style, chorus_times, chorus_loop_path)

        st.audio(audio_output_path, format="audio/mp3")

        st.subheader("🎚️ Volume Envelope After Remix")
        fig_after = plot_envelope_with_chorus(envelope_after, chorus_times)
        st.plotly_chart(fig_after, use_container_width=True)

# utils/audio_processor.py
import librosa
import numpy as np
import soundfile as sf
import plotly.graph_objects as go


def get_volume_envelope(audio_path):
    y, sr = librosa.load(audio_path)
    frame_length = 1024
    hop_length = 512
    envelope = np.abs(librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length))
    times = librosa.frames_to_time(np.arange(len(envelope)), sr=sr, hop_length=hop_length)
    return list(zip(times, envelope))


def get_chorus_intervals(audio_path):
    y, sr = librosa.load(audio_path)
    chroma = librosa.feature.chroma_cens(y=y, sr=sr)
    recurrence = librosa.segment.recurrence_matrix(chroma, mode='affinity', sym=True)
    path_sim = librosa.segment.path_enhance(recurrence)
    boundaries = librosa.segment.agglomerative(path_sim, k=4)
    segment_times = librosa.frames_to_time(boundaries, sr=sr)
    chorus_idx = np.argmax(np.diff(segment_times))  # longest segment as chorus
    return [(segment_times[chorus_idx], segment_times[chorus_idx + 1])]


def plot_envelope_with_chorus(envelope, chorus_times):
    times, values = zip(*envelope)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', name='Volume Envelope', line=dict(color='blue')))

    for start, end in chorus_times:
        fig.add_vrect(x0=start, x1=end, fillcolor='rgba(255,0,0,0.3)', layer='below', line_width=0)

    fig.update_layout(title="Volume Envelope", xaxis_title="Time (s)", yaxis_title="Amplitude")
    return fig


def process_audio(audio_path, style, chorus_times, loop_path):
    y, sr = librosa.load(audio_path, sr=None)
    loop_audio, _ = librosa.load(loop_path, sr=sr)

    for start, end in chorus_times:
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        segment_len = end_sample - start_sample
        loop_segment = np.tile(loop_audio, int(np.ceil(segment_len / len(loop_audio))))[:segment_len]
        y[start_sample:end_sample] = loop_segment

    output_path = "/mnt/data/remixed_output.mp3"
    sf.write(output_path, y, sr)

    envelope = get_volume_envelope(output_path)
    return output_path, envelope
