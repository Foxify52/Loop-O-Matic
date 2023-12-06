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
    distance_matrix = cdist(beat_features, beat_features, "correlation")
    graph = nx.from_numpy_array(distance_matrix)
    return graph

def find_similar_beats(beat_graph, current_beat, beat_match_length):
    compare_list, similar_beats = [], []
    for i in range(len(beat_graph) - (beat_match_length - 1)):
        sequence = []
        for j in range(beat_match_length):
            if i + j != current_beat:
                sequence.append(beat_graph[i + j])
        compare_list.append(sequence)
    for i in range(len(compare_list)):
        for j in range(i+1, len(compare_list)):
            if compare_list[i] == compare_list[j]:
                similar_beats.append(compare_list[i])
    return similar_beats

def compute_song(y, sr, graph, beat_times, jumps, beat_match_length, jump_interval):
    song = []
    current_beat = 0
    potential_jumps = 0
    jump_count = 0
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
                sequences_current_beat = find_similar_beats(graph[current_beat], current_beat, beat_match_length)
                sequences_beat = {beat: find_similar_beats(graph[beat], beat, beat_match_length) for beat in similar_beats}
                for beat in similar_beats:
                    if beat == current_beat:
                        continue
                    for a in sequences_current_beat:
                        for b in sequences_beat[beat]:
                            for c, d in zip(a, b):
                                if abs(c['weight'] - d['weight']) >= 10**(-8):
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
    final_song = np.concatenate(song, axis=1)
    return final_song

audio_file = "" # The file path to your song. Can be formats other than mp3. A valid example is C:\\users\\music\\ballin.mp3
jumps = 15 # The number of times the program can jump around the song.
beat_match_length = 10 # The number of concecutive beats that must match before a jump can take place.
jump_interval = 25 # The number of times jumps are guaranteed to be skipped before the next jump is allowed to take place.

if audio_file == "":
    print("Audio file path must not be empty.")
else:
    y, sr = librosa.load(path=audio_file, sr=librosa.get_samplerate(path=audio_file), mono=False)
    beat_times = decompose_beats(y, sr)
    beat_features = analyze_beats(y, sr, beat_times)
    graph = create_song_graph(beat_features)
    song_array = compute_song(y, sr, graph, beat_times, jumps, beat_match_length, jump_interval).T 
    print("Song processing complete. Now writing to file.")
    sf.write("output.mp3", song_array, sr)
    print("Done.")