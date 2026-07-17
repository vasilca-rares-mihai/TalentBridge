import os
import math
from typing import List

import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model

from shared.schemas.schemas import AttributeUpdate, ChallengeResult
from .base import VideoAnalyzer, mp_pose
from ..utils.geometry import calculate_angle


class LongJumpAnalyzer(VideoAnalyzer):
    """
    Saritura in lungime (standing long jump) — HIBRID, 2 clase: perfect / fall_landing.

    DISCRIMINATORUL = DISTANTA. O saritura te duce IN FATA pe o distanta; orice altceva
    (mers inapoi, ridicare de pe jos dupa cadere, balansul de prep, tremurul de detectie)
    ramane pe loc. Mersul inapoi nici nu produce zbor (un picior mereu pe sol).
    Asa numaram doar sarituri reale, FARA sa taiem caderile (care au zbor mic din natura lor).

      * 1D CNN da verdictul principal (perfect / fall_landing) pe fereastra aliniata.
      * Euristica (caderea soldului dupa aterizare) corecteaza cazurile clare.
      * Scor leaderboard = cea mai buna distanta (doar din sarituri corecte).
    """

    LM_NAMES = [
        'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
        'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
        'left_foot_index', 'right_foot_index',
    ]

    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Long Jump Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model = load_model(os.path.join(current_dir, 'data/model_jump_30f.h5'))
        self.clase = np.load(os.path.join(current_dir, 'data/clase_jump_30f.npy'), allow_pickle=True)
        self.scaler = joblib.load(os.path.join(current_dir, 'data/scaler_jump_30f.pkl'))

        self.WINDOW_SIZE = 30
        self.FEATS = 64

        self.total_repetitii = 0
        self.corecte = 0
        self.greseli = {'fall_landing': 0}
        self.predictie_curenta = "Asteptare"

        self.stare_miscare = "STAND"
        self.PRE_CONTEXT = 5
        self.COOLDOWN = 10
        self.LOAD_KNEE = 150
        self.AIR_MARGIN = 0.04
        self.MIN_FLIGHT = 3

        self.pre = []
        self.jump_buf = None
        self.flight_frames = 0
        self.cooldown = 0
        self.ground_y = 0.0
        self.stand_span_y = 0.0

        self.takeoff_x = None
        self.last_distance_m = 0.0
        self.best_distance_m = 0.0
        self.air_peak = 0.0
        self.MIN_JUMP_DIST = 0.20

        self.takeoff_hip_y = 0.0
        self.max_hip_y_land = 0.0
        self.FALL_DROP = 0.20
        self.NO_FALL_DROP = 0.10

        self.cur_knee = 180.0
        self.cur_ankle_y = 1.0
        self.cur_hip_x = 0.5
        self.cur_hip_y = 0.5
        self.cur_sh_y = 0.4

    def _P(self, landmarks, name):
        return landmarks[getattr(mp_pose.PoseLandmark, name.upper()).value]

    def extractLandmarks(self, landmarks):
        pts = {n: self._P(landmarks, n) for n in self.LM_NAMES}

        mhx = (pts['left_hip'].x + pts['right_hip'].x) / 2.0
        mhy = (pts['left_hip'].y + pts['right_hip'].y) / 2.0
        mhz = (pts['left_hip'].z + pts['right_hip'].z) / 2.0
        msx = (pts['left_shoulder'].x + pts['right_shoulder'].x) / 2.0
        msy = (pts['left_shoulder'].y + pts['right_shoulder'].y) / 2.0
        msz = (pts['left_shoulder'].z + pts['right_shoulder'].z) / 2.0
        scale = math.sqrt((msx - mhx) ** 2 + (msy - mhy) ** 2 + (msz - mhz) ** 2)
        if scale < 0.001:
            scale = 1.0

        feats = []
        for n in self.LM_NAMES:
            lm = pts[n]
            feats.extend([(lm.x - mhx) / scale, (lm.y - mhy) / scale, (lm.z - mhz) / scale, lm.visibility])

        def g(n):
            return [pts[n].x, pts[n].y]

        feats.extend([
            calculate_angle(g('left_hip'), g('left_knee'), g('left_ankle')),
            calculate_angle(g('right_hip'), g('right_knee'), g('right_ankle')),
            calculate_angle(g('left_shoulder'), g('left_hip'), g('left_knee')),
            calculate_angle(g('right_shoulder'), g('right_hip'), g('right_knee')),
            calculate_angle(g('left_shoulder'), g('left_elbow'), g('left_wrist')),
            calculate_angle(g('right_shoulder'), g('right_elbow'), g('right_wrist')),
            calculate_angle(g('left_hip'), g('left_shoulder'), g('left_elbow')),
            calculate_angle(g('right_hip'), g('right_shoulder'), g('right_elbow')),
        ])

        self.cur_knee = (feats[56] + feats[57]) / 2.0
        self.cur_ankle_y = max(pts['left_ankle'].y, pts['right_ankle'].y)
        self.cur_hip_x = mhx
        self.cur_hip_y = mhy
        self.cur_sh_y = msy
        return feats

    def _distanta_m(self, dx_norm):
        if self.stand_span_y < 0.01 or self.h <= 0 or not self.athlete_height:
            return 0.0
        metri_pe_unitate_y = (0.8 * self.athlete_height) / self.stand_span_y
        aspect = self.w / self.h if self.h else 1.0
        return abs(dx_norm) * aspect * metri_pe_unitate_y

    def _resample(self, buf):
        if len(buf) >= self.WINDOW_SIZE:
            idx = np.linspace(0, len(buf) - 1, self.WINDOW_SIZE).astype(int)
            return [buf[i] for i in idx]
        return buf + [buf[-1]] * (self.WINDOW_SIZE - len(buf))

    def checkRep(self, feats):
        knee = self.cur_knee

        if self.jump_buf is not None:
            self.jump_buf.append(feats)
        else:
            self.pre.append(feats)
            self.pre = self.pre[-self.PRE_CONTEXT:]

        if self.stare_miscare == "STAND":
            self.ground_y = max(self.ground_y, self.cur_ankle_y)
            self.stand_span_y = max(self.stand_span_y, self.cur_ankle_y - self.cur_sh_y)
            if knee < self.LOAD_KNEE:
                self.stare_miscare = "LOAD"
                self.flight_frames = 0
                self.air_peak = 0.0
                self.jump_buf = list(self.pre)
                self.takeoff_x = self.cur_hip_x
                self.takeoff_hip_y = self.cur_hip_y
                self.max_hip_y_land = self.cur_hip_y

        elif self.stare_miscare == "LOAD":
            if self.cur_ankle_y < self.ground_y - self.AIR_MARGIN:
                self.stare_miscare = "FLIGHT"
                self.takeoff_x = self.cur_hip_x
                self.takeoff_hip_y = self.cur_hip_y

        elif self.stare_miscare == "FLIGHT":
            self.flight_frames += 1
            self.air_peak = max(self.air_peak, self.ground_y - self.cur_ankle_y)
            if self.cur_ankle_y >= self.ground_y - self.AIR_MARGIN and self.flight_frames >= self.MIN_FLIGHT:
                self.stare_miscare = "LAND"
                self.cooldown = self.COOLDOWN
                self.last_distance_m = self._distanta_m(self.cur_hip_x - self.takeoff_x)

        elif self.stare_miscare == "LAND":
            self.max_hip_y_land = max(self.max_hip_y_land, self.cur_hip_y)
            self.cooldown -= 1
            if self.cooldown <= 0:
                self._finalizeaza()
                self.jump_buf = None
                self.pre = []
                self.stare_miscare = "STAND"

    def _finalizeaza(self):
        hip_drop = self.max_hip_y_land - self.takeoff_hip_y

        if self.last_distance_m < self.MIN_JUMP_DIST:
            print(f"  [diag] ignorat (pe loc) | dist={self.last_distance_m:.2f} air={self.air_peak:.3f} drop={hip_drop:.3f}")
            return

        rep = self._resample(self.jump_buf)
        x = np.array(rep, dtype=np.float32).reshape(1, -1)
        x = self.scaler.transform(x).reshape(1, self.WINDOW_SIZE, self.FEATS)
        pred = self.model.predict(x, verbose=0)
        verdict = str(self.clase[int(np.argmax(pred))])

        if hip_drop > self.FALL_DROP:
            verdict = "fall_landing"
        elif hip_drop < self.NO_FALL_DROP and verdict == "fall_landing":
            verdict = "perfect"

        self.total_repetitii += 1
        self.counter = self.total_repetitii
        self.predictie_curenta = verdict

        if verdict == "perfect":
            self.corecte += 1
            if self.last_distance_m > self.best_distance_m:
                self.best_distance_m = self.last_distance_m
        elif verdict in self.greseli:
            self.greseli[verdict] += 1

        print(f"Saritura {self.total_repetitii}: {verdict.upper()} | dist={self.last_distance_m:.2f}m "
              f"air={self.air_peak:.3f} drop={hip_drop:.3f} | Best: {self.best_distance_m:.2f}m")

    def displayInfo(self, _feats, image):
        cv2.putText(image, f"Corecte: {self.corecte}/{self.total_repetitii}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        culoare = (0, 255, 0) if self.predictie_curenta == 'perfect' else (0, 0, 255)
        cv2.putText(image, f"Status: {self.predictie_curenta.upper()}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, culoare, 2)
        cv2.putText(image, f"Best: {self.best_distance_m:.2f} m", (30, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(image, f"Faza: {self.stare_miscare}", (30, 155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    def getScore(self):
        return round(float(self.best_distance_m), 2)

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        strength_ids = {1, 2, 3, 4}
        total_score = 0
        for challenge in challenges_results:
            if challenge.challenge_id in strength_ids:
                total_score += challenge.result_value
        return AttributeUpdate(strength=int(total_score * 10))
