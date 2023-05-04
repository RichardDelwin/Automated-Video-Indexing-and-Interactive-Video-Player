import copy

import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import numpy as np
import cv2


class RGBVideo:
    def __init__(self, filename, otherTypeConversions=None):
        self.filename = filename
        self.width = 480
        self.height = 270
        self.frameRate = 30

        self.frame_count = None

        self.frames = self.__load_video()

        self.frames_GRAY = None
        self.frames_HSV = None
        self.frames_GRAY_MSB = None
        self.frames_HSV_HUE = None

        for type_ in otherTypeConversions:
            if type_ == "GRAY":
                self.frames_GRAY = self.convertToGrayScale()
            if type_ == "HSV":
                self.frames_HSV = self.convertToV_ofHSVScale()
            if type_ == "GRAY_MSB":
                self.frames_GRAY_MSB = self.convertToGrayScale_MSB()
            if type_ == "HSV_HUE":
                self.frames_HSV_HUE = self.convertToHSV_HUE()

    def __load_video(self):

        # Open the file in binary mode
        with open(self.filename, "rb") as f:
            # Read the entire file into a bytes object
            data = f.read()

        # Calculate the number of frames in the video
        num_frames = len(data) // (self.width * self.height * 3)
        self.frame_count = num_frames

        # Initialize the 3D array of matrices to hold the video data
        frames = np.zeros((num_frames, self.height, self.width, 3), dtype=np.uint8)

        # Loop over each frame in the video
        for i in tqdm(range(num_frames), total=num_frames):
            # Calculate the offset in bytes for the current frame
            offset = i * self.width * self.height * 3

            # Extract the RGB data for the current frame
            frame_data = data[offset:offset + self.width * self.height * 3]

            # Reshape the data into a 2D matrix of pixels
            frame_matrix = np.frombuffer(frame_data, dtype=np.uint8).reshape((self.height, self.width, 3))

            # Add the matrix to the 3D array of frames
            frames[i, :, :, :] = frame_matrix

        return frames

    def convertToGrayScale(self):

        frames_mod = []
        for i in tqdm(range(self.frame_count), total=self.frame_count):
            frames_mod.append(cv2.cvtColor(self.frames[i, :, :, :], cv2.COLOR_RGB2GRAY))

        # frames_mod = np.array(frames_mod).astype(np.int32)
        self.frames_GRAY = copy.deepcopy(frames_mod)

        return frames_mod

    def convertToV_ofHSVScale(self):

        frames_mod = []
        for i in tqdm(range(self.frame_count), total=self.frame_count):
            frames_mod.append(cv2.cvtColor(self.frames[i, :, :, :], cv2.COLOR_RGB2HSV)[:, :, 2])

        self.frames_HSV = frames_mod

        return frames_mod

    def convertToGrayScale_MSB(self):

        frames_mod = []
        for i in tqdm(range(self.frame_count), total=self.frame_count):
            frames_mod.append(cv2.cvtColor(self.frames[i, :, :, :], cv2.COLOR_RGB2GRAY) & 0b11111100)
        self.frames_HSV = frames_mod

        return frames_mod

    def convertToHSV_HUE(self):
        frames_mod = []
        for i in tqdm(range(self.frame_count), total=self.frame_count):
            frames_mod.append(cv2.cvtColor(self.frames[i, :, :, :], cv2.COLOR_RGB2HSV)[:, :, 0])

        # frames_mod = np.array(frames_mod).astype(np.int32)
        self.frames_HSV_HUE = copy.deepcopy(frames_mod)

        return frames_mod

    def blur_frameList(self, frameList, strength = 5):
        # Create a Gaussian blur kernel of size 5x5 with standard deviation of 0
        blurred_framelist = []
        kernel_size = (strength, strength)
        sigma = 0

        print("Blurring")
        for frame in tqdm(frameList, total=len(frameList)):

            kernel = cv2.getGaussianKernel(kernel_size[0], sigma) * cv2.getGaussianKernel(kernel_size[1], sigma).T

            # Normalize the kernel
            kernel = kernel / np.sum(kernel)

            # Apply the convolution operation using the kernel
            blurred_frame = cv2.filter2D(frame, -1, kernel)

            blurred_framelist.append(blurred_frame)

        return blurred_framelist


    def convertToInt32(self, frameList):
        return np.array(frameList).astype(np.int32)

    def __calc_hist(self, frame):
        # Compute the histogram of the frame
        hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
        # Normalize the histogram
        hist = cv2.normalize(hist, None).flatten()
        return hist

    def __calc_hist_wo_norm(self, frame):
        # Compute the histogram of the frame
        hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
        return hist

    def __compare_hist_kl_div(self, frame1, frame2):
        # Compute the histograms of the two frames
        hist1 = self.__calc_hist(frame1)
        hist2 = self.__calc_hist(frame2)
        # Calculate the KL divergence between the histograms

        # cv2.HISTCMP_KL_DIV
        # HISTCMP_CORREL
        # HISTCMP_CHISQR
        kl_div = cv2.compareHist(hist1, hist2, cv2.HISTCMP_KL_DIV)
        return kl_div

    def __compare_hist_bhattacharya(self, frame1, frame2):
        # Compute the histograms of the two frames
        hist1 = self.__calc_hist(frame1)
        hist2 = self.__calc_hist(frame2)
        # Calculate the KL divergence between the histograms

        # cv2.HISTCMP_KL_DIV
        # HISTCMP_CORREL
        # HISTCMP_CHISQR
        bhattacharya = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
        return bhattacharya

    def __compare_hist_chiSquare(self, frame1, frame2):
        # Compute the histograms of the two frames
        hist1 = self.__calc_hist(frame1)
        hist2 = self.__calc_hist(frame2)
        # Calculate the KL divergence between the histograms

        # cv2.HISTCMP_KL_DIV
        # HISTCMP_CORREL
        # HISTCMP_CHISQR
        d = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR_ALT)
        return d

    def __resolveFrame(self, type_="RGB"):
        if type_ == "RGB":
            return self.frames
        if type_ == "GRAY":
            return self.frames_GRAY
        if type_ == "HSV":
            return self.frames_HSV
        if type_ == "GRAY_MSB":
            return self.frames_GRAY_MSB
        if type_ == "HSV_HUE":
            return self.frames_HSV_HUE

    def save_frame(self, frame_num, output_filename, frame_type="RGB", frameList = []):

        if len(frameList) ==0:
            frameList = self.__resolveFrame(frame_type)

        frame = frameList[frame_num]
        cv2.imwrite(output_filename, frame)
        print(f"Frame {frame_num} saved to {os.path.abspath(output_filename)}")
        print("Frame Shape = ", frame.shape)

    def get_hist_diff(self, frameList, frame_type="RGB"):
        hist_diff = []

        # if len(frameList) == 0:
        #     frameList = self.__resolveFrame(frame_type)

        for i in range(1, len(frameList)):
            # Compute the KL divergence between the histograms of the current and previous frames
            kl_div = self.__compare_hist_kl_div(frameList[i], frameList[i - 1])
            hist_diff.append(kl_div)

        return hist_diff

    def get_hist_diff_bhattacharya(self, frameList):

        hist_diff = []
        hist_values = [self.__calc_hist_wo_norm(frameList[0])]

        for i in range(1, len(frameList)):

            hist_values.append(self.__calc_hist_wo_norm(frameList[i]))
            # Compute the KL divergence between the histograms of the current and previous frames
            b = self.__compare_hist_bhattacharya(frameList[i], frameList[i - 1])
            hist_diff.append(b)

        return hist_diff, hist_values

    def get_hist_diff_chiSquare(self, frameList):

        hist_diff = []
        hist_values = [self.__calc_hist_wo_norm(frameList[0])]

        for i in range(1, len(frameList)):

            hist_values.append(self.__calc_hist_wo_norm(frameList[i]))
            # Compute the KL divergence between the histograms of the current and previous frames
            b = self.__compare_hist_chiSquare(frameList[i], frameList[i - 1])
            hist_diff.append(b)

        return hist_diff, hist_values

    def get_hist_abs_diff(self, frameList):

        frameList = np.array(frameList).astype(np.int32)
        hist_diff = []
        hist_values = []

        # prev_histogram = self.__calc_hist_wo_norm(frameList[0])
        prev_histogram_sum = np.array(frameList[0]).flatten().sum()
        hist_values.append(prev_histogram_sum)

        for i in range(1, len(frameList)):
            # Compute the KL divergence between the histograms of the current and previous frames

            # curr_histogram = self.__calc_hist_wo_norm(frameList[i])
            curr_histogram_sum = np.array(frameList[i]).flatten().sum()
            hist_values.append(curr_histogram_sum)

            histogram_abs_diff = abs(curr_histogram_sum - prev_histogram_sum)
            prev_histogram_sum = curr_histogram_sum

            hist_diff.append(histogram_abs_diff)

        return hist_diff, hist_values

    def get_frame_list(self, frame_type):

        return self.__resolveFrame(frame_type)




    ### Subshot Detection #####

    def extract_contours(self, frameList, threshold=100):
        # Convert image to grayscale

        print("Finding Contours")

        for frame in tqdm(frameList, total=len(frameList)):


            # Apply threshold to obtain binary image
            ret, binary = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)

            # Find contours in binary image
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    def optical_flow(self, frameList):
        prev_frame = None
        diffs = []

        print("Calculating optical flow")
        for frame in tqdm(frameList, total=len(frameList)):

            # Calculate optical flow using Gunnar-Farneback algorithm
            if prev_frame is not None:
                flow = cv2.calcOpticalFlowFarneback(prev_frame, frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)

                # Compute magnitude of optical flow vectors
                mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

                # Normalize magnitude to be in range [0,255]
                mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)

                mag_sum = mag.flatten().sum()
                # Add difference between current frame and previous frame to list
                diffs.append(mag_sum.astype(np.uint32))

            prev_frame = frame.copy()

        return diffs