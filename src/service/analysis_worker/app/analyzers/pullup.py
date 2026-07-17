import os
import math
from collections import Counter
from typing import List

import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model

from shared.schemas.schemas import AttributeUpdate, ChallengeResult
from .base import VideoAnalyzer, mp_pose
from ..utils.geometry import calculate_angle


class PullupAnalyzer(VideoAnalyzer):
    """
    Analizor pullup pe acelasi tipar ca PushupAnalyzer:
    - extrage 19 features / cadru (identic cu extract_pullups.py),
    - clasifica forma cu un model CNN 1D pe ferestre de 30 de cadre,
    - numara repetarile cu o masinarie de stari (hang -> pull -> hang)
      bazata pe unghiul cotului si pe "barbia peste bara",
    - aplica euristici geometrice care suprascriu cazurile clare.

    Clase: perfect, uncompleted, no_full_extension.

    Daca modelul nu e gasit (inca neantrenat), cade elegant pe numarare
    pur geometrica, fara sa crape.
    """

    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Pull-up Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        cale_model = os.path.join(current_dir, 'data/model_pullup.h5')
        cale_clase = os.path.join(current_dir, 'data/clase_pullup.npy')
        cale_scaler = os.path.join(current_dir, 'data/scaler_pullup.pkl')

        self.model_loaded = False
        if os.path.exists(cale_model) and os.path.exists(cale_clase) and os.path.exists(cale_scaler):
            self.model = load_model(cale_model)
            self.clase = np.load(cale_clase, allow_pickle=True)
            self.scaler = joblib.load(cale_scaler)
            self.model_loaded = True
        else:
            print(f"[Pullup] Model AI negasit la {cale_model} - folosesc doar euristici geometrice.")

        self.WINDOW_SIZE = 30
        self.buffer_cadre = []
        self.LUNGIME_VOTARE = 15
        self.istoric_predictii = []
        self.predictie_curenta = "Asteptare"

        self.total_repetitii = 0
        self.corecte = 0
        self.greseli = {
            'uncompleted': 0,
            'no_full_extension': 0,
        }

        self.stare_miscare = "HANG"
        self.verdict_repetitie = "Asteptare prima rep..."
        self.cooldown_frames = 0

        self.predictii_rep = []
        self.min_unghi_cot = 180.0
        self.chin_passed = False
        self.hang_max_cot = 0.0
        self.extensie_jos = 180.0
        self._last_model_vote = 'n/a'

        self.elbow_angle = 180.0
        self.hip_angle = 180.0
        self.knee_angle = 180.0
        self.chin_over_bar = False

        self.constant_scale = 0.0

        self.PULL_START = 130
        self.HANG_BACK = 143
        self.TOP_CONFIRM = 115
        self.UNCOMPLETED_ELBOW = 100
        self.FULL_EXT = 140
        self.CHIN_OVER_BAR_FACTOR = 0.35

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

        self.elbow_angle = unghi_cot
        self.hip_angle = unghi_sold
        self.knee_angle = unghi_genunchi

        p_inch_r = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        p_umar_r = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        bar_y = (p_inch.y + p_inch_r.y) / 2.0
        umar_y = (p_umar.y + p_umar_r.y) / 2.0
        torso_2d = math.hypot(p_umar.x - p_sold.x, p_umar.y - p_sold.y)
        if torso_2d < 0.001:
            torso_2d = 1.0
        self.chin_over_bar = (umar_y - bar_y) < self.CHIN_OVER_BAR_FACTOR * torso_2d

        s_curent = math.sqrt((p_umar.x - p_sold.x) ** 2 +
                             (p_umar.y - p_sold.y) ** 2 +
                             (p_umar.z - p_sold.z) ** 2)
        if self.stare_miscare == "HANG":
            self.constant_scale = max(self.constant_scale, s_curent)
        scale_to_use = self.constant_scale if self.constant_scale > 0.001 else s_curent

        norm_umar = self.normalizeaza_3d(p_umar, p_inch, scale_to_use)
        norm_cot = self.normalizeaza_3d(p_cot, p_inch, scale_to_use)
        norm_sold = self.normalizeaza_3d(p_sold, p_inch, scale_to_use)
        norm_gen = self.normalizeaza_3d(p_gen, p_inch, scale_to_use)
        norm_glez = self.normalizeaza_3d(p_glez, p_inch, scale_to_use)

        date_cadru_curent = [
            unghi_cot, unghi_umar, unghi_sold, unghi_genunchi,
            norm_umar[0], norm_umar[1], norm_umar[2],
            norm_cot[0], norm_cot[1], norm_cot[2],
            norm_sold[0], norm_sold[1], norm_sold[2],
            norm_gen[0], norm_gen[1], norm_gen[2],
            norm_glez[0], norm_glez[1], norm_glez[2]
        ]
        return date_cadru_curent

    def _prezice_fereastra(self):
        if not self.model_loaded or len(self.buffer_cadre) < self.WINDOW_SIZE:
            return
        buffer_plat = np.array(self.buffer_cadre).reshape(1, -1)
        scalat = self.scaler.transform(buffer_plat)
        input_model = scalat.reshape(1, self.WINDOW_SIZE, 19).astype('float32')
        pred = self.model(input_model, training=False).numpy()
        clasa = self.clase[np.argmax(pred)]

        self.istoric_predictii.append(clasa)
        if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
            self.istoric_predictii.pop(0)
        self.predictie_curenta = Counter(self.istoric_predictii).most_common(1)[0][0]

    def _reset_rep(self):
        self.predictii_rep = []
        self.min_unghi_cot = self.elbow_angle
        self.chin_passed = self.chin_over_bar

    def _evalueaza_rep(self):
        if self.predictii_rep:
            self._last_model_vote = Counter(self.predictii_rep).most_common(1)[0][0]
        else:
            self._last_model_vote = 'n/a'
        verdict = self._last_model_vote if self._last_model_vote in self.greseli else 'perfect'

        if (not self.chin_passed) or self.min_unghi_cot > self.UNCOMPLETED_ELBOW:
            verdict = 'uncompleted'
        elif self.extensie_jos < self.FULL_EXT:
            verdict = 'no_full_extension'

        return verdict

    def checkRep(self, date_cadru_curent):
        if self.model_loaded:
            self.buffer_cadre.append(date_cadru_curent)
            if len(self.buffer_cadre) > self.WINDOW_SIZE:
                self.buffer_cadre.pop(0)
            if self.stare_miscare == "PULL" and len(self.buffer_cadre) == self.WINDOW_SIZE:
                self._prezice_fereastra()

        cot = self.elbow_angle

        if self.stare_miscare == "HANG":
            self.hang_max_cot = max(self.hang_max_cot, cot)
            if cot < self.PULL_START:
                self.stare_miscare = "PULL"
                self.extensie_jos = self.hang_max_cot
                self._reset_rep()

        elif self.stare_miscare == "PULL":
            self.predictii_rep.append(self.predictie_curenta)
            self.min_unghi_cot = min(self.min_unghi_cot, cot)
            if self.chin_over_bar:
                self.chin_passed = True

            if cot > self.HANG_BACK:
                self.stare_miscare = "HANG"
                self.hang_max_cot = cot

                if self.min_unghi_cot > self.TOP_CONFIRM:
                    return

                self.total_repetitii += 1
                self.counter = self.total_repetitii
                self.verdict_repetitie = self._evalueaza_rep()

                if self.verdict_repetitie == 'perfect':
                    self.corecte += 1
                elif self.verdict_repetitie in self.greseli:
                    self.greseli[self.verdict_repetitie] += 1

                print(f"Pull-up {self.total_repetitii}: {self.verdict_repetitie.upper()} "
                      f"| min_cot={self.min_unghi_cot:.0f} ext_jos={self.extensie_jos:.0f} "
                      f"chin={self.chin_passed} model={self._last_model_vote}")
                print(f"Total: {self.total_repetitii} | Corecte: {self.corecte}")

    def displayInfo(self, date_cadru_curent, image):
        cv2.putText(image, f"Corecte: {self.corecte}/{self.total_repetitii}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        culoare = (0, 255, 0) if self.verdict_repetitie == 'perfect' else (0, 0, 255)
        cv2.putText(image, f"Verdict: {str(self.verdict_repetitie).upper()}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, culoare, 2)

        if self.model_loaded:
            cv2.putText(image, f"Live AI: {str(self.predictie_curenta).upper()}", (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.putText(image, f"Cot: {int(self.elbow_angle)}  Stare: {self.stare_miscare}", (30, 165),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        # 1=pushup, 2=pullup, 3=squat
        strength_ids = {1, 2, 3}
        total_score = 0
        for challenge in challenges_results:
            if challenge.challenge_id in strength_ids:
                total_score += challenge.result_value
        return AttributeUpdate(strength=int(total_score * 10))
