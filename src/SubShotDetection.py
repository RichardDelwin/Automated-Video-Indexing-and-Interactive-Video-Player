import librosa
import librosa.display
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import sklearn.preprocessing
import numpy as np

from Helper import Helper

def spectral_centroid_ud(y, sr, n_fft, hop_length):
    #spectral centroid -- centre of mass -- weighted mean of the frequencies present in the sound

    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft = n_fft, hop_length = hop_length)[0]
    
    # print(spectral_centroids.shape)

    # Computing the time variable for visualization
    frames = range(len(spectral_centroids))
    t = librosa.frames_to_time(frames, sr=sr, hop_length = hop_length, n_fft = n_fft)

    # Normalising the spectral centroid for visualisation
    def normalize(x, axis=0):
        return sklearn.preprocessing.minmax_scale(x, axis=axis)
    #Plotting the Spectral Centroid along the waveform
    # librosa.display.waveshow(y, sr=sr, alpha=0.4)
    # plt.plot(t, normalize(spectral_centroids), color='r')
    # plt.show()
    return t, normalize(spectral_centroids)

def spectral_centroid_stats(time_c, spec_cen_vals):
    ts = []
    abs_diffs = []
    for idx, t in enumerate(time_c[1:]):
        ts.append(t)
        abs_diffs.append(abs(spec_cen_vals[idx+1]-spec_cen_vals[idx]))
    return ts, abs_diffs, np.array(abs_diffs).mean(), np.array(abs_diffs).std()

def plot_diffs(x,y,threshold,start, end):
    # Create a line plot of the data
    plt.plot(x, y)
    subshot_times = []

    # Add annotations for points above the threshold
    for i, j in enumerate(y):
        # each shot should be atleast one sec long
        if int(x[i]+start) != int(start) and int(x[i]+start) != int(end):
            if j > threshold:
                # print("SUBSHOT: ",x[i],x[i]+start,j)
                subshot_times.append(x[i]+start)
                plt.annotate(f"{x[i]}_{j}", xy=(x[i], j), ha='center')

    # Add a horizontal line to mark the threshold
    plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold})')

    plt.legend()

    # Set axis labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Line plot with threshold')

    return Helper.remove_duplicate_times(subshot_times)
    # Show the plot
    # plt.show()

def get_subshots(path, shots_list, frame_rate):

    sample_rate, data = wav.read(path)

    time_in_s = [f_no/frame_rate for f_no in shots_list]

    audio_frames = [int((sample_rate/frame_rate)*shot) for shot in shots_list]

    # print(audio_frames)
    # print()

    y, sr = librosa.load(path, sr=sample_rate, mono=False)
    y = librosa.to_mono(y)

    for idx, frame_end in enumerate(audio_frames[1:]):
        idx = idx + 0
        start_idx = audio_frames[idx]
        end_idx = frame_end
        fact = 7.5

        if end_idx - start_idx < 4*sample_rate:
            # print(f"shot_{idx+1}", f"frame_start_{start_idx/44100}",f"frame_end_{end_idx/44100} - small shot")
            n_fft = 512
        elif (end_idx - start_idx >= 4*sample_rate) and (end_idx - start_idx < 8*sample_rate):
            # print(f"shot_{idx+1}", f"frame_start_{start_idx/44100}",f"frame_end_{end_idx/44100} - medium shot")
            n_fft = 1024
            fact = 6.5
        elif (end_idx - start_idx >= 8*sample_rate) and (end_idx - start_idx < 16*sample_rate):
            # print(f"shot_{idx+1}", f"frame_start_{start_idx/44100}",f"frame_end_{end_idx/44100} - long shot")
            n_fft = 2048
            fact = 5.5
        else:
            # print(f"shot_{idx+1}", f"frame_start_{start_idx/44100}",f"frame_end_{end_idx/44100} - xl shot")
            n_fft = 4096
            fact = 5.5
        
        hop_length = n_fft//2
        
        if end_idx-start_idx < n_fft:
            print(f"NO FFT, no shot!, shot_{idx+1}")
            continue

        # print(f"shot_{idx+1}", f"frame_start_{start_idx}",f"frame_end_{end_idx}")


        time_c, spec_cen_vals = spectral_centroid_ud(y[start_idx:end_idx], sample_rate, n_fft, hop_length=hop_length)
        ts, abs_diffs, mean_diff, std_diff = spectral_centroid_stats(time_c, spec_cen_vals)
        th = mean_diff + fact*std_diff
        s_times = plot_diffs(ts, abs_diffs, th, start=start_idx/44100, end = end_idx/44100)
        print(idx+1, start_idx*(frame_rate/sample_rate), shots_list[idx], s_times)
        print()