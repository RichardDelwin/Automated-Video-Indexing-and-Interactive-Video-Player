import math

import numpy as np

from Helper import Helper


class Analyzer:

    def __init__(self, data, normalize=False):
        self.data = self.normalize(data) if normalize else data
        self.stats = self.get_stats()

    def normalize(self, values):
        min_value = min(values)
        max_value = max(values)
        normalized_values = [(value - min_value) / (max_value - min_value) for value in values]
        return normalized_values

    def updateData(self, data):
        self.data = data

    def get_stats(self):
        mean = np.mean(self.data)

        # Calculate the standard deviation of the values
        std_dev = np.std(self.data)

        stats = {
            "mean": mean,
            "std": std_dev,
        }

        print(stats)
        return stats

    # finds frames above specified threshold
    def findKeyFramesAndTimeStamps(self, threshold, offset=0):

        if math.isnan(threshold):
            return {
                "frames": [],
                "time_stamps": []
            }
        # adjusting frame number since frame 0 is not computed
        indices = list(map(lambda x: int(x + 1), np.where(np.array(self.data) >= threshold)[0]))
        time_stamps = list(map(lambda x : Helper.calculate_frame_time(x, offset=offset), indices))

        return self.remove_redundantFrames({"frames": indices, "time_stamps": time_stamps})

    def calc_dist_from_threshold(self, idx, threshold):
        if self.data[idx] >= threshold:
            return ((((self.data[idx]-threshold)/(1.0-threshold))*(1-0.5))+0.5)
        else:
            return (((self.data[idx])/(threshold))*(0.5))
            
    def findKeyFramesAndTimeStamps_shot(self, threshold):
        # adjusting frame number since frame 0 is not computed
        indices = list(range(1,len(self.data)+1))
        time_stamps = list(map(Helper.calculate_frame_time, indices))
        dist_from_threshold = [self.calc_dist_from_threshold(idx-1, threshold) for idx in indices]
        return {"frames": indices, "time_stamps": time_stamps, "dist_from_threshold": dist_from_threshold}

    # def findKeyFramesAndTimeStampsOfShots(self, threshold, keyFrames):
    #     # adjusting frame number since frame 0 is not computed
    #     indices = list(map(lambda x: int(x + 1), np.where(np.array(self.data) >= threshold)[0]))

    #     indices2 = list(map(lambda x : keyFrames[x], indices))

    #     time_stamps = list(map(Helper.calculate_frame_time, indices2))

    #     return self.remove_redundantFrames({"frames": indices, "time_stamps": time_stamps})

    def remove_redundantFrames(self, data):

        if data["frames"] == None or len(data["frames"]) == 0:
            return {
                "frames": [],
                "time_stamps": []
            }

        frames = data["frames"]
        time_stamps = data["time_stamps"]

        new_frames = [frames[0]]
        new_time_stamps = [time_stamps[0]]

        for i in range(1, len(frames)):

            if time_stamps[i - 1] != time_stamps[i]:
                new_frames.append(frames[i])
                new_time_stamps.append(time_stamps[i])

        return {
            "frames": new_frames,
            "time_stamps": new_time_stamps
        }
