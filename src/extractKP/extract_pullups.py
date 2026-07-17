"""
Extragere caracteristici (19 features / cadru) din clipuri REALE de pullup.
Acelasi format ca la pushup (extract_pushups_fixed.py) ca sa pastram aceeasi
arhitectura de model. Output: csv/dataset_pullups.csv

Structura folderelor asteptata:
    folder_principal/
        perfect/*.mp4
        uncompleted/*.mp4
        no_full_extension/*.mp4
        kipping/*.mp4
Daca ai DOAR clipuri corecte, pune-le toate intr-un folder 'perfect/' -
restul claselor le fabrica scriptul de augmentare (date_sintetice/pullups.py).
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import csv
import math

# Folder cu clipuri reale de pullup (modifica daca e nevoie)
folder_principal = r"C:\Users\rares\Desktop\TBignore\videos\dataset\pullup"
nume_fisier_csv = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\csv\dataset_pullups.csv"

WINDOW_SIZE = 30
OVERLAP = 15


def calculeaza_unghi(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def normalizeaza_3d(punct, referinta, scale_factor):
    return [(punct.x - referinta.x) / scale_factor,
            (punct.y - referinta.y) / scale_factor,
            (punct.z - referinta.z) / scale_factor]


mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ANTET CSV: 19 features * 30 cadre (identic ca la pushup)
antet_csv = ['clip', 'clasa', 'window_id']
for i in range(WINDOW_SIZE):
    antet_csv.extend([
        f'unghi_cot_{i}', f'unghi_umar_{i}', f'unghi_sold_{i}', f'unghi_genunchi_{i}',
        f'umar_X_{i}', f'umar_Y_{i}', f'umar_Z_{i}',
        f'cot_X_{i}', f'cot_Y_{i}', f'cot_Z_{i}',
        f'sold_X_{i}', f'sold_Y_{i}', f'sold_Z_{i}',
        f'gen_X_{i}', f'gen_Y_{i}', f'gen_Z_{i}',
        f'glez_X_{i}', f'glez_Y_{i}', f'glez_Z_{i}'
    ])

print("Incep extragerea caracteristicilor pentru PULLUP...")

if not os.path.exists(folder_principal):
    print(f"Folderul nu exista: {folder_principal}")
    print("Pune clipurile reale acolo (cel putin in subfolderul 'perfect/').")
    exit()

os.makedirs(os.path.dirname(nume_fisier_csv), exist_ok=True)

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
            if not nume_clip.lower().endswith(('.mp4', '.mov', '.avi')):
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

                    umar_2d = [p_umar.x, p_umar.y]
                    cot_2d = [p_cot.x, p_cot.y]
                    inch_2d = [p_inch.x, p_inch.y]
                    sold_2d = [p_sold.x, p_sold.y]
                    gen_2d = [p_gen.x, p_gen.y]
                    glez_2d = [p_glez.x, p_glez.y]

                    # unghi_cot = cotul (umar-cot-incheietura): semnalul principal de rep
                    unghi_cot = calculeaza_unghi(umar_2d, cot_2d, inch_2d)
                    # unghi_umar = deschiderea umarului (sold-umar-cot)
                    unghi_umar = calculeaza_unghi(sold_2d, umar_2d, cot_2d)
                    # unghi_sold = flexia soldului (umar-sold-genunchi): pt kipping
                    unghi_sold = calculeaza_unghi(umar_2d, sold_2d, gen_2d)
                    # unghi_genunchi = (sold-genunchi-glezna): pt kipping (lovire picioare)
                    unghi_genunchi = calculeaza_unghi(sold_2d, gen_2d, glez_2d)

                    # Scala = anvergura torso (umar-sold): stabila indiferent de
                    # pozitia bratelor. Referinta (origine) = INCHEIETURA (bara).
                    s_curent = math.sqrt(
                        (p_umar.x - p_sold.x) ** 2 +
                        (p_umar.y - p_sold.y) ** 2 +
                        (p_umar.z - p_sold.z) ** 2
                    )
                    if s_curent < 0.001:
                        s_curent = 1.0

                    # Normalizare relativ la incheietura (wrist-centric):
                    # nu includem incheietura in features (ar fi mereu 0,0,0),
                    # ci urmarim umar/cot/sold/genunchi/glezna fata de bara.
                    norm_umar = normalizeaza_3d(p_umar, p_inch, s_curent)
                    norm_cot = normalizeaza_3d(p_cot, p_inch, s_curent)
                    norm_sold = normalizeaza_3d(p_sold, p_inch, s_curent)
                    norm_gen = normalizeaza_3d(p_gen, p_inch, s_curent)
                    norm_glez = normalizeaza_3d(p_glez, p_inch, s_curent)

                    date_cadru_curent = [
                        unghi_cot, unghi_umar, unghi_sold, unghi_genunchi,
                        norm_umar[0], norm_umar[1], norm_umar[2],
                        norm_cot[0], norm_cot[1], norm_cot[2],
                        norm_sold[0], norm_sold[1], norm_sold[2],
                        norm_gen[0], norm_gen[1], norm_gen[2],
                        norm_glez[0], norm_glez[1], norm_glez[2]
                    ]

                    buffer_cadre.append(date_cadru_curent)

                    if len(buffer_cadre) == WINDOW_SIZE:
                        rand_final = [nume_clip, clasa_curenta, window_id]
                        for date_cadru in buffer_cadre:
                            rand_final.extend(date_cadru)

                        csv_writer.writerow(rand_final)

                        buffer_cadre = buffer_cadre[OVERLAP:]
                        window_id += 1

            cap.release()

print(f"Gata! CSV salvat la {nume_fisier_csv}")
