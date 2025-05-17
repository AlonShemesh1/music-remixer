import streamlit as st
import os
import tempfile
import shutil
import os
from utils.audio_processor import (
    load_audio, save_audio, get_bpm, get_chorus_intervals,
    mix_with_chorus_loop, plot_volume_envelope
    load_audio,
    save_audio,
    get_chorus_intervals,
    insert_loops,
    plot_envelope_with_chorus
)

st.set_page_config(page_title="Music Remixer", layout="centered")
st.set_page_config(page_title="🎵 Music Remixer", layout="centered")
st.title("🎵 Music Remixer with Chorus Detection")

st.title("🎵 Music Remixer")
st.markdown("Upload a song and choose a remix style. Chorus will be detected and looped differently.")
uploaded_file = st.file_uploader("Upload a song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Choose remix style", ["Hip-Hop", "Reggae", "Rock"])
loop_volume = st.slider("Loop Volume (dB)", -20, 10, 0)

uploaded_file = st.file_uploader("Upload your song (MP3 or WAV)", type=["mp3", "wav"])
style = st.selectbox("Select remix style", ["Hip-Hop", "Reggae", "Rock"])
remix_button = st.button("🎛️ Remix")
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        song_path = tmp.name

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
    y, sr = load_audio(song_path)
    st.audio(song_path)

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
    st.subheader("Original Volume Envelope")
    chorus_times = get_chorus_intervals(song_path)
    plot_envelope_with_chorus(y, sr, chorus_times, title="Original Envelope")

        st.subheader("Original Volume Envelope")
        y = load_audio(file_path)
        chorus_times = get_chorus_intervals(file_path)
        plot_volume_envelope(y, title="Original Audio", chorus_times=chorus_times)
    loops = {
        "Hip-Hop": ("beats/hiphop_main.mp3", "beats/hiphop_chorus.mp3"),
        "Reggae": ("beats/reggae_main.mp3", "beats/reggae_chorus.mp3"),
        "Rock": ("beats/rock_main.mp3", "beats/rock_chorus.mp3")
    }

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
    main_loop_path, chorus_loop_path = loops[style]

    if not os.path.exists(main_loop_path) or not os.path.exists(chorus_loop_path):
        st.error(f"Loop files not found for style: {style}")
    else:
        if st.button("🎧 Remix"):
            with st.spinner("Remixing with loops..."):
                y_remixed, envelope_remixed = insert_loops(
                    y, sr, main_loop_path, chorus_loop_path, chorus_times, loop_volume
                )

                output_path = os.path.join(tmpdir, "remixed.wav")
                save_audio(remixed, output_path)
                st.subheader("Remixed Volume Envelope")
                plot_envelope_with_chorus(y_remixed, sr, chorus_times, title="Remixed Envelope")

                st.success("✅ Remix complete!")
                st.audio(output_path)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
                    remixed_path = out_file.name
                    save_audio(y_remixed, sr, remixed_path)

                st.subheader("Remixed Volume Envelope")
                plot_volume_envelope(remixed, title="Remixed Audio", chorus_times=chorus_times)
                st.success("✅ Remix complete!")
                st.audio(remixed_path)
                with open(remixed_path, "rb") as f:
                    st.download_button("⬇️ Download Remixed Song", f, file_name="remixed_song.mp3")
