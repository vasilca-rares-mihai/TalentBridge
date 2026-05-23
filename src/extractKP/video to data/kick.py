import cv2
import mediapipe as mp
import numpy as np
import os
import csv
import math
from ultralytics import YOLO

# Configurari
folder_principal = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\videos\dataset\duble"
nume_fisier_csv = "dataset_duble_real.csv"
WINDOW_SIZE = 30
OVERLAP = 15
PAS = WINDOW_SIZE - OVERLAP  # Cate cadre stergem ca sa ramana doar overlap-ul (15)

# Modele AI
model_yolo = YOLO('yolov8s.pt')
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Generare Antet CSV (12 caracteristici x 30 cadre = 360 coloane + cele 3 initiale)
antet_csv = ['clip', 'clasa', 'window_id']
nume_features = ['minge_x', 'minge_y', 'gen_st_x', 'gen_st_y', 'glez_st_x', 'glez_st_y',
                 'gen_dr_x', 'gen_dr_y', 'glez_dr_x', 'glez_dr_y', 'dist_st', 'dist_dr']

for i in range(WINDOW_SIZE):
    for feat in nume_features:
        antet_csv.append(f"{feat}_{i}")

print("Incepem extragerea biomecanica hibrida (YOLO+MP) pentru DUBLE...")

with open(nume_fisier_csv, mode='w', newline='', encoding='utf-8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(antet_csv)

    for nume_folder in os.listdir(folder_principal):
        cale_folder_clasa = os.path.join(folder_principal, nume_folder)
        if not os.path.isdir(cale_folder_clasa):
            continue

        clasa_curenta = nume_folder.replace('.', '')
        print(f"---> Procesez clasa: {clasa_curenta}")

        for nume_clip in os.listdir(cale_folder_clasa):
            if not nume_clip.endswith(('.mp4', '.mov', '.avi')):
                continue

            cale_completa = os.path.join(cale_folder_clasa, nume_clip)
            cap = cv2.VideoCapture(cale_completa)
            buffer_cadre = []
            window_id = 0

            # Valori de rezerva in caz ca modelul nu detecteaza in primul cadru
            ultima_minge = (0.5, 0.5)
            coordonate_om = {'gen_st': (0, 0), 'glez_st': (0, 0), 'gen_dr': (0, 0), 'glez_dr': (0, 0)}

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                h, w, _ = frame.shape
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 1. Extragere Body (MediaPipe)
                results = pose.process(image_rgb)
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    # Coordonatele in MP sunt deja normalizate (0.0 - 1.0)
                    coordonate_om['gen_st'] = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                               landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y)
                    coordonate_om['glez_st'] = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                                landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y)
                    coordonate_om['gen_dr'] = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                               landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y)
                    coordonate_om['glez_dr'] = (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                                landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y)

                # 2. Extragere Minge (YOLO)
                yolo_results = model_yolo.predict(source=frame, classes=[32], conf=0.15, verbose=False)
                minge_curenta = ultima_minge

                if len(yolo_results[0].boxes) > 0:
                    box = yolo_results[0].boxes.xyxy[0]
                    # Normalizam coordonatele mingii la fel ca la MediaPipe (impartim la latime si inaltime)
                    x_centru = float((box[0] + box[2]) / 2) / w
                    y_centru = float((box[1] + box[3]) / 2) / h
                    minge_curenta = (x_centru, y_centru)
                    ultima_minge = minge_curenta  # Actualizam memoria

                # 3. Calculam distanta (Euclidiana) intre minge si glezne
                dist_st = math.sqrt((minge_curenta[0] - coordonate_om['glez_st'][0]) ** 2 +
                                    (minge_curenta[1] - coordonate_om['glez_st'][1]) ** 2)
                dist_dr = math.sqrt((minge_curenta[0] - coordonate_om['glez_dr'][0]) ** 2 +
                                    (minge_curenta[1] - coordonate_om['glez_dr'][1]) ** 2)

                # 4. Formare array de caracteristici pentru cadrul curent (12 elemente)
                date_cadru_curent = [
                    minge_curenta[0], minge_curenta[1],
                    coordonate_om['gen_st'][0], coordonate_om['gen_st'][1],
                    coordonate_om['glez_st'][0], coordonate_om['glez_st'][1],
                    coordonate_om['gen_dr'][0], coordonate_om['gen_dr'][1],
                    coordonate_om['glez_dr'][0], coordonate_om['glez_dr'][1],
                    dist_st, dist_dr
                ]

                buffer_cadre.append(date_cadru_curent)

                # 5. Salvare in CSV cu logica ta de Sliding Window
                if len(buffer_cadre) == WINDOW_SIZE:
                    rand_final = [nume_clip, clasa_curenta, window_id]
                    for date_cadru in buffer_cadre:
                        rand_final.extend(date_cadru)

                    csv_writer.writerow(rand_final)

                    # Daca WINDOW e 30 si OVERLAP e 15, pastram ultimele 15
                    buffer_cadre = buffer_cadre[PAS:]
                    window_id += 1

            cap.release()

print(f"\nGata! Datele pentru duble au fost salvate in {nume_fisier_csv}")