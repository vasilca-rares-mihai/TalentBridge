import cv2
from .base import VideoAnalyzer, mp_pose
from utils import calculate_angle, drawLine, extract_pose_landmarks
from .exercise_thresholds import ExerciseThresholds

class PushupAnalyzer(VideoAnalyzer):
    def __init__(self, video_path):
        super().__init__(video_path, window_name="Push-up Analysis")

    # function that extracts the coordinates of key points from the image and returns them
    def extractLandmarks(self, landmarks):
        landmark_name = [
            "LEFT_SHOULDER",
            "RIGHT_SHOULDER",
            "LEFT_ELBOW",
            "RIGHT_ELBOW",
            "LEFT_WRIST",
            "RIGHT_WRIST",

            "LEFT_HEEL",
            "LEFT_KNEE",
            "LEFT_HIP"
        ]
        coords = extract_pose_landmarks(landmarks, landmark_name)

        return coords

    #function I used to draw some information, for exemple: body position for pushups
    def displayInfo(self, coords, image):

        drawLine(image, coords["LEFT_HEEL"], coords["LEFT_KNEE"])
        drawLine(image, coords["LEFT_KNEE"], coords["LEFT_HIP"])
        drawLine(image, coords["LEFT_HIP"], coords["LEFT_SHOULDER"])

        cv2.putText(image, self.stage, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 192, 203), 2)
        h, w, _ = image.shape
        kneeL_coords = (int(coords["LEFT_KNEE"][0] * w), int(coords["LEFT_KNEE"][1] * h))
        cv2.putText(image, str(int(calculate_angle(coords["LEFT_HEEL"], coords["LEFT_KNEE"], coords["LEFT_HIP"]))), kneeL_coords, cv2.FONT_HERSHEY_DUPLEX , 0.5, (255, 192, 203), 2)
        hipL_coords = (int(coords["LEFT_HIP"][0] * w), int(coords["LEFT_HIP"][1] * h))
        cv2.putText(image, str(int(calculate_angle(coords["LEFT_KNEE"], coords["LEFT_HIP"], coords["LEFT_SHOULDER"]))), hipL_coords, cv2.FONT_HERSHEY_DUPLEX , 0.5, (255, 192, 203), 2 )
        elbowL_coords = (int(coords["LEFT_ELBOW"][0] * w), int(coords["LEFT_ELBOW"][1] * h))
        cv2.putText(image, str(int(calculate_angle(coords["LEFT_SHOULDER"], coords["LEFT_ELBOW"], coords["LEFT_WRIST"]))), elbowL_coords, cv2.FONT_HERSHEY_DUPLEX , 0.5, (255, 192, 203), 2)

    def checkRep(self, coords):

        if(calculate_angle(coords["LEFT_HEEL"], coords["LEFT_KNEE"], coords["LEFT_HIP"]) > 145 and calculate_angle(coords["LEFT_KNEE"], coords["LEFT_HIP"], coords["LEFT_SHOULDER"]) > 145):
            # angle1 for left arm
            self.angle1 = calculate_angle(coords["LEFT_SHOULDER"], coords["LEFT_ELBOW"], coords["LEFT_WRIST"])
            #angle2 for right arm
            self.angle2 = calculate_angle(coords["RIGHT_SHOULDER"], coords["RIGHT_ELBOW"], coords["RIGHT_WRIST"])
            if self.angle1 < ExerciseThresholds.PUSHUP_DOWN_ANGLE and self.angle2 < ExerciseThresholds.PUSHUP_DOWN_ANGLE:
                self.stage = "down"
            if self.angle1 > ExerciseThresholds.PUSHUP_UP_ANGLE and  self.angle2 > ExerciseThresholds.PUSHUP_UP_ANGLE and self.stage == "down":
                self.stage = "up"
                self.counter += 1
        else:
            print("INCORRECT BODY POSITION!!!")

        #print only when the counter has changed the value
        if self.prev_counter != self.counter:
            print(f"Push-ups: {self.counter}")
            self.prev_counter = self.counter