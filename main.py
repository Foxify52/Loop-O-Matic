import random, librosa
import numpy as np
import networkx as nx
import soundfile as sf
from scipy.spatial.distance import cdist

def decompose_beats(y, sr):
    onset_env = librosa.onset.onset_strength(y=np.mean(y, axis=0), sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times

def analyze_beats(y, sr, beat_times):
    S = librosa.feature.melspectrogram(y=np.mean(y, axis=0), sr=sr, n_mels=128)
    log_S = librosa.amplitude_to_db(S, ref=np.max)
    beat_features = []
    for beat_time in beat_times:
        beat_sample = librosa.time_to_frames(beat_time, sr=sr)
        beat_feature = log_S[:, beat_sample]
        beat_features.append(beat_feature)
    return np.array(beat_features)

def create_song_graph(beat_features):
    distance_matrix = cdist(beat_features, beat_features, "cosine")
    graph = nx.from_numpy_array(distance_matrix)
    return graph

def compute_song(y, sr, graph, beat_times, jumps, beat_match_length, jump_interval):
    song = []
    current_beat = 0
    potential_jumps = 0
    jump_count = 0
    while jump_count <= jumps:
        if current_beat >= len(beat_times) - 1:
            current_beat = 0
        start_time = int(beat_times[current_beat] * sr)
        end_time = int(beat_times[current_beat + 1] * sr)
        if end_time <= len(y[0]):
            song.append(y[:, start_time:end_time])
        else:
            song.append(y[:, start_time:])
            current_beat = 0
        print(f"Jump count: {jump_count}, Current beat: {current_beat}, Passed potential jumps: {potential_jumps}")
        similar_beats = [node for node in graph.neighbors(current_beat)]
        if len(similar_beats) > 0:
            potential_jumps += 1
            if random.random() < 0.2 and potential_jumps >= jump_interval:
                similar_beats = [beat for beat in similar_beats if len(set(graph[current_beat]) & set(graph[beat])) >= beat_match_length and beat != current_beat]
                if len(similar_beats) > 0:
                    current_beat = min(similar_beats, key=lambda x: np.linalg.norm(beat_features[current_beat] - beat_features[x]))
                    potential_jumps = 0
                    jump_count += 1
                else:
                    current_beat += 1
            else:
                current_beat += 1
        else:
            current_beat += 1
    while current_beat < len(beat_times) - 1:
        start_time = int(beat_times[current_beat] * sr)
        end_time = int(beat_times[current_beat + 1] * sr)
        if end_time <= len(y[0]):
            song.append(y[:, start_time:end_time])
        else:
            song.append(y[:, start_time:])
            current_beat = 0
        current_beat += 1
    final_song = np.concatenate(song, axis=1)
    return final_song

audio_file = "" # Set your song's file path here. A valid example is C:\\users\\music\\ballin.mp3
jumps = 10 # The number of times the program can jump around the song.
beat_match_length = 45 # The number of concecutive beats that must match before a jump can take place.
jump_interval = 20 # The number of times jumps are guaranteed to be skipped before the next jump is allowed to take place.

if audio_file == "":
    print("Audio file path must not be empty.")
else:
    y, sr = librosa.load(path=audio_file, sr=librosa.get_samplerate(path=audio_file), mono=False)
    beat_times = decompose_beats(y, sr)
    beat_features = analyze_beats(y, sr, beat_times)
    graph = create_song_graph(beat_features)
    song_array = compute_song(y, sr, graph, beat_times).T 
    sf.write("output.mp3", song_array, sr)