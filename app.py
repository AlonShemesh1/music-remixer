import streamlit as st
import os
import tempfile
import random
from utils.audio_processor import (
    load_audio, save_audio, get_chorus_intervals,
    mix_with_chorus_loop, get_bpm, plot_volume_envelope
)

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer – Random Loops Edition")

uploaded_file = st.file_uploader("🎵 Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("🎚 Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("🔊 Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name

    st.audio(song_path)
    st.subheader("📈 Original Song Volume Envelope")

    song = load_audio(song_path)
    plot_volume_envelope(song)

    with st.spinner("🔍 Analyzing song..."):
        bpm = get_bpm(song_path)
        st.write(f"🕒 Detected BPM: {bpm}")

        # בחר שני לופים רנדומליים מתוך 4 עבור הסגנון שנבחר
        main_index = random.randint(1, 4)
        chorus_index = random.randint(1, 4)

        main_loop_path = f"beats/{style.lower().replace('-', '')}_loop_{main_index}.mp3"
        chorus_loop_path = f"beats/{style.lower().replace('-', '')}_loop_{chorus_index}.mp3"

        if not os.path.exists(main_loop_path) or not os.path.exists(chorus_loop_path):
            st.error(f"❌ Missing loop files for {style}. Please check beats folder.")
        else:
            main_loop = load_audio(main_loop_path) + loop_volume
            chorus_loop = load_audio(chorus_loop_path) + loop_volume

            if st.button("🎛 Remix"):
                with st.spinner("🎶 Remixing in progress..."):
                    chorus_times = get_chorus_intervals(song_path)
                    remixed = mix_with_chorus_loop(song, main_loop, chorus_loop, chorus_times, bpm, loop_volume)

                    st.subheader("📉 Remixed Volume Envelope")
                    plot_volume_envelope(remixed)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                        output_path = out_file.name
                        save_audio(remixed, output_path)

                    st.success("✅ Remix complete!")
                    st.audio(output_path, format="audio/mp3")
                    with open(output_path, "rb") as f:
                        st.download_button("⬇️ Download Remixed Song", f, file_name="remixed_song.mp3")

    os.remove(song_path)
