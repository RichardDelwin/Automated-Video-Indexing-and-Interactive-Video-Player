from ShotDetection import get_shots
from SceneDetection import get_scenes
from SubShotDetection import get_subshots
from Aggregator import combine_scenes_and_shots, format_to_final_json

import sys
import json


if __name__ == "__main__":
    path = sys.argv[1]
    path_mp4 = sys.argv[2]
    path_wav = sys.argv[3]

    frame_type = "HSV"
    analysis_type = "HSV-Shot-Bhattacharya"

    res_shots, frame_count = get_shots(frame_type, path, path_mp4, analysis_type = analysis_type)

    # with open(f"./test/{analysis_type}-res.json", "w") as f:
    #     json.dump(res_shots, f, indent=4)
    
    frame_type_scenes="HSV_HUE"
    analysis_type_scenes = "HSV_HUE-Scene-ChiSquareAlt"
    res_scenes, _ = get_scenes(frame_type_scenes, path, analysis_type=analysis_type_scenes)

    # with open(f"./test/{analysis_type_scenes}-res.json", "w") as f:
    #     json.dump(res_scenes, f, indent=4)

    scene_shot_buckets = combine_scenes_and_shots(res_shots["frames"], res_scenes["frames"], frame_count)

    shots_list = []

    for sc, sh in scene_shot_buckets.items():
        shots_list = shots_list + [fr_no[0] for fr_no in sh]
    sorted_shots = sorted(shots_list)

    print(sorted_shots == shots_list)

    sorted_shots.append(frame_count)

    print(sorted_shots)

    shot_subshot_map = get_subshots(path_wav, shots_list=sorted_shots, frame_rate=30.0)

    final_json = format_to_final_json(scene_shot_buckets, shot_subshot_map)

    with open(f"./test/final.json", "w") as f:
        json.dump(final_json, f, indent=4)