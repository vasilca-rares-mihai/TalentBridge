import cv2
from .base import VideoAnalyzer, mp_pose
from utils import calculate_angle, drawLine, extract_pose_landmarks
from .exercise_thresholds import ExerciseThresholds

class PullupAnalyzer(VideoAnalyzer):
    def __init__(self, video_path):
        super().__init__(video_path, window_name="Pull-up Analysis")

    #function that extracts the coordinates of key points from the image and returns them
    def extractLandmarks(self, landmarks):
        landmark_name = [
            "LEFT_SHOULDER",
            "RIGHT_SHOULDER",
            "LEFT_ELBOW",
            "RIGHT_ELBOW",
            "LEFT_WRIST",
            "RIGHT_WRIST",
            "MOUTH_LEFT"
        ]
        coords = extract_pose_landmarks(landmarks, landmark_name)
        return coords

    def displayInfo(self, coords, image):
        drawLine(image, coords["LEFT_WRIST"], coords["RIGHT_WRIST"])

        cv2.putText(image, self.stage, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        h, w, _ = image.shape
        left_arm_coords = (int(coords["LEFT_ELBOW"][0] * w), int(coords["LEFT_ELBOW"][1] * h))
        cv2.putText(image, str(int(calculate_angle(coords["LEFT_SHOULDER"], coords["LEFT_ELBOW"], coords["LEFT_WRIST"]))), left_arm_coords, cv2.FONT_HERSHEY_DUPLEX , 0.5,(255, 192, 203), 2)
        right_arm_coords = (int(coords["RIGHT_ELBOW"][0] * w), int(coords["RIGHT_ELBOW"][1] * h))
        cv2.putText(image, str(int(calculate_angle(coords["RIGHT_SHOULDER"], coords["RIGHT_ELBOW"], coords["RIGHT_WRIST"]))), right_arm_coords, cv2.FONT_HERSHEY_DUPLEX , 0.5,(255, 192, 203), 2)

    def checkRep(self, coords):
        #variables that help me count exercise repetitions
        #bar - y coord. when bar < chin.y => one correct rep
        bar = (coords["RIGHT_WRIST"][1] + coords["LEFT_WRIST"][1]) / 2
        #angleL and angleR. angle because a correct rep is when the angles > 160
        #angle1 for left arm
        self.angle1 = calculate_angle(coords["LEFT_SHOULDER"], coords["LEFT_ELBOW"], coords["LEFT_WRIST"])
        #angle2 for right arm
        self.angle2 = calculate_angle(coords["RIGHT_SHOULDER"], coords["RIGHT_ELBOW"], coords["RIGHT_WRIST"])
        #I approximated the chin level (between shoulder and mouth, on the y coordinate
        chin = ((coords["LEFT_SHOULDER"][1]+coords["RIGHT_SHOULDER"][1]) /2 + coords["MOUTH_LEFT"][1])/2

        if self.angle1 > ExerciseThresholds.PULLUP_DOWN_ANGLE and self.angle2 > ExerciseThresholds.PULLUP_DOWN_ANGLE:
            self.stage = "down"
        if self.angle1 < ExerciseThresholds.PULLUP_UP_ANGLE and self.angle2 < ExerciseThresholds.PULLUP_UP_ANGLE and self.stage == "down" and chin < bar:
            self.stage = "up"
            self.counter += 1

        #print only when the counter has changed the value
        if(self.prev_counter != self.counter):
            print(f"Pull-ups: {self.counter}")
            self.prev_counter = self.counter