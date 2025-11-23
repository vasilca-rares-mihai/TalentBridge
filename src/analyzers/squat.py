import cv2
from .base import VideoAnalyzer, mp_pose
from utils import calculate_angle, drawLine, extract_pose_landmarks
from .exercise_thresholds import ExerciseThresholds

class SquatAnalyzer(VideoAnalyzer):

    def __init__(self, video_path):
        super().__init__(video_path, window_name="Squat Analysis")

    #function that extracts the coordinates of key points from the image and returns them
    def extractLandmarks(self, landmarks):
        landmark_name = [
            "LEFT_HIP",
            "RIGHT_HIP",
            "LEFT_KNEE",
            "RIGHT_KNEE",
            "LEFT_ANKLE",
            "RIGHT_ANKLE"
        ]
        coords = extract_pose_landmarks(landmarks, landmark_name)


        return coords


    #function I used to draw some information, for exemple: legs position for squats
    def displayInfo(self, coords, image):

        drawLine(image, coords["LEFT_HIP"], coords["LEFT_KNEE"])
        drawLine(image, coords["LEFT_KNEE"], coords["LEFT_ANKLE"])

        cv2.putText(image, self.stage, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 192, 203), 2)
        h, w, _ = image.shape
        kneeL_coords = (int(coords["LEFT_KNEE"][0] * w), int(coords["LEFT_KNEE"][1] * h))
        cv2.putText(image, str(int(calculate_angle(coords["LEFT_HIP"], coords["LEFT_KNEE"], coords["LEFT_ANKLE"]))), kneeL_coords, cv2.FONT_HERSHEY_DUPLEX , 0.5, (255, 192, 203), 2 )


    def checkRep(self, coords):
        #angle1 for left leg
        self.angle1 = calculate_angle(coords["LEFT_HIP"], coords["LEFT_KNEE"], coords["LEFT_ANKLE"])
        #angle2 for right leg
        self.angle2 = calculate_angle(coords["RIGHT_HIP"], coords["RIGHT_KNEE"], coords["RIGHT_ANKLE"])

        if self.angle1 < ExerciseThresholds.SQUAT_DOWN_ANGLE and self.angle2 < ExerciseThresholds.SQUAT_DOWN_ANGLE:
            self.stage = "down"
        if self.angle1 > ExerciseThresholds.SQUAT_UP_ANGLE and self.angle2 > ExerciseThresholds.SQUAT_UP_ANGLE and self.stage == "down":
            self.stage = "up"
            self.counter += 1

        # print only when the counter has changed the value
        if self.prev_counter != self.counter:
            print(f"Squats: {self.counter}")
            self.prev_counter = self.counter