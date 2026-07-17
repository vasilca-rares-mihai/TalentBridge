import cv2
import time
import mediapipe as mp
from abc import ABC, abstractmethod

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.7
)

class VideoAnalyzer(ABC):
    def __init__(self, video_path, window_name="Training Analysis", output_path=None):
        self.video_path = video_path
        self.output_path = output_path
        self.window_name = window_name
        self.cap = cv2.VideoCapture(video_path)

        self.stage = "initial"
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.writer = None
        if self.output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, (self.w, self.h))
        self.prev_counter = None

        self.angle1 = 0
        self.angle2 = 0
        self.counter = 0
        self.speed = 0
        self.distance = 0

        self.athlete_age = None
        self.athlete_gender = None
        self.athlete_height = None
        self.athlete_weight = None




    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    @abstractmethod
    def extractLandmarks(self, landmarks):
        pass

    @abstractmethod
    def checkRep(self, landmarks_data):
        pass

    @abstractmethod
    def displayInfo(self, landmarks_data, image):
        pass

    @abstractmethod
    def calculateAttribute(self):
        pass

    def getScore(self):
        corecte = getattr(self, "corecte", None)
        if corecte is not None:
            return int(corecte)
        return int(getattr(self, "counter", 0) or 0)

    def build_summary(self):
        summary = {
            "exercise": self.__class__.__name__.replace("Analyzer", ""),
            "reps": int(getattr(self, "counter", 0) or 0),
        }
        total = getattr(self, "total_repetitii", None)
        correct = getattr(self, "corecte", None)
        if total is not None and correct is not None:
            summary["correct"] = int(correct)
            summary["total"] = int(total)
            summary["accuracy"] = round(100.0 * correct / total, 1) if total else 0.0
        greseli = getattr(self, "greseli", None)
        if isinstance(greseli, dict):
            summary["mistakes"] = {k: int(v) for k, v in greseli.items()}
        best_dist = getattr(self, "best_distance_m", None)
        if best_dist is not None:
            summary["best_distance_m"] = round(float(best_dist), 2)
        spd = getattr(self, "speed", None)
        if spd:
            summary["speed_ms"] = round(float(spd), 2)
        return summary

    def analyze(self, athlete):
        self.athlete_age = athlete.age
        self.athlete_gender = athlete.gender
        self.athlete_height = athlete.height
        self.athlete_weight = athlete.weight
        print(f"Type of analysis: {self.__class__.__name__}")

        start_time = time.time()

        with mp_pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    landmarks_data = self.extractLandmarks(landmarks)
                    self.checkRep(landmarks_data)

                    if self.writer:
                        self.displayInfo(landmarks_data, frame)
                        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                if self.writer:
                    cv2.putText(frame, f"FPS: {int(self.fps)}", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    self.writer.write(frame)

        elapsed = time.time() - start_time
        print(f"Analysis completed. Total repetitions: {self.counter}")
        print(f"Durata analiza: {elapsed:.1f}s ({int(elapsed // 60)}m {int(elapsed % 60)}s)")
        self.cap.release()
        cv2.destroyAllWindows()
        return self.counter

