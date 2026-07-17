"""
Extractor SARITURA IN LUNGIME — ferestre ALINIATE pe saritura (ca analyzer-ul).

Procesează folderul de clipuri PERFECTE. Pentru fiecare clip ruleaza ACELASI FSM
ca LongJumpAnalyzer (STAND->LOAD->FLIGHT->LAND + cooldown) si emite cate o fereastra
per saritura (load -> zbor -> aterizare + cateva cadre dupa), reesantionata la 30 cadre.

Features/cadru (64): 14 landmark-uri x (x,y,z,visibility) normalizate hip-centric/torso
+ 8 unghiuri (genunchi L/R, sold L/R, cot L/R, brat L/R).

INCLUDE BRATELE (coate + incheieturi) — esential pt clasa no_arm_swing.

Greselile (fall_landing / no_arm_swing) se fabrica sintetic in rebuild_long_jump.py.

Output: extractKP/date_sintetice/dataset_jump.csv
"""

import os
import math

import cv2
import numpy as np
import pandas as pd
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# ---- spec canonica (TREBUIE identica in analyzer si train) ----
LM_NAMES = [
    'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
    'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
    'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
    'left_foot_index', 'right_foot_index',
]
ANGLE_NAMES = [
    'unghi_genunchi_l', 'unghi_genunchi_r', 'unghi_sold_l', 'unghi_sold_r',
    'unghi_cot_l', 'unghi_cot_r', 'unghi_brat_l', 'unghi_brat_r',
]
WINDOW_SIZE = 30

# ---- praguri FSM (TREBUIE identice cu LongJumpAnalyzer) ----
LOAD_KNEE = 150
AIR_MARGIN = 0.04
MIN_FLIGHT = 3
PRE_CONTEXT = 5      # cadre pastrate inainte de LOAD
COOLDOWN = 10        # cadre capturate dupa aterizare (pt a prinde caderea)

DATASET_DIR = r"C:\Users\rares\Desktop\long_jump_dataset\perfect"
OUT_CSV = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\date_sintetice\dataset_jump.csv"


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    rad = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    ang = np.abs(rad * 180.0 / np.pi)
    return 360 - ang if ang > 180.0 else ang


def L(landmarks, name):
    return landmarks[getattr(mp_pose.PoseLandmark, name.upper()).value]


def frame_features(landmarks):
    """Returneaza vectorul de 64 features pt un cadru (normalizat hip-centric/torso)."""
    pts = {n: L(landmarks, n) for n in LM_NAMES}

    mhx = (pts['left_hip'].x + pts['right_hip'].x) / 2.0
    mhy = (pts['left_hip'].y + pts['right_hip'].y) / 2.0
    mhz = (pts['left_hip'].z + pts['right_hip'].z) / 2.0
    msx = (pts['left_shoulder'].x + pts['right_shoulder'].x) / 2.0
    msy = (pts['left_shoulder'].y + pts['right_shoulder'].y) / 2.0
    msz = (pts['left_shoulder'].z + pts['right_shoulder'].z) / 2.0
    scale = math.sqrt((msx - mhx) ** 2 + (msy - mhy) ** 2 + (msz - mhz) ** 2)
    if scale < 0.001:
        scale = 1.0

    feats = []
    for n in LM_NAMES:
        lm = pts[n]
        feats.extend([(lm.x - mhx) / scale, (lm.y - mhy) / scale, (lm.z - mhz) / scale, lm.visibility])

    def g(n):
        return [pts[n].x, pts[n].y]

    feats.extend([
        calculate_angle(g('left_hip'), g('left_knee'), g('left_ankle')),
        calculate_angle(g('right_hip'), g('right_knee'), g('right_ankle')),
        calculate_angle(g('left_shoulder'), g('left_hip'), g('left_knee')),
        calculate_angle(g('right_shoulder'), g('right_hip'), g('right_knee')),
        calculate_angle(g('left_shoulder'), g('left_elbow'), g('left_wrist')),
        calculate_angle(g('right_shoulder'), g('right_elbow'), g('right_wrist')),
        calculate_angle(g('left_hip'), g('left_shoulder'), g('left_elbow')),
        calculate_angle(g('right_hip'), g('right_shoulder'), g('right_elbow')),
    ])
    return feats


def raw_metrics(landmarks):
    """Marimi brute pt FSM (ca in analyzer)."""
    knee = (calculate_angle([L(landmarks, 'left_hip').x, L(landmarks, 'left_hip').y],
                            [L(landmarks, 'left_knee').x, L(landmarks, 'left_knee').y],
                            [L(landmarks, 'left_ankle').x, L(landmarks, 'left_ankle').y]) +
            calculate_angle([L(landmarks, 'right_hip').x, L(landmarks, 'right_hip').y],
                            [L(landmarks, 'right_knee').x, L(landmarks, 'right_knee').y],
                            [L(landmarks, 'right_ankle').x, L(landmarks, 'right_ankle').y])) / 2.0
    ankle_y = max(L(landmarks, 'left_ankle').y, L(landmarks, 'right_ankle').y)
    return knee, ankle_y


def resample(buf, n=WINDOW_SIZE):
    if len(buf) >= n:
        idx = np.linspace(0, len(buf) - 1, n).astype(int)
        return [buf[i] for i in idx]
    # prea putine cadre: repetam ultimul
    return buf + [buf[-1]] * (n - len(buf))


def proceseaza_clip(cale, nume, win_id):
    cap = cv2.VideoCapture(cale)
    ferestre = []

    pre = []                 # ring de cadre inainte de LOAD
    jump_buf = None          # buffer activ al sariturii
    stare = "STAND"
    ground_y = 0.0
    flight = 0
    cooldown = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        res = pose.process(image)
        if not res.pose_landmarks:
            continue
        lm = res.pose_landmarks.landmark
        feats = frame_features(lm)
        knee, ankle_y = raw_metrics(lm)

        if jump_buf is not None:
            jump_buf.append(feats)
        else:
            pre.append(feats)
            pre = pre[-PRE_CONTEXT:]

        if stare == "STAND":
            ground_y = max(ground_y, ankle_y)
            if knee < LOAD_KNEE:
                stare = "LOAD"
                flight = 0
                jump_buf = list(pre)   # pornim cu contextul pre-LOAD
        elif stare == "LOAD":
            if ankle_y < ground_y - AIR_MARGIN:
                stare = "FLIGHT"
        elif stare == "FLIGHT":
            flight += 1
            if ankle_y >= ground_y - AIR_MARGIN and flight >= MIN_FLIGHT:
                stare = "LAND"
                cooldown = COOLDOWN
        elif stare == "LAND":
            cooldown -= 1
            if cooldown <= 0:
                ferestre.append([nume, 'perfect', win_id] + sum(resample(jump_buf), []))
                win_id += 1
                jump_buf = None
                pre = []
                stare = "STAND"

    cap.release()
    return ferestre, win_id


if __name__ == "__main__":
    if not os.path.exists(DATASET_DIR):
        print(f"Nu gasesc folderul: {DATASET_DIR}")
        raise SystemExit

    clipuri = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
    print(f"Procesez {len(clipuri)} clipuri perfecte...")

    toate = []
    win_id = 0
    for nume in clipuri:
        fr, win_id = proceseaza_clip(os.path.join(DATASET_DIR, nume), nume, win_id)
        print(f"  {nume}: {len(fr)} sarituri")
        toate.extend(fr)

    columns = ['clip', 'clasa', 'window_id']
    for i in range(WINDOW_SIZE):
        for n in LM_NAMES:
            columns += [f'{n}_x_{i}', f'{n}_y_{i}', f'{n}_z_{i}', f'{n}_v_{i}']
        for a in ANGLE_NAMES:
            columns.append(f'{a}_{i}')

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df = pd.DataFrame(toate, columns=columns)
    df.to_csv(OUT_CSV, index=False)
    print(f"\nGata! {len(df)} ferestre (perfect, jump-aligned) salvate in {OUT_CSV}")
    print(f"Features/cadru: {(df.shape[1]-3)//WINDOW_SIZE} (trebuie 64)")
