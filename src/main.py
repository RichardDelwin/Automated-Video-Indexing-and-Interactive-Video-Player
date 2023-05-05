from ShotDetection import get_shots
from SceneDetection import get_scenes
from SubShotDetection import get_subshots

import sys
import json


if __name__ == "__main__":
    path = sys.argv[1]
    path_mp4 = sys.argv[2]
    path_wav = sys.argv[3]

    frame_type = "HSV"
    analysis_type = "HSV-Shot-Bhattacharya"

    res, frame_count = get_shots(frame_type, path, path_mp4, analysis_type = analysis_type)
    with open(f"./test/{analysis_type}-res.json", "w") as f:
        json.dump(res, f, indent=4)
    
    frame_type_scenes="HSV_HUE"
    analysis_type_scenes = "HSV_HUE-Scene-ChiSquareAlt"
    res_scenes, _ = get_scenes(frame_type_scenes, path, analysis_type=analysis_type_scenes)
    with open(f"./test/{analysis_type_scenes}-res.json", "w") as f:
        json.dump(res_scenes, f, indent=4)

    # Append start and end frame for shot boundaries
    shots_list = res["frames"].copy()
    shots_list.insert(0,0)
    shots_list.append(frame_count)

    # shots_list = [ 0,
    #     183,
    #     313,
    #     446,
    #     620,
    #     798,
    #     931,
    #     1100,
    #     1236,
    #     1321,
    #     1411,
    #     1498,
    #     1586,
    #     1767,
    #     1943,
    #     2026,
    #     2115,
    #     2208,
    #     2297,
    #     2386,
    #     2473,
    #     2650,
    #     2826,
    #     3000,
    #     3175,
    #     3410,
    #     3682,
    #     3690,
    #     4059,
    #     4285,
    #     5648,
    #     6276
    # ]

    shot_subshot_map = get_subshots(path_wav, shots_list=shots_list, frame_rate=30.0)
    print(shot_subshot_map)