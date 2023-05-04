import sys
from Analyzer import Analyzer
from Helper import Helper
from VideoReader import RGBVideo


def get_scenes(video, frame_type="HSV_HUE", analysis_type = "HSV_HUE-Scene-ChiSquareAlt"):

    dest_dir = "./test/New-ReadyPlayerOne"

    frame_list = video.get_frame_list(frame_type=frame_type)
    frame_list = video.blur_frameList(frame_list, strength=15)


    # ChiSquare Alternative (Used for scenes)
    hist_diff = video.get_hist_diff_chiSquare(frame_list)

    videoAnalyzer = Analyzer(hist_diff, normalize=False)
    threshold = videoAnalyzer.stats["mean"] + 9.5 * videoAnalyzer.stats["std"] #3.5 for shots

    res = videoAnalyzer.findKeyFramesAndTimeStamps(threshold)
    Helper.write_to_json(res, "{}/{}-stats.json".format(dest_dir, analysis_type))
    Helper.plot_hist_diff(hist_diff, "{}/{}-hist.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"])

    return res

frame_type="HSV_HUE"
path_rgb = r"E:\CSCI-576-Project\data\Ready_Player_One_rgb\Ready_Player_One_rgb\InputVideo.rgb"
video = RGBVideo(path_rgb, otherTypeConversions=[frame_type])
print(get_scenes(video))

