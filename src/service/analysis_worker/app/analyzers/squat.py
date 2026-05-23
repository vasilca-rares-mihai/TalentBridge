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

        # Fereastra antrenata e de 30
        self.WINDOW_SIZE = 30
        self.buffer_cadre = []

        # Marim si lungimea de votare ca sa fie stabila predictia pe un window de 30
        self.LUNGIME_VOTARE = 15
        self.istoric_predictii = []
        self.predictie_curenta = "Asteptare"

        self.total_repetitii = 0
        self.corecte = 0

        # Structura pentru greselile antrenate pe setul de date sintetic
        self.greseli = {
            'incomplete': 0,
            'arched_back': 0
        }

        self.stare_miscare = "UP"
        self.verdict_repetitie = "perfect"

    def extractLandmarks(self, landmarks):
        # Functie ajutatoare pentru extragerea (x, y, z, v) din MediaPipe
        def get_landmark_data(lm):
            return [lm.x, lm.y, lm.z, lm.visibility]

        # 1. Extragem punctele (in ordinea exacta din CSV-ul antrenat)
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

        features = []
        features.extend(get_landmark_data(l_sh))
        features.extend(get_landmark_data(r_sh))
        features.extend(get_landmark_data(l_hip))
        features.extend(get_landmark_data(r_hip))
        features.extend(get_landmark_data(l_kn))
        features.extend(get_landmark_data(r_kn))
        features.extend(get_landmark_data(l_an))
        features.extend(get_landmark_data(r_an))
        features.extend(get_landmark_data(l_fi))
        features.extend(get_landmark_data(r_fi))

        # 2. Calculam unghiurile de interes pt ambele picioare
        unghi_sold_l = calculate_angle([l_sh.x, l_sh.y], [l_hip.x, l_hip.y], [l_kn.x, l_kn.y])
        unghi_genunchi_l = calculate_angle([l_hip.x, l_hip.y], [l_kn.x, l_kn.y], [l_an.x, l_an.y])
        unghi_glezna_l = calculate_angle([l_kn.x, l_kn.y], [l_an.x, l_an.y], [l_fi.x, l_fi.y])

        unghi_sold_r = calculate_angle([r_sh.x, r_sh.y], [r_hip.x, r_hip.y], [r_kn.x, r_kn.y])
        unghi_genunchi_r = calculate_angle([r_hip.x, r_hip.y], [r_kn.x, r_kn.y], [r_an.x, r_an.y])
        unghi_glezna_r = calculate_angle([r_kn.x, r_kn.y], [r_an.x, r_an.y], [r_fi.x, r_fi.y])

        features.extend([unghi_sold_l, unghi_genunchi_l, unghi_glezna_l, unghi_sold_r, unghi_genunchi_r, unghi_glezna_r])

        # Array-ul va avea exact 46 de elemente
        return features

    def checkRep(self, date_cadru_curent):
        # Indexul 41 contine 'unghi_genunchi_l' in array-ul nostru de 46 caracteristici
        unghi_genunchi_curent = date_cadru_curent[41]
        self.buffer_cadre.append(date_cadru_curent)

        if len(self.buffer_cadre) == self.WINDOW_SIZE:
            buffer_plat = np.array(self.buffer_cadre)
            fereastra_liniara = buffer_plat.reshape(1, -1)

            # Scalam datele
            fereastra_scalata_liniara = self.scaler.transform(fereastra_liniara)
            # Reshape pentru CNN 1D: (1 batch, 30 frames, 46 features)
            input_model = fereastra_scalata_liniara.reshape(1, self.WINDOW_SIZE, 46)

            # Predictie
            predictii_brute = self.model.predict(input_model, verbose=0)
            idx_clasa = np.argmax(predictii_brute)
            clasa_ghicita = str(self.clase[idx_clasa])

            # Votare pentru stabilitate in timp real
            self.istoric_predictii.append(clasa_ghicita)
            if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
                self.istoric_predictii.pop(0)

            voturi = Counter(self.istoric_predictii)
            self.predictie_curenta = voturi.most_common(1)[0][0]

            # Daca atinge 100 grade genunchiul, a intrat in repeta
            if unghi_genunchi_curent < 100 and self.stare_miscare == "UP":
                self.stare_miscare = "DOWN"
                self.verdict_repetitie = "perfect"

            # In faza de DOWN marcam greseala daca modelul o sesizeaza
            if self.stare_miscare == "DOWN":
                if self.predictie_curenta != "perfect":
                    self.verdict_repetitie = self.predictie_curenta

            # Peste 160 de grade consideram finalul repetarii
            if unghi_genunchi_curent > 160 and self.stare_miscare == "DOWN":
                self.stare_miscare = "UP"
                self.total_repetitii += 1
                self.counter = self.total_repetitii  # variabila inherited din base

                if self.verdict_repetitie == "perfect":
                    self.corecte += 1
                    print(f"Genoflexiunea {self.total_repetitii}: PERFECTA!")
                else:
                    if self.verdict_repetitie in self.greseli:
                        self.greseli[self.verdict_repetitie] += 1
                    print(f"Genoflexiunea {self.total_repetitii}: GRESITA ({self.verdict_repetitie.upper()})")

                print(f"Total Squats: {self.total_repetitii} | Corecte: {self.corecte}")

            self.buffer_cadre.pop(0)

    def displayInfo(self, date_cadru_curent, image):
        # Folosim index 41 pt unghi_genunchi in fereastra pe ecran
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