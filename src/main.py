from MLPipeline import ShotML

from Analyzer import Analyzer
from Helper import Helper
from VideoReader import RGBVideo


import sys
import json


## Subshot detection
#
# frame_type="HSV"
# #
# path = sys.argv[1]
# dest_dir = "./test/New-ReadyPlayerOne"
# #
# analysis_type = "HUE-Subshot-OpticalFlow"
# print("Loading video ",path)
# video = RGBVideo(path, otherTypeConversions=[frame_type])
# frame_list = video.get_frame_list(frame_type=frame_type)
# #
# optical_diff = video.optical_flow(frameList=frame_list[1352:2458])
# # Helper.plot_hist_diff(optical_diff, "{}/{}-hist.png".format(dest_dir, analysis_type))
#
# videoAnalyzer = Analyzer(optical_diff, normalize=False)
# threshold = videoAnalyzer.stats["mean"] + 3.5 * videoAnalyzer.stats["std"] #3.5 for shots
#
# res = videoAnalyzer.findKeyFramesAndTimeStamps(threshold)
# Helper.plot_hist_diff(optical_diff, "{}/{}-hist.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"], offset=1352)

# frame_type="HSV"
#
# path = sys.argv[1]
# dest_dir = "./test/New-ReadyPlayerOne"
#
# analysis_type = "HUE-Subshot-localThresholding"
# print("Loading video ",path)
# video = RGBVideo(path, otherTypeConversions=[frame_type])
# frame_list = video.get_frame_list(frame_type=frame_type)
#
# all_res = []
# all_hist_diff = []
# all_res_frames=[]
# frames = [161,251,419,420,507,1131,1178,1352,2458,2582,3147,3243,3284,3302,3546,3570,3620,3728,3770,3808,3847,3878,3989,3990,4022,4052,4081,4128,4231,4346,4491,4724,4843,5329,5599,5753,5951,6139,6303,6856,6968,7048,7457,7591,7668,7835,7876,7890,8017,8079,8114,8177,8190,8268,8289,8311,8369,8510,8683]
# prev_frame = 0
# for frame in frames:
#     if frame-prev_frame == 1:
#         prev_frame = frame
#         continue
#     hist_diff, _ = video.get_hist_diff_bhattacharya(frameList=frame_list[prev_frame:frame])
# # Helper.plot_hist_diff(optical_diff, "{}/{}-hist.png".format(dest_dir, analysis_type))
#
#     videoAnalyzer = Analyzer(hist_diff, normalize=False)
#     threshold = videoAnalyzer.stats["mean"] + 3 * videoAnalyzer.stats["std"] #3.5 for shots
#
#     res = videoAnalyzer.findKeyFramesAndTimeStamps(threshold, prev_frame)
#
#     all_res.extend(res["time_stamps"])
#     all_hist_diff.extend(hist_diff)
#     all_res_frames.extend(list(map(lambda x: x+prev_frame, res["frames"])))
#     prev_frame = copy.deepcopy(frame)
#
# Helper.plot_hist_diff(all_hist_diff, "{}/{}-hist.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=all_res_frames)
# Helper.write_to_json({"frames":all_res_frames,"time_stamps":all_res}, "{}/{}-stats.json".format(dest_dir, analysis_type))
# #


### Scene and shot detection

# frame_type="HSV"

def get_shots(frame_type, path, path_mp4, analysis_type = "HSV-Shot-Bhattacharya"):
    dest_dir = "./test/"

    print("Loading video ",path)
    video = RGBVideo(path, otherTypeConversions=[frame_type])
    frame_list = video.get_frame_list(frame_type=frame_type)


    # ChiSquare Alternative (Used for scenes)
    hist_diff = video.get_hist_diff_bhattacharya(frame_list)

    videoAnalyzer = Analyzer(hist_diff, normalize=False)
    threshold = videoAnalyzer.stats["mean"]

    hist_preds = videoAnalyzer.findKeyFramesAndTimeStamps_shot(threshold)

    shot_ml = ShotML()
    ml_preds = shot_ml.getPredictions(path_mp4)

    res = hist_preds.copy()

    weighted_preds = Helper.get_weighted_preds(ml_preds, hist_preds)

    res["ml_preds"] = ml_preds[:-1].tolist()
    res["weighted_preds"] = weighted_preds

    filtered_res = Helper.filter_predictions(res, 0.45)

    Helper.write_to_json(res, "{}/{}-stats.json".format(dest_dir, analysis_type))
    Helper.plot_hist_diff(hist_diff, "{}/{}-hist.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"])
    
    return filtered_res

if __name__ == "__main__":
    path = sys.argv[1]
    path_mp4 = sys.argv[2]
    frame_type = "HSV"
    analysis_type = "HSV-Shot-Bhattacharya"
    res = get_shots(frame_type, path, path_mp4, analysis_type = analysis_type)
    with open(f"./test/{analysis_type}-res.json", "w") as f:
        json.dump(res, f, indent=4)
#
#
#
# # Histogram diff using battacharya (Used for shots)
# # https://stackoverflow.com/questions/44902410/python-opencv-3-how-to-use-cv2-cv-comp-hellinger
# analysis_type = "HSV-SubShots-Bhattacharya"
# video.save_frame(1000, '{}/{}-frame1000.png'.format(dest_dir, analysis_type), frame_type=frame_type, frameList=frame_list)
#
# hist_diff, hist_values = video.get_hist_diff_bhattacharya(frame_list)
#
# videoAnalyzer = Analyzer(hist_diff, normalize=False)
# threshold = videoAnalyzer.stats["mean"] + 9.5 * videoAnalyzer.stats["std"]   #10 for scenes, 4.5 for shots
#
# res = videoAnalyzer.findKeyFramesAndTimeStamps(threshold)
# Helper.write_to_json(res, "{}/{}-stats.json".format(dest_dir, analysis_type))
# Helper.plot_hist_diff(hist_diff, "{}/{}-hist.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"])
# #




## ----------------------------------------- NOT GOOD ------------------------------------------------------

# # Histogram sums for each frame, and absolute diff
#
# frame_list = video.get_frame_list(frame_type=frame_type)
#
# hist_diff_abs, hist_sum_values = video.get_hist_abs_diff(frame_list)
#
# videoAnalyzer = Analyzer(hist_diff_abs, normalize=False)
#
# threshold = videoAnalyzer.stats["mean"] + 10 * videoAnalyzer.stats["std"]
#
# res = videoAnalyzer.findKeyFramesAndTimeStamps(threshold)
# Helper.write_to_json(res, "{}/stats-absolute{}.json".format(dest_dir, analysis_type))
# Helper.plot_hist_diff(hist_diff_abs, "{}/hist-absolute-{}.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"])
# Helper.plot_hist_diff(hist_sum_values, "{}/hist-sums-{}.png".format(dest_dir, analysis_type))





# # shot boundaries
# threshold = videoAnalyzer.stats["mean"] + 0.5 * videoAnalyzer.stats["std"]
# res = videoAnalyzer.findKeyFramesAndTimeStamps(threshold)
# Helper.write_to_json(res, "{}/stats-{}.json".format(dest_dir, analysis_type))
# Helper.plot_hist_diff(videoAnalyzer.data, "{}/hist-{}.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"])
#
#
# # Scene Boundaries using KL divergence
# threshold2 = videoAnalyzer.stats["mean"] + 10 * videoAnalyzer.stats["std"]
# res2 = videoAnalyzer.findKeyFramesAndTimeStamps(threshold2)
# Helper.write_to_json(res2, "{}/stats-scenes-{}.json".format(dest_dir, analysis_type))
# Helper.plot_hist_diff(videoAnalyzer.data, "{}/hist-scenes-{}.png".format(dest_dir, analysis_type), hline=threshold2, dot_coords=res2["frames"])
