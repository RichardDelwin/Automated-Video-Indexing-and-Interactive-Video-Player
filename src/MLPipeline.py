from transnetv2 import TransNetV2
import os
import sys

class ShotML:

    def __init__(self):
        self._myModel = TransNetV2()

    def getPredictions(self, file):
        if os.path.isfile(file):
            a , single_frame_predictions, b = self._myModel.predict_video(file)
            return single_frame_predictions
        print(f"[File {file} does not exist, using only histogram thresholding.", file=sys.stderr) # todo
        return None