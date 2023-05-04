from ShotDetection import get_shots
from SceneDetection import get_scenes

import sys
import json


if __name__ == "__main__":
    path = sys.argv[1]
    path_mp4 = sys.argv[2]
    frame_type = "HSV"
    analysis_type = "HSV-Shot-Bhattacharya"

    res = get_shots(frame_type, path, path_mp4, analysis_type = analysis_type)
    with open(f"./test/{analysis_type}-res.json", "w") as f:
        json.dump(res, f, indent=4)
    
    frame_type_scenes="HSV_HUE"
    analysis_type_scenes = "HSV_HUE-Scene-ChiSquareAlt"
    res_scenes = get_scenes(frame_type_scenes, path, analysis_type=analysis_type_scenes)
    with open(f"./test/{analysis_type_scenes}-res.json", "w") as f:
        json.dump(res_scenes, f, indent=4)
