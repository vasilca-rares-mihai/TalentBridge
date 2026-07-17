import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from collections import Counter
from typing import List
import os
import math
from ultralytics import YOLO

from shared.models.sql_models import Attribute
from shared.schemas.schemas import AttributeUpdate, ChallengeResult
from .base import VideoAnalyzer, mp_pose


class DubleAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Duble Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, 'data')

        cale_model = os.path.join(data_dir, 'model_duble.h5')
        cale_clase = os.path.join(data_dir, 'clase_duble.npy')
        cale_scaler = os.path.join(data_dir, 'scaler_duble.pkl')
        cale_yolo = os.path.join(data_dir, 'yolov8s.pt')

        if not os.path.exists(cale_model):
            print(f"[DEBUG-INIT] EROARE: Nu gasesc modelul AI la: {cale_model}")

        self.model = load_model(cale_model)
        self.clase = np.load(cale_clase, allow_pickle=True)
        self.scaler = joblib.load(cale_scaler)
        self.yolo = YOLO(cale_yolo)

        self.WINDOW_SIZE = 15
        self.buffer_cadre = []

        self.LUNGIME_VOTARE = 3
        self.istoric_predictii = []
        self.predictie_curenta = "Asteptare"

        self.total_duble = 0
        self.st_count = 0
        self.dr_count = 0
        self.wrong_count = 0
        self.ultima_minge = (0.5, 0.5)
        self.istoric_minge_y = []
        self.cadre_de_la_ultima_dubla = 100

        self.stare_st = "NEUTRAL"
        self.stare_dr = "NEUTRAL"

    def extractLandmarks(self, landmarks):
        gen_st = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y)
        glez_st = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y)
        gen_dr = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y)
        glez_dr = (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y)

        return [gen_st, glez_st, gen_dr, glez_dr]

    def displayInfo(self, date_cadru_curent, image):
        h, w, _ = image.shape
        results = self.yolo.predict(source=image, classes=[32], conf=0.05, verbose=False)

        if len(results[0].boxes) > 0:
            box = results[0].boxes.xyxy[0]

            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

            centru_x = int((x1 + x2) / 2)
            centru_y = int((y1 + y2) / 2)

            cv2.circle(image, (centru_x, centru_y), 5, (255, 0, 0), -1)
            self.ultima_minge = (float(centru_x) / w, float(centru_y) / h)

        cv2.putText(image, f"Stangul: {self.st_count} | Dreptul: {self.dr_count}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(image, f"AI: {self.predictie_curenta.upper()} | Invalide: {self.wrong_count}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    def checkRep(self, date_cadru_curent):
        gen_st, glez_st, gen_dr, glez_dr = date_cadru_curent
        minge = self.ultima_minge

        dist_st = math.sqrt((minge[0] - glez_st[0]) ** 2 + (minge[1] - glez_st[1]) ** 2)
        dist_dr = math.sqrt((minge[0] - glez_dr[0]) ** 2 + (minge[1] - glez_dr[1]) ** 2)

        vector_final = [
            minge[0], minge[1], gen_st[0], gen_st[1], glez_st[0], glez_st[1],
            gen_dr[0], gen_dr[1], glez_dr[0], glez_dr[1], dist_st, dist_dr
        ]

        self.buffer_cadre.append(vector_final)

        if len(self.buffer_cadre) == self.WINDOW_SIZE:
            fereastra = np.array(self.buffer_cadre).reshape(1, self.WINDOW_SIZE, 12)
            fereastra_scalata = self.scaler.transform(fereastra.reshape(1, -1)).reshape(1, self.WINDOW_SIZE, 12)

            probs = self.model.predict(fereastra_scalata, verbose=0)
            clasa_ghicita = self.clase[np.argmax(probs)]

            self.istoric_predictii.append(clasa_ghicita)
            if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
                self.istoric_predictii.pop(0)

            voturi = Counter(self.istoric_predictii)
            vechea_predictie = self.predictie_curenta
            self.predictie_curenta = voturi.most_common(1)[0][0]

            if vechea_predictie != self.predictie_curenta:
                print(f"[DEBUG-AI] Predictia s-a schimbat in: '{self.predictie_curenta}' (Voturi: {voturi})")

            if not hasattr(self, 'stare_minge'):
                self.stare_minge = "FALLING"
                self.extreme_y = minge[1]

            y_curr = minge[1]
            bounced = False
            self.cadre_de_la_ultima_dubla += 1

            if self.stare_minge == "FALLING":
                if y_curr > self.extreme_y:
                    self.extreme_y = y_curr
                elif y_curr < self.extreme_y - 0.004:
                    self.stare_minge = "RISING"
                    self.extreme_y = y_curr
                    bounced = True
            elif self.stare_minge == "RISING":
                if y_curr < self.extreme_y:
                    self.extreme_y = y_curr
                elif y_curr > self.extreme_y + 0.004:
                    self.stare_minge = "FALLING"
                    self.extreme_y = y_curr

            if bounced and self.cadre_de_la_ultima_dubla > 8:
                self.cadre_de_la_ultima_dubla = 0
                verdict = self.predictie_curenta
                if verdict == 'left':
                    self.st_count += 1
                    print(f"[DEBUG-BOUNCE] DUBLE STANGUL ++ (Total: {self.st_count}) "
                          f"| CNN={verdict} dist_st={dist_st:.3f} dist_dr={dist_dr:.3f}")
                elif verdict == 'right':
                    self.dr_count += 1
                    print(f"[DEBUG-BOUNCE] DUBLE DREPTUL ++ (Total: {self.dr_count}) "
                          f"| CNN={verdict} dist_st={dist_st:.3f} dist_dr={dist_dr:.3f}")
                else:
                    self.wrong_count += 1
                    print(f"[DEBUG-BOUNCE] ATINGERE INVALIDA (wrong={self.wrong_count}) "
                          f"| CNN={verdict} dist_st={dist_st:.3f} dist_dr={dist_dr:.3f}")

            self.buffer_cadre.pop(0)

        self.total_duble = self.st_count + self.dr_count
        self.counter = self.total_duble

    def calculateAttribute(self, challenges_results: List[ChallengeResult]):
        ball_control_ids = {4, 5}
        total_score = 0

        for challenge in challenges_results:
            if challenge.challenge_id in ball_control_ids:
                total_score += challenge.result_value

        return AttributeUpdate(ball_control=int(total_score * 10))