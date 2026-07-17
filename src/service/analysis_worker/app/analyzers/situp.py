import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from collections import Counter
from typing import List
import os

from shared.schemas.schemas import AttributeUpdate, ChallengeResult
from .base import VideoAnalyzer, mp_pose
from ..utils.geometry import calculate_angle, drawLine, extract_pose_landmarks



class SitupAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Sit-up Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        cale_model = os.path.join(current_dir, 'data/model_situps.h5')
        cale_clase = os.path.join(current_dir, 'data/clase_situps.npy')
        cale_scaler = os.path.join(current_dir, 'data/scaler_situps.pkl')

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
            'feet_lifting': 0,
            'uncompleted': 0
        }

        self.stare_miscare = "JOS"
        self.verdict_repetitie = "perfect"

    def normalizeaza_3d(self, punct, referinta):
        return [punct.x - referinta.x, punct.y - referinta.y, punct.z - referinta.z]

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

        norm_umar = self.normalizeaza_3d(p_umar, p_sold)
        norm_cot = self.normalizeaza_3d(p_cot, p_sold)
        norm_inch = self.normalizeaza_3d(p_inch, p_sold)
        norm_gen = self.normalizeaza_3d(p_gen, p_sold)
        norm_glez = self.normalizeaza_3d(p_glez, p_sold)

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
        unghi_sold_curent = date_cadru_curent[2]
        self.buffer_cadre.append(date_cadru_curent)

        if len(self.buffer_cadre) == self.WINDOW_SIZE:

            buffer_plat = np.array(self.buffer_cadre)
            fereastra_liniara = buffer_plat.reshape(1, -1)
            fereastra_scalata_liniara = self.scaler.transform(fereastra_liniara)
            input_model = fereastra_scalata_liniara.reshape(1, self.WINDOW_SIZE, 19)

            predictii_brute = self.model.predict(input_model, verbose=0)
            clasa_ghicita = self.clase[np.argmax(predictii_brute)]

            self.istoric_predictii.append(clasa_ghicita)
            if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
                self.istoric_predictii.pop(0)

            voturi = Counter(self.istoric_predictii)
            self.predictie_curenta = voturi.most_common(1)[0][0]

            if unghi_sold_curent < 100 and self.stare_miscare == "JOS":
                self.stare_miscare = "SUS"
                self.predictii_sus = []
                self.min_unghi_sold = 180

            if self.stare_miscare == "SUS":
                self.predictii_sus.append(self.predictie_curenta)
                if unghi_sold_curent < self.min_unghi_sold:
                    self.min_unghi_sold = unghi_sold_curent

            if unghi_sold_curent > 115 and self.stare_miscare == "SUS":
                self.stare_miscare = "JOS"
                self.total_repetitii += 1
                self.counter = self.total_repetitii

                if "feet_lifting" in self.predictii_sus:
                    self.verdict_repetitie = "feet_lifting"
                else:
                    if self.min_unghi_sold > 75:
                        self.verdict_repetitie = "uncompleted"
                    elif "perfect" in self.predictii_sus:
                        self.verdict_repetitie = "perfect"
                    else:
                        self.verdict_repetitie = "uncompleted"

                if self.verdict_repetitie == "perfect":
                    self.corecte += 1
                    print(f"Abdomen {self.total_repetitii}: PERFECT!")
                else:
                    if self.verdict_repetitie in self.greseli:
                        self.greseli[self.verdict_repetitie] += 1
                    print(f"Abdomen {self.total_repetitii}: GRESIT ({self.verdict_repetitie.upper()})")

            self.buffer_cadre.pop(0)

    def displayInfo(self, date_cadru_curent, image):
        cv2.putText(image, f"Corecte: {self.corecte}/{self.total_repetitii}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        culoare_status = (0, 255, 0) if self.verdict_repetitie == 'perfect' else (0, 0, 255)
        cv2.putText(image, f"Verdict: {self.verdict_repetitie.upper()}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8,culoare_status,2)

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        core_ids = {4, 5}
        total_score = 0

        for challenge in challenges_results:
            if challenge.challenge_id in core_ids:
                total_score += challenge.result_value

        return AttributeUpdate(strength=int(total_score * 10))