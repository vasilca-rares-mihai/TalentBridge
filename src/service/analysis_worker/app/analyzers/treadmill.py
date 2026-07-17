import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from collections import Counter
from typing import List
import os

from shared.models.sql_models import Attribute
from shared.schemas.schemas import AttributeUpdate, ChallengeResult
from .base import VideoAnalyzer, mp_pose
from .filter import OneEuroFilter
from ..utils.geometry import drawLine


class StepAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Running Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        cale_model = os.path.join(current_dir, 'data/model_run.h5')
        cale_clase = os.path.join(current_dir, 'data/clase_run.npy')
        cale_scaler_meta = os.path.join(current_dir, 'data/scaler_meta.pkl')
        cale_scaler_seq = os.path.join(current_dir, 'data/scaler_seq.pkl')

        if not os.path.exists(cale_model):
            print(f"Nu gasesc modelul AI la: {cale_model}")

        self.model = load_model(cale_model)
        self.clase = np.load(cale_clase, allow_pickle=True)
        self.scaler_meta = joblib.load(cale_scaler_meta)
        self.scaler_seq = joblib.load(cale_scaler_seq)

        self.WINDOW_SIZE = 30
        self.buffer_cadre = []
        self.LUNGIME_VOTARE = 15
        self.istoric_predictii = []
        self.predictie_curenta = "Asteptare"

        self.filter_left = OneEuroFilter(min_cutoff=1.0, beta=2.0, freq=30.0)
        self.filter_right = OneEuroFilter(min_cutoff=1.0, beta=2.0, freq=30.0)
        self.L = 0
        self.counter = 0
        self.frame_count = 0
        self.last_step_frame = 0
        self.video_timer = 0.0

        self.KP_NAMES = [
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_hip", "right_hip", "left_knee", "right_knee",
            "left_ankle", "right_ankle", "left_heel", "right_heel",
            "left_foot_index", "right_foot_index"
        ]

    def calc_angle_2d(self, a, b, c):
        """Unghi ABC in grade (b = varf)"""
        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)
        cos_a = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
        return float(np.degrees(np.arccos(np.clip(cos_a, -1.0, 1.0))))

    def extractLandmarks(self, landmarks):
        def get_pt(lm_enum):
            pt = landmarks[lm_enum.value]
            return [pt.x, pt.y]

        p = {
            "left_shoulder": get_pt(mp_pose.PoseLandmark.LEFT_SHOULDER),
            "right_shoulder": get_pt(mp_pose.PoseLandmark.RIGHT_SHOULDER),
            "left_elbow": get_pt(mp_pose.PoseLandmark.LEFT_ELBOW),
            "right_elbow": get_pt(mp_pose.PoseLandmark.RIGHT_ELBOW),
            "left_hip": get_pt(mp_pose.PoseLandmark.LEFT_HIP),
            "right_hip": get_pt(mp_pose.PoseLandmark.RIGHT_HIP),
            "left_knee": get_pt(mp_pose.PoseLandmark.LEFT_KNEE),
            "right_knee": get_pt(mp_pose.PoseLandmark.RIGHT_KNEE),
            "left_ankle": get_pt(mp_pose.PoseLandmark.LEFT_ANKLE),
            "right_ankle": get_pt(mp_pose.PoseLandmark.RIGHT_ANKLE),
            "left_heel": get_pt(mp_pose.PoseLandmark.LEFT_HEEL),
            "right_heel": get_pt(mp_pose.PoseLandmark.RIGHT_HEEL),
            "left_foot_index": get_pt(mp_pose.PoseLandmark.LEFT_FOOT_INDEX),
            "right_foot_index": get_pt(mp_pose.PoseLandmark.RIGHT_FOOT_INDEX),
            "left_wrist": get_pt(mp_pose.PoseLandmark.LEFT_WRIST),
            "right_wrist": get_pt(mp_pose.PoseLandmark.RIGHT_WRIST)
        }

        unghi_genunchi_stang = self.calc_angle_2d(p["left_hip"], p["left_knee"], p["left_ankle"])
        unghi_genunchi_drept = self.calc_angle_2d(p["right_hip"], p["right_knee"], p["right_ankle"])
        unghi_sold_stang = self.calc_angle_2d(p["left_shoulder"], p["left_hip"], p["left_knee"])
        unghi_sold_drept = self.calc_angle_2d(p["right_shoulder"], p["right_hip"], p["right_knee"])
        unghi_glezna_stang = self.calc_angle_2d(p["left_knee"], p["left_ankle"], p["left_foot_index"])
        unghi_glezna_drept = self.calc_angle_2d(p["right_knee"], p["right_ankle"], p["right_foot_index"])

        mid_sh = [(p["left_shoulder"][0] + p["right_shoulder"][0]) / 2,
                  (p["left_shoulder"][1] + p["right_shoulder"][1]) / 2]
        mid_hip = [(p["left_hip"][0] + p["right_hip"][0]) / 2,
                   (p["left_hip"][1] + p["right_hip"][1]) / 2]
        vert = [mid_hip[0], mid_hip[1] + 0.10]
        unghi_trunchi = self.calc_angle_2d(mid_sh, mid_hip, vert)

        unghi_brat_stang = self.calc_angle_2d(p["left_shoulder"], p["left_elbow"], p["left_wrist"])
        unghi_brat_drept = self.calc_angle_2d(p["right_shoulder"], p["right_elbow"], p["right_wrist"])

        date_cadru_curent = []
        for kp in self.KP_NAMES:
            date_cadru_curent.extend([p[kp][0], p[kp][1]])

        date_cadru_curent.extend([
            unghi_genunchi_stang, unghi_genunchi_drept,
            unghi_sold_stang, unghi_sold_drept,
            unghi_glezna_stang, unghi_glezna_drept,
            unghi_trunchi, unghi_brat_stang, unghi_brat_drept
        ])

        return {
            "features_ai": date_cadru_curent,
            "left_heel_raw": p["left_heel"],
            "right_heel_raw": p["right_heel"]
        }

    def checkRep(self, date_procesate):
        self.frame_count += 1
        self.buffer_cadre.append(date_procesate["features_ai"])

        if len(self.buffer_cadre) == self.WINDOW_SIZE:
            fereastra_bruta = np.array(self.buffer_cadre)
            fereastra_scalata = self.scaler_seq.transform(fereastra_bruta)

            flat_kp = []
            for ki, kn in enumerate(self.KP_NAMES):
                for f in range(self.WINDOW_SIZE):
                    flat_kp.append(fereastra_scalata[f][ki * 2])
                    flat_kp.append(fereastra_scalata[f][ki * 2 + 1])

            flat_angles = []
            for ai in range(9):
                for f in range(self.WINDOW_SIZE):
                    flat_angles.append(fereastra_scalata[f][28 + ai])

            seq_scaled_flat = np.array([flat_kp + flat_angles])

            ankle_x = np.array([self.buffer_cadre[f][16] for f in range(self.WINDOW_SIZE)])
            vel = np.diff(ankle_x)
            steps_in_window = sum(1 for i in range(len(vel) - 1) if vel[i] <= 0 < vel[i + 1])

            win_sec = self.WINDOW_SIZE / self.fps
            cadence_spm = (steps_in_window / win_sec) * 60.0
            ankle_range = float(np.max(ankle_x) - np.min(ankle_x))
            step_length_m = max(0.30, ankle_range * 3.5)
            speed_ms = cadence_spm * step_length_m / 60.0
            distance_m = speed_ms * win_sec

            metrics_raw = np.array([[steps_in_window, win_sec, cadence_spm, speed_ms, distance_m]])
            metrics_scaled = self.scaler_meta.transform(metrics_raw)

            if len(self.model.inputs) == 2:
                expected_shape_0 = self.model.inputs[0].shape.as_list()
                if len(expected_shape_0) == 3:
                    input_seq = fereastra_scalata.reshape(1, self.WINDOW_SIZE, 37)
                    input_model = [input_seq, metrics_scaled]
                else:
                    input_model = [seq_scaled_flat, metrics_scaled]
            else:
                input_model = np.hstack([seq_scaled_flat, metrics_scaled])

            predictii_brute = self.model.predict(input_model, verbose=0)
            clasa_ghicita = self.clase[np.argmax(predictii_brute)]

            self.istoric_predictii.append(clasa_ghicita)
            if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
                self.istoric_predictii.pop(0)

            voturi = Counter(self.istoric_predictii)
            self.predictie_curenta = voturi.most_common(1)[0][0]

            self.buffer_cadre.pop(0)

        left_x_raw = date_procesate["left_heel_raw"][0]
        right_x_raw = date_procesate["right_heel_raw"][0]

        l_smooth = self.filter_left.apply(left_x_raw)
        r_smooth = self.filter_right.apply(right_x_raw)

        prag_sensibil = 0.015
        cooldown_frames = 5

        self.distance = self.calculateDistance()
        self.speed = self.calculateSpeed(self.distance)

        if (self.frame_count - self.last_step_frame) > cooldown_frames:
            if r_smooth < (l_smooth - prag_sensibil) and self.L == 0:
                self.counter += 1
                self.L = 1
                self.last_step_frame = self.frame_count
            elif l_smooth < (r_smooth - prag_sensibil) and self.L == 1:
                self.counter += 1
                self.L = 0
                self.last_step_frame = self.frame_count

    def displayInfo(self, date_procesate, image):
        cv2.putText(image, f"Pasi: {self.counter}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(image, f"Viteza: {self.speed:.2f} m/s", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if self.predictie_curenta == 'perfect':
            culoare_status = (0, 255, 0)
        elif self.predictie_curenta == 'overstriding':
            culoare_status = (0, 165, 255)
        else:
            culoare_status = (0, 0, 255)

        cv2.putText(image, f"Stil AI: {self.predictie_curenta.upper()}", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.9, culoare_status, 2)

    def getScore(self):
        # scor leaderboard = distanta alergata (m)
        return round(float(self.distance), 2)

    def calculateDistance(self):
        return self.counter * self.athlete_height * 0.65

    def calculateSpeed(self, distance):
        self.video_timer += (1.0 / self.fps)
        if self.video_timer > 0:
            return distance / self.video_timer
        return 0

    def calculateAcceleration(self, raw_speed):
        return 1250

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        for challenge_result in challenges_results:
            if challenge_result.challenge_id == 4:
                raw_speed = self.calculateSpeed(challenge_result.result_value)
                acceleration = self.calculateAcceleration(raw_speed)
                return AttributeUpdate(sprint_speed=int(raw_speed), acceleration=int(acceleration))
        return AttributeUpdate()