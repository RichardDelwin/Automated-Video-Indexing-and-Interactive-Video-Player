import json

def get_start_and_end(frames, total_frame_count):

    res = []
    start = 0
    # TOTAL_TIME = int(round(total_frame_count/30, 3)*1000)

    # frames = list(map(lambda x: int(round(x/30, 3)*1000), frames))
    for frame in frames:

        res.append((start, frame-1))
        start = frame

    res.append((frame, total_frame_count))

    return res
def find_index(lst, target):
    left = 0
    right = len(lst) - 1

    while left <= right:
        mid = (left + right) // 2
        if target < lst[mid]:
            right = mid - 1
        else:
            left = mid + 1

    return left
def resolve_ambiguous_shots(new_shots_inferred_from_scenes, shots_frames):

    PRECISION = 10
    for new_shot in new_shots_inferred_from_scenes:
        index = find_index(shots_frames, new_shot)

        if index==0:
            if abs(shots_frames[0] - new_shot) >= PRECISION:
                shots_frames.append(new_shot)
                shots_frames.sort()
            else:
                shots_frames[0] = new_shot

        elif index == len(shots_frames):

            if abs(shots_frames[-1] - new_shot) >= PRECISION:
                shots_frames.append(new_shot)
                shots_frames.sort()
            else:
                shots_frames[-1] = new_shot

        else:
            left_shot = shots_frames[index-1]
            right_shot = shots_frames[index]

            if abs(left_shot - new_shot) < PRECISION:
                shots_frames[index - 1] = new_shot
            elif abs(right_shot - new_shot) < PRECISION:
                shots_frames[index] = new_shot
            else:
                shots_frames.append(new_shot)
                shots_frames.sort()

    return shots_frames
def combine_scenes_and_shots(shots_res, scenes_res, total_frame_count):


    scenes_frames = set(scenes_res.copy())
    shots_frames = set(shots_res.copy())

    new_shots_inferred_from_scenes = scenes_frames - shots_frames

    shots_frames = sorted(list(shots_frames))
    scenes_frames = sorted(list(scenes_frames))
    shots_frames = resolve_ambiguous_shots(new_shots_inferred_from_scenes, shots_frames)

    print('Number of scenes added : ', len(shots_frames) - len(shots_res))

    shots_res = get_start_and_end(shots_frames, total_frame_count)
    scenes_res = get_start_and_end(scenes_frames, total_frame_count)

    buckets = {k: [] for k in scenes_res}

    for shot in shots_res:

        shot_start, shot_end = shot

        for scene, scene_children in buckets.items():

            scene_start, scene_end = scene

            if shot_start>=scene_start and shot_end<=scene_end:
                scene_children.append(shot)

    buckets = {k:sorted(v, key=lambda x: x[0]) for k, v in buckets.items()}
    buckets = convert_dict_to_json_format(buckets)
    write_json(buckets, filename="./../data/combined.json")

    return buckets

def convert_dict_to_json_format(d):

    return  {f"{k[0]},{k[1]}":v for k, v in d.items()}
# def combine_scenes_and_shots(shots_res, scenes_res):
#
#
#     scenes_frames = scenes_res.copy()
#     shots_frames = shots_res.copy()
#
#     shots_res = get_start_and_end(shots_res)
#     scenes_res = get_start_and_end(scenes_res)
#
#
#
#     buckets = {k: [] for k in scenes_res}
#
#     shots = shots_res.copy()
#     while shots:
#
#         shot = shots.pop(0)
#         shot_start, shot_end = shot
#
#         for k, v in buckets.items():
#
#             scene_start, scene_end = k
#
#             if shot_start >= scene_start and shot_start <= scene_end:
#                 if shot_end <=scene_end:
#                     v.append(shot)
#                     break
#                 else:
#
#                     if shot_end-scene_end <= 30:
#                         v.append((scene_start, shot_end))
#                         break
#                     else:
#                         v.append((scene_start, scene_end))
#                         break
#                         shots.append((scene_end,  shot_end))
#
#             elif abs(scene_start - shot_start)<=30:
#                 if shot_end<scene_end:
#                     v.append((scene_start, shot_end))
#                 else:
#                     if shot_end - scene_end <= 30:
#                         v.append((scene_start, shot_end))
#                     else:
#                         v.append((scene_start, scene_end))
#                         shots.append((scene_end, shot_end))
#     write_json(buckets, filename="./../data/combined.json")
#     return buckets
    #
    # scene_start_times = [6, 20, 40]
    # shot_start_times = [5, 25, 45]
    #
    # current_scene_start = 0
    # current_scene_end = scene_start_times[1] - 1
    #
    # # Loop over shots and update scene start times as needed
    # for i, shot_start in enumerate(shot_start_times):
    #     if shot_start <= current_scene_end:
    #         # Shot starts within the current scene
    #         pass
    #     else:
    #         # Shot starts after the current scene, update scene start time
    #         scene_start_times[i] = shot_start
    #         current_scene_start = shot_start
    #         current_scene_end = scene_start + (scene_start_times[i + 1] - scene_start_times[i]) - 1
    #
    # # Update the last scene end time to be the end of the last shot
    # scene_start_times[-1] = max(scene_start_times[-1], shot_start_times[-1])
    #
    # print(scene_start_times)
def write_json(data, filename):

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def read_json(filename):

    with open(filename, "r") as f:
        data = json.load(f)

    return data


def get_timestamp_ms(frame_index, frame_rate=30):
    time = int((frame_index / frame_rate) * 1000)

    ms = time % 1000
    time = time // 1000

    seconds = time % 60
    time = time // 60

    minutes = time % 60

    timestamp = f"{minutes:02}:{seconds:02}:{ms:03}"
    return timestamp

def get_timestamp_from_ms(time):

    time = int(time*1000)
    ms = time % 1000
    time = time // 1000

    seconds = time % 60
    time = time // 60

    minutes = time % 60

    timestamp = f"{minutes:02}:{seconds:02}:{ms:03}"
    return timestamp


def format_to_final_json(res, subshots_res):

    scenes = []
    scene_iterator = 1

    for scene, shots in res.items():

        scene_name = f"scene_{scene_iterator}"
        scene_iterator+=1

        scene_start = int(scene.split(",")[0])

        shots_in_scene = []
        for shot_i, shot in enumerate(shots):

            subshots_in_scene = []
            shot_start = shot[0]

            sub_i = 1
            if shot_start in subshots_res:
                for subshot_time in subshots_res[shot_start]:

                    if sub_i == 1:
                        subshots_in_scene.append({
                            "name": f"sub_shot_{sub_i}",
                            "timestamp": f"{get_timestamp_ms(shot_start)}"
                        })
                        sub_i+=1

                    subshots_in_scene.append({
                        "name" : f"sub_shot_{sub_i}",
                        "timestamp" : f"{get_timestamp_from_ms(subshot_time)}"
                    })
                    sub_i += 1

            shots_in_scene.append({
                "name" : f"shot_{shot_i+1}",
                "timestamp" : f"{get_timestamp_ms(shot_start)}",
                "subshots": subshots_in_scene
            })

        scenes.append({
            f"{scene_name}":{
                "timestamp": f"{get_timestamp_ms(scene_start)}",
                "shots": shots_in_scene
            }
        })

    return {"data":scenes}

shots_res_json = r"E:\CSCI-576-Project\Final_github_repo\CSCI576-Project\data\HSV-Shot-Bhattacharya-res.json"
scenes_res_json = r"E:\CSCI-576-Project\Final_github_repo\CSCI576-Project\data\HSV_HUE-Scene-ChiSquareAlt-res.json"
subshots_res = read_json(r"E:\CSCI-576-Project\Final_github_repo\CSCI576-Project\data\map-res.json")
shots_res = read_json(shots_res_json)
scenes_res = read_json(scenes_res_json)

res = combine_scenes_and_shots(shots_res["frames"], scenes_res["frames"], 8682)

json_final = format_to_final_json(res, subshots_res)

write_json(json_final, "./../data/final.json")
