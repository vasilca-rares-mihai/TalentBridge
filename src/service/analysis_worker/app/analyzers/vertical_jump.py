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
from ..utils.geometry import calculate_angle, drawLine, extract_pose_landmarks


class VerticalJumpAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Vertical Jump Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        cale_model = os.path.join(current_dir, 'data/model_vertical_jump.h5')
        cale_clase = os.path.join(current_dir, 'data/clase_vertical_jump.npy')
        cale_scaler_seq = os.path.join(current_dir, 'data/scaler_seq_vj.pkl')
        cale_scaler_meta = os.path.join(current_dir, 'data/scaler_meta_vj.pkl')

        if not os.path.exists(cale_model):
            print(f"Nu gasesc modelul AI la: {cale_model}")

        self.model = load_model(cale_model)
        self.clase = np.load(cale_clase, allow_pickle=True)
        self.scaler_seq = joblib.load(cale_scaler_seq)
        self.scaler_meta = joblib.load(cale_scaler_meta)

        self.WINDOW_SIZE = 30
        self.buffer_cadre = []

        self.LUNGIME_VOTARE = 15
        self.istoric_predictii = []
        self.predictie_curenta = "Asteptare"

        self.total_repetitii = 0
        self.corecte = 0
        self.greseli = {
            'cu_deplasare_in_fata': 0,
            'un_picior': 0
        }

        self.stare_miscare = "STAND"
        self.verdict_repetitie = "perfect"
        self.cadre_in_aer = 0

        self.ref_x = None
        self.ref_y = None
        self.predictii_zbor = []
        self.best_height = 0.0

        self.CROUCH_Y = 0.60
        self.FLIGHT_Y = 0.52
        self.STAND_Y = 0.58
        self.MIN_AIR_FRAMES = 2
        self.takeoff_hip_x = 0.5
        self.DEPLASARE_THRESHOLD = 0.25

        self._cycle_min_y = 1.0
        self._cycle_saw_flight = False

    def extractLandmarks(self, landmarks):
        kp_mapping = [
            mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER,
            mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_ELBOW,
            mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP,
            mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE,
            mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.RIGHT_ANKLE,
            mp_pose.PoseLandmark.LEFT_HEEL, mp_pose.PoseLandmark.RIGHT_HEEL,
            mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
        ]

        mid_hip_x = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x + landmarks[
            mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2
        mid_hip_y = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y + landmarks[
            mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
        mid_sh_y = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y + landmarks[
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2

        if self.ref_x is None or (self.stare_miscare == "STAND" and mid_hip_y < self.ref_y):
            self.ref_x = mid_hip_x
            self.ref_y = mid_hip_y
            s_val = abs(mid_hip_y - mid_sh_y)
            self.ref_s = s_val if s_val > 0.05 else 0.20

        p = {}
        for kp in kp_mapping:
            norm_x = (landmarks[kp.value].x - self.ref_x) / self.ref_s + 0.50
            norm_y = (landmarks[kp.value].y - self.ref_y) / self.ref_s + 0.55
            p[kp.name.lower()] = [norm_x, norm_y]

        wrist_l = [(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x - self.ref_x) / self.ref_s + 0.50,
                   (landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y - self.ref_y) / self.ref_s + 0.55]
        wrist_r = [(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x - self.ref_x) / self.ref_s + 0.50,
                   (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y - self.ref_y) / self.ref_s + 0.55]

        u_gen_s = calculate_angle(p["left_hip"], p["left_knee"], p["left_ankle"])
        u_gen_d = calculate_angle(p["right_hip"], p["right_knee"], p["right_ankle"])
        u_sold_s = calculate_angle(p["left_shoulder"], p["left_hip"], p["left_knee"])
        u_sold_d = calculate_angle(p["right_shoulder"], p["right_hip"], p["right_knee"])
        u_gle_s = calculate_angle(p["left_knee"], p["left_ankle"], p["left_foot_index"])
        u_gle_d = calculate_angle(p["right_knee"], p["right_ankle"], p["right_foot_index"])

        mid_sh = [(p["left_shoulder"][0] + p["right_shoulder"][0]) / 2,
                  (p["left_shoulder"][1] + p["right_shoulder"][1]) / 2]
        mid_p_hip = [(p["left_hip"][0] + p["right_hip"][0]) / 2, (p["left_hip"][1] + p["right_hip"][1]) / 2]
        vert = [mid_p_hip[0], mid_p_hip[1] + 0.10]
        u_trunchi = calculate_angle(mid_sh, mid_p_hip, vert)

        u_brat_s = calculate_angle(p["left_shoulder"], p["left_elbow"], wrist_l)
        u_brat_d = calculate_angle(p["right_shoulder"], p["right_elbow"], wrist_r)

        date_cadru_curent = []
        for kp in kp_mapping:
            date_cadru_curent.extend([p[kp.name.lower()][0], p[kp.name.lower()][1]])
        date_cadru_curent.extend(
            [u_gen_s, u_gen_d, u_sold_s, u_sold_d, u_gle_s, u_gle_d, u_trunchi, u_brat_s, u_brat_d])
        
        return date_cadru_curent

    def checkRep(self, date_cadru_curent):
        if date_cadru_curent:
            self.buffer_cadre.append(date_cadru_curent)

            y_curent_sold = (date_cadru_curent[9] + date_cadru_curent[11]) / 2

            if len(self.buffer_cadre) > self.WINDOW_SIZE:
                self.buffer_cadre.pop(0)

            if len(self.buffer_cadre) == self.WINDOW_SIZE and self.stare_miscare in ("SQUAT", "FLIGHT"):
                buffer_plat = np.array(self.buffer_cadre, dtype=np.float32)
                fereastra_scalata = self.scaler_seq.transform(buffer_plat.reshape(-1, 37)).reshape(1, self.WINDOW_SIZE, 37)

                jumps_in_window = 1 if self.stare_miscare in ["FLIGHT", "LAND"] else 0
                win_sec = self.WINDOW_SIZE / 30.0

                max_inaltime = 0.0
                cadre_intinse = 0
                for c in self.buffer_cadre:
                    y_s = (c[9] + c[11]) / 2
                    h = max(0.0, float(0.55 - y_s) * 1.5)
                    if h > max_inaltime:
                        max_inaltime = h
                    if (c[28] + c[29]) / 2 > 160:
                        cadre_intinse += 1

                estimare_inaltime_m = max_inaltime
                self.best_height = max(self.best_height, max_inaltime)
                takeoff_velocity = max_inaltime * 4.5
                hang_time_sec = (cadre_intinse / 30.0) if cadre_intinse > 0 else 0.20

                c_first = self.buffer_cadre[0]
                c_last = self.buffer_cadre[-1]
                x_first = (c_first[8] + c_first[10]) / 2
                x_last = (c_last[8] + c_last[10]) / 2
                horiz_disp = abs(x_last - x_first)

                meta_raw = np.array(
                    [[jumps_in_window, horiz_disp, estimare_inaltime_m, takeoff_velocity, hang_time_sec]],
                    dtype=np.float32)
                meta_scalata = self.scaler_meta.transform(meta_raw)

                predictii_brute = self.model(
                    {"input_sequence": fereastra_scalata, "input_meta": meta_scalata},
                    training=False
                ).numpy()
                self.predictie_curenta = self.clase[np.argmax(predictii_brute)]

            if y_curent_sold > self.CROUCH_Y and self.stare_miscare in ["STAND", "LAND"]:
                self.stare_miscare = "SQUAT"
                self.cadre_in_aer = 0
                self.predictii_zbor = []
                self.start_hip_x = (date_cadru_curent[8] + date_cadru_curent[10]) / 2
                self.start_sh_width = abs(date_cadru_curent[0] - date_cadru_curent[2])

            if y_curent_sold < self.FLIGHT_Y and self.stare_miscare in ["SQUAT", "STAND", "LAND"]:
                if date_cadru_curent[28] > 140 or date_cadru_curent[29] > 140:
                    if self.stare_miscare != "FLIGHT":
                        self.cadre_in_aer = 0
                        self.predictii_zbor = []
                        self.takeoff_hip_x = (date_cadru_curent[8] + date_cadru_curent[10]) / 2
                    self.stare_miscare = "FLIGHT"
                    self._cycle_saw_flight = True

            if self.stare_miscare == "FLIGHT":
                self.cadre_in_aer += 1
                if hasattr(self, 'predictie_curenta') and self.predictie_curenta != "Asteptare":
                    self.predictii_zbor.append(self.predictie_curenta)

                if y_curent_sold > self.FLIGHT_Y and self.cadre_in_aer > self.MIN_AIR_FRAMES:
                    self.stare_miscare = "LAND"
                    self.total_repetitii += 1
                    self.counter = self.total_repetitii

                    if self.predictii_zbor:
                        from collections import Counter
                        ultimele_predictii = self.predictii_zbor[-5:]
                        ai_verdict = Counter(ultimele_predictii).most_common(1)[0][0]
                    else:
                        ai_verdict = getattr(self, 'predictie_curenta', "perfect")

                    self.verdict_repetitie = ai_verdict

                    hip_x_now = (date_cadru_curent[8] + date_cadru_curent[10]) / 2
                    deplasare = abs(hip_x_now - self.takeoff_hip_x)
                    if self.verdict_repetitie == "perfect" and deplasare > self.DEPLASARE_THRESHOLD:
                        self.verdict_repetitie = "cu_deplasare_in_fata"

                    print(f"  [diag] Saritura {self.total_repetitii}: AI={ai_verdict} "
                          f"deplasare={deplasare:.3f} -> verdict final={self.verdict_repetitie}")

                    if self.verdict_repetitie == "perfect":
                        self.corecte += 1
                        print(f"Sarituri {self.total_repetitii}: CORECTA (PERFECT)!")
                    else:
                        if self.verdict_repetitie in self.greseli:
                            self.greseli[self.verdict_repetitie] += 1
                        print(f"Sarituri {self.total_repetitii}: DEFECTUOASA ({self.verdict_repetitie.upper()})")

                    print(f"Total Sarituri: {self.total_repetitii} | Corecte: {self.corecte}")

            if y_curent_sold < self.CROUCH_Y and self.stare_miscare == "LAND":
                self.stare_miscare = "STAND"

            self._cycle_min_y = min(self._cycle_min_y, y_curent_sold)
            if y_curent_sold > self.STAND_Y + 0.02 and self.stare_miscare in ["STAND", "LAND"]:
                if self._cycle_min_y < self.STAND_Y - 0.01:
                    detectat = "detectata" if self._cycle_saw_flight else "RATATA"
                    print(f"  [diag] incercare: y_varf={self._cycle_min_y:.3f} "
                          f"(prag_zbor={self.FLIGHT_Y}) -> {detectat}")
                self._cycle_min_y = 1.0
                self._cycle_saw_flight = False

    def displayInfo(self, date_cadru_curent, image):
        cv2.putText(image, f"Sarituri: {self.corecte}/{self.total_repetitii}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        verdict_text = self.verdict_repetitie.upper() if self.verdict_repetitie else "N/A"
        culoare_status = (0, 255, 0) if self.verdict_repetitie == 'perfect' else (0, 0, 255)
        cv2.putText(image, f"AI Verdict: {verdict_text}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, culoare_status, 2)

        cv2.putText(image, f"Faza: {self.stare_miscare}", (30, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    def getScore(self):
        return round(float(self.best_height), 2)

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        leg_power_ids = {4, 5, 6}
        total_score = 0

        for challenge in challenges_results:
            if challenge.challenge_id in leg_power_ids:
                total_score += challenge.result_value

        return AttributeUpdate(agility=int(total_score * 10))