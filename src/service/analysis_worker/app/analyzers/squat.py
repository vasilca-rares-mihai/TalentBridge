import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from collections import Counter
from typing import List
import os
import math

from shared.models.sql_models import Attribute
from shared.schemas.schemas import AttributeUpdate, ChallengeResult
from .base import VideoAnalyzer, mp_pose
from ..utils.geometry import calculate_angle, drawLine, extract_pose_landmarks
from .exercise_thresholds import ExerciseThresholds


class SquatAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Squat Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        cale_model = os.path.join(current_dir, 'data/model_squats_30f.h5')
        cale_clase = os.path.join(current_dir, 'data/clase_squats_30f.npy')
        cale_scaler = os.path.join(current_dir, 'data/scaler_squats_30f.pkl')

        if not os.path.exists(cale_model):
            print(f"Nu gasesc modelul AI la: {cale_model}")

        self.model = load_model(cale_model)
        self.clase = np.load(cale_clase, allow_pickle=True)
        self.scaler = joblib.load(cale_scaler)

        self.WINDOW_SIZE = 30
        self.buffer_cadre = []

        self.LUNGIME_VOTARE = 15
        self.istoric_predictii = []
        self.predictie_curenta = "Asteptare"

        self.total_repetitii = 0
        self.corecte = 0

        self.greseli = {
            'uncompleted': 0,
            'arched_back': 0
        }

        self.stare_miscare = "UP"
        self.verdict_repetitie = "perfect"

        self.constant_scale = 0.0

        self.cooldown_frames = 0
        self.FAKE_REP_KNEE = 138
        self.INCOMPLETE_KNEE = 120
        self.ARCH_THRESHOLD = 0.10

    def normalizeaza_3d_squat(self, punct, ref_x, ref_y, ref_z, scale_factor, visibility):
        if scale_factor < 0.001:
            scale_factor = 1.0
        return [
            (punct.x - ref_x) / scale_factor,
            (punct.y - ref_y) / scale_factor,
            (punct.z - ref_z) / scale_factor,
            visibility
        ]

    def extractLandmarks(self, landmarks):
        l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        r_sh = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        l_kn = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        r_kn = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        l_an = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        r_an = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        l_fi = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
        r_fi = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]

        mid_hip_x = (l_hip.x + r_hip.x) / 2.0
        mid_hip_y = (l_hip.y + r_hip.y) / 2.0
        mid_hip_z = (l_hip.z + r_hip.z) / 2.0

        mid_sh_x = (l_sh.x + r_sh.x) / 2.0
        mid_sh_y = (l_sh.y + r_sh.y) / 2.0
        mid_sh_z = (l_sh.z + r_sh.z) / 2.0
        s_curent = math.sqrt((mid_sh_x - mid_hip_x)**2 + (mid_sh_y - mid_hip_y)**2 + (mid_sh_z - mid_hip_z)**2)

        if self.stare_miscare == "UP":
            self.constant_scale = max(self.constant_scale, s_curent)

        scale_to_use = self.constant_scale if self.constant_scale > 0.001 else s_curent

        features = []
        for lm in [l_sh, r_sh, l_hip, r_hip, l_kn, r_kn, l_an, r_an, l_fi, r_fi]:
            features.extend(self.normalizeaza_3d_squat(lm, mid_hip_x, mid_hip_y, mid_hip_z, scale_to_use, lm.visibility))

        unghi_sold_l = calculate_angle([l_sh.x, l_sh.y], [l_hip.x, l_hip.y], [l_kn.x, l_kn.y])
        unghi_genunchi_l = calculate_angle([l_hip.x, l_hip.y], [l_kn.x, l_kn.y], [l_an.x, l_an.y])
        unghi_glezna_l = calculate_angle([l_kn.x, l_kn.y], [l_an.x, l_an.y], [l_fi.x, l_fi.y])

        unghi_sold_r = calculate_angle([r_sh.x, r_sh.y], [r_hip.x, r_hip.y], [r_kn.x, r_kn.y])
        unghi_genunchi_r = calculate_angle([r_hip.x, r_hip.y], [r_kn.x, r_kn.y], [r_an.x, r_an.y])
        unghi_glezna_r = calculate_angle([r_kn.x, r_kn.y], [r_an.x, r_an.y], [r_fi.x, r_fi.y])

        features.extend([unghi_sold_l, unghi_genunchi_l, unghi_glezna_l, unghi_sold_r, unghi_genunchi_r, unghi_glezna_r])

        return features

    def checkRep(self, date_cadru_curent):
        unghi_genunchi_curent = date_cadru_curent[41]

        self.buffer_cadre.append(date_cadru_curent)

        if unghi_genunchi_curent < 140 and self.stare_miscare == "UP":
            self.stare_miscare = "DOWN"
            self.buffer_cadre = self.buffer_cadre[-10:]

        if unghi_genunchi_curent > 160 and self.stare_miscare == "DOWN":
            self.stare_miscare = "COOLDOWN"
            self.cooldown_frames = 15

        if self.stare_miscare == "COOLDOWN" and self.cooldown_frames > 0:
            self.cooldown_frames -= 1
            return

        if self.stare_miscare == "COOLDOWN":
            self.stare_miscare = "UP"

            min_knee = min([cadru[41] for cadru in self.buffer_cadre]) if self.buffer_cadre else 180
            if min_knee > self.FAKE_REP_KNEE:
                self.buffer_cadre = []
                return

            self.total_repetitii += 1
            self.counter = self.total_repetitii
            
            if len(self.buffer_cadre) >= 10:
                indici = np.linspace(0, len(self.buffer_cadre) - 1, self.WINDOW_SIZE).astype(int)
                rep_30_cadre = [self.buffer_cadre[idx] for idx in indici]
                
                buffer_plat = np.array(rep_30_cadre)
                fereastra_liniara = buffer_plat.reshape(1, -1)
                
                fereastra_scalata_liniara = self.scaler.transform(fereastra_liniara)
                input_model = fereastra_scalata_liniara.reshape(1, self.WINDOW_SIZE, 46)

                predictii_brute = self.model.predict(input_model, verbose=0)
                idx_clasa = np.argmax(predictii_brute)
                clasa_ghicita = str(self.clase[idx_clasa])

                self.predictie_curenta = clasa_ghicita
                self.verdict_repetitie = clasa_ghicita
                if min_knee > self.INCOMPLETE_KNEE:
                    self.verdict_repetitie = "uncompleted"

                if self.verdict_repetitie == "perfect":
                    self.corecte += 1
                    print(f"Genoflexiunea {self.total_repetitii}: PERFECTA!")
                else:
                    if self.verdict_repetitie in self.greseli:
                        self.greseli[self.verdict_repetitie] += 1
                    print(f"Genoflexiunea {self.total_repetitii}: GRESITA ({self.verdict_repetitie.upper()})")

            print(f"Total Squats: {self.total_repetitii} | Corecte: {self.corecte}")

            self.buffer_cadre = []

    def displayInfo(self, date_cadru_curent, image):
        if len(date_cadru_curent) == 46:
            unghi_genunchi_afisare = int(date_cadru_curent[41])
            cv2.putText(image, f"Unghi Genunchi: {unghi_genunchi_afisare}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 192, 203), 2)

        cv2.putText(image, f"Corecte: {self.corecte}/{self.total_repetitii}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        culoare_status = (0, 255, 0) if self.predictie_curenta == 'perfect' else (0, 0, 255)
        cv2.putText(image, f"Status AI: {self.predictie_curenta.upper()}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    culoare_status, 2)

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        strength_ids = {1, 2, 3}
        total_score = 0

        for challenge in challenges_results:
            if challenge.challenge_id in strength_ids:
                total_score += challenge.result_value

        return AttributeUpdate(strength=int(total_score * 10))