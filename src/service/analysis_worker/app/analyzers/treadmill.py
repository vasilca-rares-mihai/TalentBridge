import os
from typing import List

import cv2
import time
from .base import VideoAnalyzer, mp_pose
from .filter import OneEuroFilter
from ..utils.geometry import distance_points, drawLine, extract_pose_landmarks, filter_outliers_inplace
from shared.schemas.schemas import AttributeUpdate, ChallengeResult

class StepAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Running Analysis", output_path=output_path)
        self.prev_distance_px = 0.0
        self.video_timer = 0.0
        self.speed_vector = []

        self.filter_left = OneEuroFilter(min_cutoff=1.0, beta=2.0, freq=30.0)
        self.filter_right = OneEuroFilter(min_cutoff=1.0, beta=2.0, freq=30.0)

        self.L = 0
        self.prev_counter = 0
        self.frame_count = 0
        self.last_step_frame = 0

        self.vector_stang_filtrat = []
        self.vector_drept_filtrat = []

    def extractLandmarks(self, landmarks):
        landmark_name = ["LEFT_HEEL", "RIGHT_HEEL"]
        coords = extract_pose_landmarks(landmarks, landmark_name)
        return coords

    def displayInfo(self, coords, image):
        drawLine(image, coords["LEFT_HEEL"], coords["RIGHT_HEEL"])
        cv2.putText(image, f"Pasi: {self.counter}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    def checkRep(self, coords):
        self.frame_count += 1

        left_x_raw = coords["LEFT_HEEL"][0]
        right_x_raw = coords["RIGHT_HEEL"][0]

        l_smooth = self.filter_left.apply(left_x_raw)
        r_smooth = self.filter_right.apply(right_x_raw)

        self.vector_stang_filtrat.append(l_smooth)
        self.vector_drept_filtrat.append(r_smooth)

        prag_sensibil = 0.015
        cooldown_frames = 5

        self.distance = self.calculateDistance()
        self.speed = self.calculateSpeed(self.distance)
        if (self.frame_count - self.last_step_frame) > cooldown_frames:
            if r_smooth < (l_smooth - prag_sensibil) and self.L == 0:
                self.counter += 1
                self.L = 1
                self.last_step_frame = self.frame_count
                print(
                    f"Right foot! Total: {self.counter} (Frame: {self.frame_count}) distance: {self.distance}, speed: {self.speed}")

            elif l_smooth < (r_smooth - prag_sensibil) and self.L == 1:
                self.counter += 1
                self.L = 0
                self.last_step_frame = self.frame_count
                print(
                    f"Left foot! Total: {self.counter} (Frame: {self.frame_count}), distance: {self.distance}, acceleration: {self.speed}")


    def calculateDistance(self):
        return self.counter * self.athlete_height * 0.65

    def calculateSpeed(self, distance):
        self.video_timer += (1.0 / self.fps)
        if self.video_timer > 0:
            return distance / self.video_timer
        else:
            return 0
    def calculateAcceleration(self, raw_speed):
        return 1250 # trb modificat

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        for challenge_result in challenges_results:
            if challenge_result.challenge_id == 4:
                raw_speed = self.calculateSpeed(challenge_result.result_value)
                acceleration = self.calculateAcceleration(raw_speed)
                update_obj = AttributeUpdate(sprint_speed=int(raw_speed), acceleration=int(acceleration))
                return update_obj

        return AttributeUpdate()

