import cv2
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from collections import Counter
from typing import List
import os
import math
from ultralytics import YOLO

from .base import VideoAnalyzer, mp_pose
from ..utils.schemas import AttributeUpdate, ChallengeResult


class DubleAnalyzer(VideoAnalyzer):
    def __init__(self, video_path, output_path=None):
        super().__init__(video_path, window_name="Duble Analysis", output_path=output_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, 'data')

        self.model = load_model(os.path.join(data_dir, 'model_duble.h5'))
        self.clase = np.load(os.path.join(data_dir, 'clase_duble.npy'), allow_pickle=True)
        self.scaler = joblib.load(os.path.join(data_dir, 'scaler_duble.pkl'))
        # YOLO va căuta automat yolov8s.pt în folderul curent de lucru
        # sau poți forța calea:
        self.yolo = YOLO(os.path.join(data_dir, 'yolov8s.pt'))

        self.WINDOW_SIZE = 15
        self.buffer_cadre = []

        # Variabile pentru contorizare
        self.total_duble = 0
        self.st_count = 0
        self.dr_count = 0
        self.wrong_count = 0

        self.istoric_predictii = []
        self.LUNGIME_VOTARE = 5
        self.ultima_minge = (0.5, 0.5)  # Memorie pentru YOLO

    def extract_features(self, frame, landmarks):
        h, w, _ = frame.shape

        # 1. Extragere Body (MediaPipe)
        gen_st = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y)
        glez_st = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y)
        gen_dr = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                  landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y)
        glez_dr = (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y)

        # 2. Extragere Minge (YOLO)
        results = self.yolo.predict(source=frame, classes=[32], conf=0.15, verbose=False)
        minge = self.ultima_minge
        if len(results[0].boxes) > 0:
            box = results[0].boxes.xyxy[0]
            minge = (float((box[0] + box[2]) / 2) / w, float((box[1] + box[3]) / 2) / h)
            self.ultima_minge = minge

        # 3. Calcul Distante
        dist_st = math.sqrt((minge[0] - glez_st[0]) ** 2 + (minge[1] - glez_st[1]) ** 2)
        dist_dr = math.sqrt((minge[0] - glez_dr[0]) ** 2 + (minge[1] - glez_dr[1]) ** 2)

        return [minge[0], minge[1], gen_st[0], gen_st[1], glez_st[0], glez_st[1],
                gen_dr[0], gen_dr[1], glez_dr[0], glez_dr[1], dist_st, dist_dr]

    def process_frame(self, frame, landmarks):
        date_cadru = self.extract_features(frame, landmarks)
        self.buffer_cadre.append(date_cadru)

        if len(self.buffer_cadre) == self.WINDOW_SIZE:
            # Predictie
            fereastra = np.array(self.buffer_cadre).reshape(1, self.WINDOW_SIZE, 12)
            fereastra_scalata = self.scaler.transform(fereastra.reshape(1, -1)).reshape(1, self.WINDOW_SIZE, 12)

            probs = self.model.predict(fereastra_scalata, verbose=0)
            clasa = self.clase[np.argmax(probs)]

            self.istoric_predictii.append(clasa)
            if len(self.istoric_predictii) > self.LUNGIME_VOTARE:
                self.istoric_predictii.pop(0)

            # Vot majoritar
            predictie_finala = Counter(self.istoric_predictii).most_common(1)[0][0]

            # Logica de contorizare (evitam dublarea numărătorii folosind un buffer sau un flag)
            if predictie_finala == 'left':
                self.st_count += 1
            elif predictie_finala == 'right':
                self.dr_count += 1
            else:
                self.wrong_count += 1

            self.buffer_cadre.pop(0)  # Sliding window
            return predictie_finala
        return "Asteptare"

    def displayInfo(self, image, predictie):
        cv2.putText(image, f"Stangul: {self.st_count} | Dreptul: {self.dr_count}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(image, f"Status: {predictie.upper()}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)