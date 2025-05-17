import streamlit as st
import os
import tempfile
import shutil
from utils.audio_processor import (
    load_audio,
    save_audio,
    get_chorus_intervals,
    insert_loops,
    mix_with_chorus_loop,
    get_bpm,
    plot_volume_envelope
    load_audio, save_audio, get_bpm, get_chorus_intervals,
    mix_with_chorus_loop, plot_volume_envelope
)

st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer with Chorus Detection")
st.set_page_config(page_title="Music Remixer", layout="centered")

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name
st.title("🎵 Music Remixer")
st.markdown("Upload a song and choose a remix style. Chorus will be detected and looped differently.")

    # Load original audio
    song = load_audio(song_path)
    st.audio(song_path)
    st.subheader("Original Volume Envelope")
    plot_volume_envelope(song, title="Original Song", chorus_times=[])
uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Select remix style", ["Hip-Hop", "Reggae", "Rock"])
remix_button = st.button("🎛️ Remix")

    # Set loop paths
    loop_paths = {
        "Hip-Hop": {
            "main": "beats/hiphop_main.mp3",
            "chorus": "beats/hiphop_chorus.mp3"
        },
        "Reggae": {
            "main": "beats/reggae_main.mp3",
            "chorus": "beats/reggae_chorus.mp3"
        },
        "Rock": {
            "main": "beats/rock_main.mp3",
            "chorus": "beats/rock_chorus.mp3"
        }
# Map styles to loop files
loop_paths = {
    "Hip-Hop": {
        "main": "beats/hiphop_main.mp3",
        "chorus": "beats/hiphop_chorus.mp3"
    },
    "Reggae": {
        "main": "beats/reggae_main.mp3",
        "chorus": "beats/reggae_chorus.mp3"
    },
    "Rock": {
        "main": "beats/rock_main.mp3",
        "chorus": "beats/rock_chorus.mp3"
    }
}

    main_path = loop_paths[style]["main"]
    chorus_path = loop_paths[style]["chorus"]
if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

    if not os.path.exists(main_path) or not os.path.exists(chorus_path):
        st.error(f"Missing loop files for {style}")
    else:
        if st.button("Remix"):
            with st.spinner("Detecting chorus and applying loops..."):
                bpm = get_bpm(song_path)
                st.write(f"Detected BPM: {bpm}")
        st.subheader("Original Volume Envelope")
        y = load_audio(file_path)
        chorus_times = get_chorus_intervals(file_path)
        plot_volume_envelope(y, title="Original Audio", chorus_times=chorus_times)

                chorus_times = get_chorus_intervals(song_path)
                st.write("Chorus sections:", chorus_times)
        if remix_button:
            with st.spinner("Remixing..."):
                bpm = get_bpm(file_path)
                remixed = mix_with_chorus_loop(
                    song=y,
                    main_loop_path=loop_paths[style]["main"],
                    chorus_loop_path=loop_paths[style]["chorus"],
                    chorus_times=chorus_times,
                    bpm=bpm,
                    volume_db=-3
                )

                remixed = mix_with_chorus_loop(song, main_path, chorus_path, chorus_times, bpm, loop_volume)
                output_path = os.path.join(tmpdir, "remixed.wav")
                save_audio(remixed, output_path)

                st.success("✅ Remix complete!")
                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed, title="Remixed Song", chorus_times=chorus_times)
                st.audio(output_path)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                    output_path = out_file.name
                    save_audio(remixed, output_path)
                    st.audio(output_path, format="audio/mp3")
                    with open(output_path, "rb") as f:
                        st.download_button("Download Remixed Song", f, file_name="remixed_song.mp3")

    os.remove(song_path)
                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed, title="Remixed Audio", chorus_times=chorus_times)
