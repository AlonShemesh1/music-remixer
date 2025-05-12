import streamlit as st
import os
import tempfile
from utils.audio_processor import (
    load_audio, save_audio, get_chorus_intervals,
    insert_loops, plot_volume_envelope
)

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer with Chorus Detection")

uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name

    song = load_audio(song_path)
    st.audio(song_path)
    st.subheader("Original Song Volume")
    plot_volume_envelope(song)

    # Load loops
    loop_files = {
        "Hip-Hop": ("beats/hiphop_main.mp3", "beats/hiphop_chorus.mp3"),
        "Reggae": ("beats/reggae_main.mp3", "beats/reggae_chorus.mp3"),
        "Rock": ("beats/rock_main.mp3", "beats/rock_chorus.mp3")
    }

    main_path, chorus_path = loop_files[style]
    if not os.path.exists(main_path) or not os.path.exists(chorus_path):
        st.error(f"Missing loop files for {style}")
    else:
        main_loop = load_audio(main_path) + loop_volume
        chorus_loop = load_audio(chorus_path) + loop_volume

        if st.button("Remix"):
            with st.spinner("Detecting chorus and remixing..."):
                chorus_times = get_chorus_intervals(song_path)
                remixed = insert_loops(song, main_loop, chorus_loop, chorus_times)

                st.subheader("Remixed Volume")
                plot_volume_envelope(remixed)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
                    output_path = out.name
                    save_audio(remixed, output_path)

                st.success("🎉 Remix complete!")
                st.audio(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("Download Remixed Song", f, "remixed_song.mp3")
