import streamlit as st
import tempfile
import os
from utils.audio_processor import (
    load_audio,
    save_audio,
    get_chorus_intervals,
    insert_loops,
    plot_envelope_with_chorus
)

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer")

uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name

    y, sr = load_audio(song_path)
    st.audio(song_path)

    st.subheader("Original Volume Envelope")
    chorus_times = get_chorus_intervals(song_path)
    plot_envelope_with_chorus(y, sr, chorus_times, title="Original Envelope")

    loops = {
        "Hip-Hop": ("beats/hiphop_main.mp3", "beats/hiphop_chorus.mp3"),
        "Reggae": ("beats/reggae_main.mp3", "beats/reggae_chorus.mp3"),
        "Rock": ("beats/rock_main.mp3", "beats/rock_chorus.mp3")
    }

    main_loop_path, chorus_loop_path = loops[style]

    if not os.path.exists(main_loop_path) or not os.path.exists(chorus_loop_path):
        st.error(f"Loop files not found for style: {style}")
    else:
        if st.button("🎧 Remix"):
            with st.spinner("Remixing with loops..."):
                y_remixed, envelope_remixed = insert_loops(
                    y, sr, main_loop_path, chorus_loop_path, chorus_times, loop_volume
                )

                st.subheader("Remixed Volume Envelope")
                plot_envelope_with_chorus(y_remixed, sr, chorus_times, title="Remixed Envelope")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                    remixed_path = out_file.name
                    save_audio(y_remixed, sr, remixed_path)

                st.success("✅ Remix complete!")
                st.audio(remixed_path)
                with open(remixed_path, "rb") as f:
                    st.download_button("⬇️ Download Remixed Song", f, file_name="remixed_song.mp3")
