from MLPipeline import ShotML

from Analyzer import Analyzer
from Helper import Helper
from VideoReader import RGBVideo


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
    # Helper.plot_hist_diff(hist_diff, "{}/{}-hist.png".format(dest_dir, analysis_type), hline=threshold, dot_coords=res["frames"])
    
    return filtered_res