import streamlit as st
from utils.audio_processor import load_audio, mix_with_beat, save_audio
import tempfile
import streamlit as st

# Optional: check if file exists before trying to load it
import os
if os.path.exists("piano.jpg"):
    st.image("piano.jpg", use_container_width=True)
else:
    st.warning("Image 'piano.jpg' not found.")


st.title("🎶 Simple Music Remixer")

# File upload
uploaded_file = st.file_uploader("Upload your song (MP3/WAV)", type=["mp3", "wav"])

# Genre selection
genre = st.selectbox("Choose remix style:", ["Reggae", "Hip-Hop", "Rock"])

# Volume control slider
loop_volume = st.slider(
    "Set loop beat volume (dB):",
    min_value=0,
    max_value=30,
    value=10,
    help="Adjust how loud the loop beat is mixed with your song."
)

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")
    
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

            if selected_genre == "Hip-hop":
    beat_path = "beats/hiphop_beat.mp3"
elif selected_genre == "Reggae":
    beat_path = "beats/reggae_beat.mp3"
elif selected_genre == "Rock":
    beat_path = "beats/rock_beat.mp3"
else:
    beat_path = None

if beat_path:
    beat = AudioSegment.from_file(beat_path)
    remixed = mix_with_beat(song, beat, volume=loop_volume)
    # Then export or play remixed

    
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
