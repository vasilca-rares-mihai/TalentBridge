import cv2
import mediapipe as mp
import numpy as np
import os
import csv

folder_principal = r"C:\Users\rares\Desktop\TBignore\videos\dataset\pushup"
nume_fisier_csv = "dataset_unghiuri_60frames.csv"

WINDOW_SIZE = 60
OVERLAP = 30


def calculeaza_unghi(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ANTET CSV: 4 unghiuri × 60 cadre
antet_csv = ['clip', 'clasa', 'window_id']

for i in range(WINDOW_SIZE):
    antet_csv.extend([
        f'unghi_cot_{i}',
        f'unghi_umar_{i}',
        f'unghi_sold_{i}',
        f'unghi_genunchi_{i}'
    ])

print("Încep extragerea unghiurilor pe ferestre de 60 cadre...")

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
            if not nume_clip.endswith('.mp4'):
                continue

            cale_completa = os.path.join(cale_folder_clasa, nume_clip)
            cap = cv2.VideoCapture(cale_completa)

            buffer_cadre = []
            window_id = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    p_umar = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    p_cot = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    p_inch = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                    p_sold = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    p_gen = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                    p_glez = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

                    umar = [p_umar.x, p_umar.y]
                    cot = [p_cot.x, p_cot.y]
                    inch = [p_inch.x, p_inch.y]
                    sold = [p_sold.x, p_sold.y]
                    gen = [p_gen.x, p_gen.y]
                    glez = [p_glez.x, p_glez.y]

                    unghi_cot = calculeaza_unghi(umar, cot, inch)
                    unghi_umar = calculeaza_unghi(sold, umar, cot)
                    unghi_sold = calculeaza_unghi(umar, sold, gen)
                    unghi_genunchi = calculeaza_unghi(sold, gen, glez)

                    date_cadru_curent = [
                        unghi_cot,
                        unghi_umar,
                        unghi_sold,
                        unghi_genunchi
                    ]

                    buffer_cadre.append(date_cadru_curent)

                    if len(buffer_cadre) == WINDOW_SIZE:
                        rand_final = [nume_clip, clasa_curenta, window_id]

                        for date_cadru in buffer_cadre:
                            rand_final.extend(date_cadru)

                        csv_writer.writerow(rand_final)

                        # overlap 30
                        buffer_cadre = buffer_cadre[OVERLAP:]
                        window_id += 1

            cap.release()

print(f"\nGata! Datasetul este salvat în: {nume_fisier_csv}")