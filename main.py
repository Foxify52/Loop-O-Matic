import random, librosa
import numpy as np
import networkx as nx
import soundfile as sf
from collections import Counter
from scipy.spatial.distance import cdist

def analyze_song(y, sr):
    onset_env = librosa.onset.onset_strength(y=np.mean(y, 0), sr=sr)
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    C = librosa.feature.chroma_cqt(y=np.mean(y, 0), sr=sr)
    beat_features = []
    for beat_time in beat_times:
        beat_sample = librosa.time_to_frames(beat_time, sr=sr)
        beat_feature = C[:, beat_sample]
        beat_features.append(beat_feature)
    
    return beat_times, np.array(beat_features)

def find_similar_beats(graph, beat_match_length):
    indices = list(graph.keys())
    weights = [graph[node]['weight'] for node in indices]
    sequences = []

    for i in range(len(indices) - (beat_match_length - 1)):
        sequence_indices = indices[i:i + beat_match_length]
        sequence_weights = weights[i:i + beat_match_length]
        sequence = tuple(zip(sequence_indices, sequence_weights))
        sequences.append(sequence)

    sequence_counts = Counter(sequences)
    return [seq for seq, count in sequence_counts.items() if count > 1]

def compute_jumps(y, sr, graph, beat_times, jumps, beat_match_length, jump_interval):
    song, current_beat, potential_jumps, jump_count = [], 0, 0, 0
    while jump_count <= jumps or current_beat < len(beat_times) - 1:
        if current_beat >= len(beat_times) - 1:
            current_beat = 0
        start_time = int(beat_times[current_beat] * sr)
        end_time = int(beat_times[current_beat + 1] * sr) if current_beat < len(beat_times) - 1 else len(y[0])
        song.append(y[:, start_time:end_time])
        print(f"{min(int((jump_count/jumps)*100), 100)}% processed. Please wait.", end="\r")
        similar_beats = [node for node in graph.neighbors(current_beat)]
        if len(similar_beats) > 0 and jump_count <= jumps:
            potential_jumps += 1
            if random.random() < 0.2 and potential_jumps >= jump_interval:
                sequences_current_beat = find_similar_beats(graph[current_beat], beat_match_length)
                sequences_beat = {beat: find_similar_beats(graph[beat], beat_match_length) for beat in similar_beats}
                for beat in similar_beats:
                    if beat == current_beat:
                        continue
                    for a in sequences_current_beat:
                        for b in sequences_beat[beat]:
                            for c, d in zip(a, b):
                                if abs(c["weight"] - d["weight"]) >= 10**(-32):
                                    break
                                else:
                                    similar_beats.append(beat)
                                    break
                if len(similar_beats) > 0:
                    current_beat = min(similar_beats, key=lambda x: np.linalg.norm(beat_features[current_beat] - beat_features[x])) + 1
                    potential_jumps = 0
                    jump_count += 1
                else:
                    current_beat += 1
            else:
                current_beat += 1
        else:
            current_beat += 1
    return np.concatenate(song, axis=1)

audio_file = "" # The file path to your song. Can be formats other than mp3. A valid example is C:\\users\\music\\ballin.mp3
jumps = 15 # The number of times the program can jump around the song.
beat_match_length = 10 # The number of concecutive beats that must match before a jump can take place.
jump_interval = 25 # The number of times jumps are guaranteed to be skipped before the next jump is allowed to take place.

if audio_file == "":
    print("Audio file path must not be empty.")
else:
    y, sr = librosa.load(path=audio_file, sr=librosa.get_samplerate(audio_file), mono=False)
    beat_times, beat_features = analyze_song(y, sr)
    graph = nx.from_numpy_array(cdist(beat_features, beat_features, "euclidean"), create_using=nx.Graph())
    song_array = compute_jumps(y, sr, graph, beat_times, jumps, beat_match_length, jump_interval).T (y, sr, graph, beat_times, 30, 35, 40).T 
    print("Song processing complete. Now writing to file.")
    sf.write("output.mp3", song_array, sr)
    print("Done.")