import streamlit as st
import os
from utils.audio_processor import (
    load_audio,
    save_audio,
    plot_volume_envelope,
    apply_loops_with_chorus
)

st.set_page_config(page_title="Music Remixer", layout="centered")
st.title("🎵 AI Music Remixer")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])

style = st.selectbox("Choose remix style", ["Hip-Hop", "Electronic", "Funky"])
loop_volume = st.slider("Loop volume (dB)", -20, 10, 0)

main_loops = {
    "Hip-Hop": "beats/hiphop_main.mp3",
    "Electronic": "beats/electro_main.mp3",
    "Funky": "beats/funky_main.mp3"
}

chorus_loops = {
    "Hip-Hop": "beats/hiphop_chorus.mp3",
    "Electronic": "beats/electro_chorus.mp3",
    "Funky": "beats/funky_chorus.mp3"
}

if uploaded_file:
    try:
        st.subheader("Original Song")
        song = load_audio(uploaded_file)
        st.audio(uploaded_file)

        st.subheader("Original Volume Envelope")
        plot_volume_envelope(song)

        if st.button("Remix"):
            with st.spinner("Remixing in progress..."):
                progress = st.progress(0)

                main_loop = main_loops[style]
                chorus_loop = chorus_loops[style]

                remixed = apply_loops_with_chorus(
                    song,
                    main_loop_path=main_loop,
                    chorus_loop_path=chorus_loop,
                    loop_gain_db=loop_volume
                )

                for i in range(100):
                    progress.progress(i + 1)

                st.success("Remix complete!")

                st.subheader("Remixed Song")
                os.makedirs("output", exist_ok=True)
                output_path = os.path.join("output", "remixed_song.mp3")
                save_audio(remixed, output_path)
                st.audio(output_path)

                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed)

                with open(output_path, "rb") as f:
                    st.download_button("Download Remixed Song", f, file_name="remixed_song.mp3")

    except Exception as e:
        st.error(f"Error processing the file: {e}")
