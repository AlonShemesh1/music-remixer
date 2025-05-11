import streamlit as st
from utils.audio_processor import load_audio, mix_with_beat, save_audio
import tempfile
from utils.audio_processor import plot_volume_envelope
import matplotlib.pyplot as plt

# Duration of song in seconds
duration = len(song) / 1000.0

# Let user scrub/select playback position
playback_position = st.slider("Playback position (seconds)", 0.0, duration, 0.0, step=0.5)

st.title("🎶 Simple Music Remixer")

# File upload
uploaded_file = st.file_uploader("Upload your song (MP3/WAV)", type=["mp3", "wav"])

# Genre selection
genre = st.selectbox("Choose remix style:", ["Reggae", "Hip-Hop", "Rock"])

# Volume control slider
loop_volume = st.slider(
    "Set loop beat volume (dB):",
    min_value=-20,
    max_value=5,
    value=-3,
    help="Adjust how loud the loop beat is mixed with your song."
)

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")

        # Plot volume envelope of uploaded song
    with st.spinner("Loading volume envelope..."):
        song = load_audio(uploaded_file)
        fig_env = plot_volume_envelope(song, title="Uploaded Song Volume Over Time")
        st.pyplot(fig_env)

    if st.button("Remix it!"):
        with st.spinner("Processing..."):
            # Load user song
            song = load_audio(uploaded_file)
            
            # Select beat file based on genre
            beat_file = {
                "Reggae": "beats/reggae_loop.mp3",
                "Hip-Hop": "beats/hiphop_loop.mp3",
                "Rock": "beats/rock_loop.mp3"
            }[genre]
            
            # Load beat
            beat = load_audio(beat_file)
            
            # Mix with user-defined loop volume
            remixed = mix_with_beat(song, beat, loop_gain_db=loop_volume)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                save_audio(remixed, tmp.name)
                st.success("Done!")
                st.audio(tmp.name)
                
                # Download link
                st.download_button(
                    label="Download remixed song",
                    data=open(tmp.name, 'rb'),
                    file_name=f"remixed_{uploaded_file.name}",
                    mime="audio/mp3"
                )

