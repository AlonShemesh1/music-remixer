import streamlit as st
from pydub import AudioSegment
import librosa
import numpy as np
import os
# import matplotlib.pyplot as plt
import shutil
from io import BytesIO

# UI בסיסי
st.set_page_config(layout="wide", page_title="Music Transformer", page_icon="🎵")
st.markdown("<h1 style='text-align: center;'>🎶 Transform Your Song Into a New Genre</h1>", unsafe_allow_html=True)
st.image("piano.jpg", use_container_width=True)


uploaded_song = st.file_uploader("Upload your song", type=["mp3", "wav"])
genres = {
    "Hip Hop": "hiphop",
    "Reggae": "reggae",
    "Rock": "rock"
}
genre_name = st.selectbox("Select Genre", list(genres.keys()))
process_button = st.button("Transform Song")

def get_bpm(audio_path):
    y, sr = librosa.load(audio_path)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return float(tempo)

def detect_chorus_start(audio_path):
    y, sr = librosa.load(audio_path)
    energy = librosa.feature.rms(y=y)[0]
    avg_energy = np.mean(energy)
    for i in range(len(energy)):
        if energy[i] > avg_energy * 1.8:
            return int(librosa.frames_to_time(i, sr=sr) * 1000)
    return 30000

def sync_loops(song_bytes, loop_path, drum_path, bpm):
    song = AudioSegment.from_file(song_bytes)
    loop = AudioSegment.from_file(loop_path)
    drum = AudioSegment.from_file(drum_path)

    beat_ms = 60000 / bpm
    loop_repeats = [loop for _ in range(int(len(song) / beat_ms) + 1)]
    loop_overlay = sum(loop_repeats)[:len(song)]

    result = song.overlay(loop_overlay)
    chorus_start = detect_chorus_start(song_bytes)
    chorus_len = int(len(song) * 0.25)
    drums = sum([drum for _ in range(chorus_len // len(drum) + 1)])[:chorus_len]

    return result.overlay(drums, position=chorus_start)

if process_button and uploaded_song:
    with st.spinner("Processing..."):
        st.progress(20)
        loop_path = f"loops/{genres[genre_name]}_loop.wav"
        drum_path = f"loops/{genres[genre_name]}_drum.wav"
        
        song_bytes = BytesIO(uploaded_song.read())
        bpm = get_bpm(song_bytes)
        st.progress(50)
        song_bytes.seek(0)  # Reset pointer
        processed = sync_loops(song_bytes, loop_path, drum_path, bpm)
        
        st.progress(90)
        output = BytesIO()
        processed.export(output, format="wav")
        output.seek(0)
        st.audio(output, format="audio/wav")
        st.success("Done!")

        # # גרף
        # y, sr = librosa.load(output)
        # fig, ax = plt.subplots()
        # librosa.display.waveshow(y, sr=sr, ax=ax)
        # st.pyplot(fig)
