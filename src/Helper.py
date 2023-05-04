import json

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd


class Helper:

    @staticmethod
    def calculate_frame_time(frame_num, frame_rate=30, offset=0):
        # Calculate the time in seconds
        time_sec = (frame_num+offset) / frame_rate
        # Convert to minutes and seconds
        minutes = int(time_sec // 60)
        seconds = int(time_sec % 60)
        # Convert to hours if necessary
        if minutes >= 60:
            hours = int(minutes // 60)
            minutes = int(minutes % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def write_to_json(data, file_path):

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def convert_timestamps(timestamps):
        # Convert timestamps to MM:SS format and remove duplicates
        time_strs = []
        prev_time = -1
        for t in sorted(set(timestamps)):
            if t != prev_time:
                m, s = divmod(t, 60)
                time_strs.append(f"{m:02d}:{s:02d}")
                prev_time = t

        return time_strs

    @staticmethod
    def plot_hist_diff(hist_diff, filename, savefig=True, hline=None, dot_coords=None, offset=0):

        figsize = (15, 15)
        fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
        ax.plot(np.arange(1, len(hist_diff) + 1), hist_diff)
        if hline is not None:
            ax.axhline(y=hline, color='r', linestyle='--', label="Threshold")

        if dot_coords is not None:

            dot_values = [hist_diff[i - 1] for i in dot_coords]
            ax.plot(dot_coords, dot_values, 'ro')
            for i, coord in enumerate(dot_coords):
                ax.annotate(f'({coord}, {dot_values[i]:.2f}  |' + Helper.calculate_frame_time(coord+offset), xy=(coord, dot_values[i]),
                            xytext=(coord + 10, dot_values[i] + 0.02), fontsize=10, color='red', rotation=90)

            ax.text(0.02, 0.98, f'Number of red dots: {len(dot_coords)}', transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))

        ax.set_xlabel('Frame number')
        ax.set_ylabel('Histogram difference (KL divergence)')
        ax.set_title('Histogram difference between consecutive frames')

        ax.legend(loc='best')

        plt.grid()

        if savefig:
            plt.savefig(filename)

    @staticmethod
    def get_weighted_preds(ml_preds, hist_preds):
        frames = hist_preds["frames"]
        dist_from_threshold = hist_preds["dist_from_threshold"]
        weighted_preds = []
        for idx, frame_no in enumerate(frames):
            ml_val = ml_preds[frame_no-1]
            hist_val = dist_from_threshold[idx]
            wt_val = 0.6*hist_val + 0.4*ml_val
            weighted_preds.append(wt_val)
        return weighted_preds
    
    @staticmethod
    def filter_predictions(result,threshold=0.5):
        # Filter based on threshold of final ensemble
        df = pd.DataFrame.from_dict(result)
        df = df[df.weighted_preds >= threshold]

        # Remove redundant timestamps
        df.drop_duplicates('time_stamps', inplace=True)
        df.reset_index(inplace=True)
        return df.to_dict('list')

    def plot_mfcc_diff_value(values, filename, savefig=True, dot_coords=None):

        figsize = (35, 15)
        fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
        ax.plot(list(range(len(values))), values)

        if dot_coords is not None:

            dot_values = [values[i] for i in dot_coords]
            ax.plot(dot_coords, dot_values, 'ro')
            # for i, coord in enumerate(dot_coords):
            #     ax.annotate(f'({coord}, {dot_values[i]})', xy=(coord, dot_values[i]),
            #                 xytext=(coord + 10, dot_values[i] + 0.02), fontsize=10, color='red', rotation=90)

            ax.text(0.02, 0.98, f'Number of red dots: {len(dot_coords)}', transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))

        ax.set_xlabel('MFCC index')
        ax.set_ylabel('Euclidean distance of MFCC values')
        ax.set_title('Audio diffs')

        ax.legend(loc='best')

        plt.grid()

        if savefig:
            plt.savefig(filename)

# Example usage
# frame_num = 100
# frame_rate = 30
# frame_time = calculate_frame_time(frame_num, frame_rate)
# print(frame_time)  # output: "00:03:20"
#
# values = [
#   "182",
#   "312",
#   "445",
#   "619",
#   "797",
#   "930",
#   "1099",
#   "1235",
#   "1320",
#   "1410",
#   "1497",
#   "1585",
#   "1766",
#   "1942",
#   "2025",
#   "2114",
#   "2207",
#   "2296",
#   "2385",
#   "2472",
#   "2649",
#   "2825",
#   "2999",
#   "3174",
#   "3409",
#   "4058",
#   "5651",
#   "6275"
# ]
# time_stamps = list(map(Helper.calculate_frame_time, list(map(int, values))))
# print(json.dumps(time_stamps))