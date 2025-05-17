import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

def get_chorus_intervals_advanced(file_path, sr=22050):
    y, _ = librosa.load(file_path, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    similarity = np.dot(chroma.T, chroma)
    sim_norm = similarity / np.max(similarity)

    # Path enhancement using median filter
    path_sim = librosa.decompose.nn_filter(sim_norm, aggregate=np.median, metric='cosine')

    # Repeat score and peaks
    rep_scores = np.mean(path_sim, axis=0)
    peaks = librosa.util.peak_pick(rep_scores, 16, 16, 16, 16, 0.9, 5)

    times = librosa.frames_to_time(peaks, sr=sr)
    chorus_times = [(t, t + 10.0) for t in times if t + 10.0 < librosa.get_duration(y=y, sr=sr)]
    return chorus_times

def plot_musical_features(file_path, sr=22050):
    y, _ = librosa.load(file_path, sr=sr)

    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    librosa.display.specshow(chroma, y_axis='chroma', x_axis='time', ax=ax[0])
    ax[0].set(title='Chroma Features')

    # Tempogram
    tempogram = librosa.feature.tempogram(y=y, sr=sr)
    librosa.display.specshow(tempogram, y_axis='tempo', x_axis='time', ax=ax[1])
    ax[1].set(title='Tempogram')

    # MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    librosa.display.specshow(mfcc, x_axis='time', ax=ax[2])
    ax[2].set(title='MFCC')

    fig.tight_layout()
    return fig
