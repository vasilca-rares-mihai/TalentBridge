import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import math

# Initializam MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)


# Functie pentru calculul unghiurilor (2D)
def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


# Numele coloanelor pentru un cadru
landmark_names = [
    'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip',
    'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
    'left_foot_index', 'right_foot_index'
]
angle_names = [
    'unghi_sold_l', 'unghi_genunchi_l', 'unghi_glezna_l',
    'unghi_sold_r', 'unghi_genunchi_r', 'unghi_glezna_r'
]

# Setam parametrii ferestrei
WINDOW_SIZE = 30
STRIDE = 5  # La cate cadre mutam fereastra pentru a genera un nou rand
video_path = 'jump1.mp4'  # <--- PUNE AICI NUMELE VIDEOCLIPULUI TAU

cap = cv2.VideoCapture(video_path)
buffer_cadre = []
toate_ferestrele = []
fereastra_id = 0

print("Incepem procesarea videoclipului...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # MediaPipe are nevoie de RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # 1. Extragem coordonatele (x, y, z, v) pentru punctele noastre
        points = {
            'left_shoulder': landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
            'right_shoulder': landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
            'left_hip': landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
            'right_hip': landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
            'left_knee': landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
            'right_knee': landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
            'left_ankle': landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value],
            'right_ankle': landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value],
            'left_foot_index': landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value],
            'right_foot_index': landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
        }

        # 2. Construim features pentru acest frame
        frame_features = []
        for name in landmark_names:
            lm = points[name]
            frame_features.extend([lm.x, lm.y, lm.z, lm.visibility])


        # 3. Calculam unghiurile
        def get_coords(name):
            return [points[name].x, points[name].y]


        # Unghiuri stanga
        u_sold_l = calculate_angle(get_coords('left_shoulder'), get_coords('left_hip'), get_coords('left_knee'))
        u_gen_l = calculate_angle(get_coords('left_hip'), get_coords('left_knee'), get_coords('left_ankle'))
        u_glez_l = calculate_angle(get_coords('left_knee'), get_coords('left_ankle'), get_coords('left_foot_index'))

        # Unghiuri dreapta
        u_sold_r = calculate_angle(get_coords('right_shoulder'), get_coords('right_hip'), get_coords('right_knee'))
        u_gen_r = calculate_angle(get_coords('right_hip'), get_coords('right_knee'), get_coords('right_ankle'))
        u_glez_r = calculate_angle(get_coords('right_knee'), get_coords('right_ankle'), get_coords('right_foot_index'))

        frame_features.extend([u_sold_l, u_gen_l, u_glez_l, u_sold_r, u_gen_r, u_glez_r])

        # Adaugam in buffer
        buffer_cadre.append(frame_features)

        # Cand avem suficiente cadre pentru un sliding window
        if len(buffer_cadre) == WINDOW_SIZE:
            # Flatten la toate caracteristicile din ferestra
            rand_csv = ['jump_clip', 'perfect', fereastra_id]
            for cadru in buffer_cadre:
                rand_csv.extend(cadru)

            toate_ferestrele.append(rand_csv)
            fereastra_id += 1

            # Aplicam Stride-ul (stergem primele 'STRIDE' cadre pentru a muta fereastra)
            buffer_cadre = buffer_cadre[STRIDE:]

cap.release()

# Construim Headerele (coloanele)
columns = ['clip', 'clasa', 'window_id']
for i in range(WINDOW_SIZE):
    for name in landmark_names:
        columns.extend([f'{name}_x_{i}', f'{name}_y_{i}', f'{name}_z_{i}', f'{name}_v_{i}'])
    for ang in angle_names:
        columns.append(f'{ang}_{i}')

# Generam CSV-ul
df = pd.DataFrame(toate_ferestrele, columns=columns)
df.to_csv('dataset_jump.csv', index=False)

print(f"Gata! S-au generat {len(df)} ferestre de cate 30 de cadre in 'dataset_jump.csv'")