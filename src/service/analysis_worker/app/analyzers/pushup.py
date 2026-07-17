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


class PushupAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Push-up Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        cale_model = os.path.join(current_dir, 'data/model_flotari.h5')
        cale_clase = os.path.join(current_dir, 'data/clase.npy')
        cale_scaler = os.path.join(current_dir, 'data/scaler_flotari.pkl')

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
            'hips too high': 0,
            'knees too low': 0,
            'shoulders first': 0,
            'uncompleted': 0
        }

        self.stare_miscare = "UP"
        self.verdict_repetitie = "Asteptare prima rep..."
        self.cooldown_frames = 0
        self.predictii_si_unghiuri = []
        self.min_unghi_cot_repetitie = 180
        self.min_unghi_sold_repetitie = 180
        self.min_unghi_genunchi_repetitie = 180

        self.constant_scale = 0.0

    def normalizeaza_3d(self, punct, referinta, scale_factor):
        if scale_factor < 0.001:
            scale_factor = 1.0
        return [(punct.x - referinta.x) / scale_factor,
                (punct.y - referinta.y) / scale_factor,
                (punct.z - referinta.z) / scale_factor]

    def extractLandmarks(self, landmarks):
        p_umar = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        p_cot = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        p_inch = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        p_sold = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        p_gen = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        p_glez = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

        umar_2d = [p_umar.x, p_umar.y]
        cot_2d = [p_cot.x, p_cot.y]
        inch_2d = [p_inch.x, p_inch.y]
        sold_2d = [p_sold.x, p_sold.y]
        gen_2d = [p_gen.x, p_gen.y]
        glez_2d = [p_glez.x, p_glez.y]

        unghi_cot = calculate_angle(umar_2d, cot_2d, inch_2d)
        unghi_umar = calculate_angle(sold_2d, umar_2d, cot_2d)
        unghi_sold = calculate_angle(umar_2d, sold_2d, gen_2d)
        unghi_genunchi = calculate_angle(sold_2d, gen_2d, glez_2d)

        s_curent = math.sqrt((p_umar.x - p_sold.x) ** 2 + (p_umar.y - p_sold.y) ** 2 + (p_umar.z - p_sold.z) ** 2)

        if self.stare_miscare == "UP":
            self.constant_scale = max(self.constant_scale, s_curent)

        scale_to_use = self.constant_scale if self.constant_scale > 0.001 else s_curent

        norm_umar = self.normalizeaza_3d(p_umar, p_sold, scale_to_use)
        norm_cot = self.normalizeaza_3d(p_cot, p_sold, scale_to_use)
        norm_inch = self.normalizeaza_3d(p_inch, p_sold, scale_to_use)
        norm_gen = self.normalizeaza_3d(p_gen, p_sold, scale_to_use)
        norm_glez = self.normalizeaza_3d(p_glez, p_sold, scale_to_use)

        date_cadru_curent = [
            unghi_cot, unghi_umar, unghi_sold, unghi_genunchi,
            norm_umar[0], norm_umar[1], norm_umar[2],
            norm_cot[0], norm_cot[1], norm_cot[2],
            norm_inch[0], norm_inch[1], norm_inch[2],
            norm_gen[0], norm_gen[1], norm_gen[2],
            norm_glez[0], norm_glez[1], norm_glez[2]
        ]

        return date_cadru_curent

    def checkRep(self, date_cadru_curent):
        unghi_cot_curent = date_cadru_curent[0]
        unghi_sold_curent = date_cadru_curent[2]
        unghi_genunchi_curent = date_cadru_curent[3]

        self.buffer_cadre.append(date_cadru_curent)

        if len(self.buffer_cadre) == self.WINDOW_SIZE:
            buffer_plat = np.array(self.buffer_cadre)
            fereastra_liniara = buffer_plat.reshape(1, -1)
            fereastra_scalata_liniara = self.scaler.transform(fereastra_liniara)
            input_model = fereastra_scalata_liniara.reshape(1, self.WINDOW_SIZE, 19).astype('float32')

            predictii_brute = self.model(input_model, training=False).numpy()
            clasa_ghicita = self.clase[np.argmax(predictii_brute)]

            self.istoric_predictii.append(clasa_ghicita)
            if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
                self.istoric_predictii.pop(0)

            voturi = Counter(self.istoric_predictii)
            self.predictie_curenta = voturi.most_common(1)[0][0]

            if self.cooldown_frames > 0:
                self.cooldown_frames -= 1
                self.buffer_cadre.pop(0)
                return

            if unghi_cot_curent < 160 and self.stare_miscare == "UP":
                self.stare_miscare = "DOWN"
                self.predictii_si_unghiuri = []
                self.min_unghi_cot_repetitie = unghi_cot_curent
                self.min_unghi_sold_repetitie = unghi_sold_curent
                self.min_unghi_genunchi_repetitie = unghi_genunchi_curent

            if self.stare_miscare == "DOWN":
                self.predictii_si_unghiuri.append((self.predictie_curenta, unghi_cot_curent))

                if unghi_cot_curent < self.min_unghi_cot_repetitie:
                    self.min_unghi_cot_repetitie = unghi_cot_curent
                if unghi_sold_curent < self.min_unghi_sold_repetitie:
                    self.min_unghi_sold_repetitie = unghi_sold_curent
                if unghi_genunchi_curent < self.min_unghi_genunchi_repetitie:
                    self.min_unghi_genunchi_repetitie = unghi_genunchi_curent

            if unghi_cot_curent > 165 and self.stare_miscare == "DOWN":

                if self.min_unghi_cot_repetitie > 135 or self.min_unghi_genunchi_repetitie < 120:
                    self.stare_miscare = "UP"
                    self.buffer_cadre.pop(0)
                    return

                self.stare_miscare = "UP"
                self.total_repetitii += 1
                self.counter = self.total_repetitii

                idx_min = 0
                for i in range(len(self.predictii_si_unghiuri)):
                    if self.predictii_si_unghiuri[i][1] == self.min_unghi_cot_repetitie:
                        idx_min = i
                        break

                idx_start = idx_min
                idx_end = min(idx_min + 15, len(self.predictii_si_unghiuri))
                predictii_valide = [p[0] for p in self.predictii_si_unghiuri[idx_start:idx_end]]

                if not predictii_valide:
                    self.verdict_repetitie = "perfect"
                else:
                    self.verdict_repetitie = Counter(predictii_valide).most_common(1)[0][0]

                if self.verdict_repetitie == "perfect":
                    self.corecte += 1
                    print(f"Repetitia {self.total_repetitii}: PERFECTA!")
                else:
                    if self.verdict_repetitie in self.greseli:
                        self.greseli[self.verdict_repetitie] += 1
                    print(f"Repetitia {self.total_repetitii}: GRESITA ({self.verdict_repetitie.upper()})")

                print(f"Total: {self.total_repetitii} | Corecte: {self.corecte}")

                self.cooldown_frames = 15

            self.buffer_cadre.pop(0)

    def displayInfo(self, date_cadru_curent, image):
        cv2.putText(image, f"Corecte: {self.corecte}/{self.total_repetitii}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        culoare_status = (0, 255, 0) if self.verdict_repetitie == 'perfect' else (0, 0, 255)

        cv2.putText(image, f"Verdict: {self.verdict_repetitie.upper()}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    culoare_status, 2)

        cv2.putText(image, f"Live AI: {self.predictie_curenta.upper()}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (200, 200, 200), 1)

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        strength_ids = {1, 2, 3}
        total_score = 0

        for challenge in challenges_results:
            if challenge.challenge_id in strength_ids:
                total_score += challenge.result_value

        return AttributeUpdate(strength=int(total_score * 10))