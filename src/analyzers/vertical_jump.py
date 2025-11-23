import cv2
from .base import VideoAnalyzer, mp_pose
from utils import distance_points, drawLine, pxToM, extract_pose_landmarks

class VerticalJumpAnalyzer(VideoAnalyzer):
    def __init__(self, video_path):
        super().__init__(video_path, window_name='Vertical Jump Analysis')
        self.line = None
        self.prev_coord = 1
        self.flag = True
        self.flag2 = True
        self.flag3 = True
        self.list_of_jumps = [0]
        self.jump_height_px = 0
        self.athlete_height_px = None
        self.legs_on_first_frame = (0,0)

    def calculateHeightJump(self):
        self.jump_height_px = self.legs_on_first_frame[1] - self.prev_coord
        self.list_of_jumps.append(pxToM(self.athlete_height, self.jump_height_px, self.athlete_height_px))

    def initializeVariablesForHeight(self, coords):
        if self.flag3:
            self.flag3 = False
            legs = ((coords["RIGHT_HEEL"][0] + coords["LEFT_HEEL"][0]) / 2, (coords["RIGHT_HEEL"][1] + coords["LEFT_HEEL"][1]) / 2)
            head = ((coords["RIGHT_EYE"][0] + coords["LEFT_EYE"][0]) /2, (coords["RIGHT_EYE"][1] + coords["LEFT_EYE"][1]) /2)
            self.athlete_height_px = distance_points(legs, head)
            self.legs_on_first_frame = legs



    #function that extracts the coordinates of key points from the image and returns them
    def extractLandmarks(self, landmarks):
        landmark_name = [
            "RIGHT_HEEL",
            "LEFT_HEEL",
            "RIGHT_KNEE",
            "LEFT_KNEE",
            "RIGHT_EYE",
            "LEFT_EYE"
        ]
        coords = extract_pose_landmarks(landmarks, landmark_name)
        return coords

    #function I used to draw some information, for exemple: the line that shows, when crossed by the athlete's legs, a jump is performed
    def displayInfo(self, coords, image):
        if self.flag:
            self.line = ((coords["RIGHT_HEEL"][1] + coords["LEFT_HEEL"][1]) / 2 + (coords["LEFT_KNEE"][1] + coords["RIGHT_KNEE"][1]) / 2) / 2
            self.flag = False
        drawLine(image, (0,self.line), (300,self.line))
        cv2.putText(image, self.stage, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        drawLine(image, (coords["LEFT_HEEL"][0], self.legs_on_first_frame[1]), coords["LEFT_HEEL"])
        drawLine(image, (coords["RIGHT_HEEL"][0], self.legs_on_first_frame[1]), coords["RIGHT_HEEL"])



    def checkRep(self, coords):
        #the function call that helps me calculate the height in meters of the jump. an initialization of the variables
        self.initializeVariablesForHeight(coords)
        # when yJump decrease, the athlete jumps off the ground. when yJump increase, the athlete lands on the ground
        y_jump = (coords["RIGHT_HEEL"][1] + coords["LEFT_HEEL"][1]) / 2
        if y_jump > self.line:
            self.stage = "down"
            self.flag2 = True
        elif y_jump < self.line and self.stage == "down":
            self.stage = "up"
        #after the line that I consider the jump has been crossed, I start calculating the maximum height jumped and convert it into meters
        if self.prev_coord < (coords["RIGHT_HEEL"][1] + coords["LEFT_HEEL"][1]) / 2 and self.stage == "up" and self.flag2:
            self.flag2 = False
            self.counter += 1
            self.calculateHeightJump()

        self.prev_coord = (coords["RIGHT_HEEL"][1] + coords["LEFT_HEEL"][1]) / 2

        if self.prev_counter != self.counter:
            print(f"Jump: {self.counter}; jump height: {self.list_of_jumps[self.counter]} m")
            self.prev_counter = self.counter
















