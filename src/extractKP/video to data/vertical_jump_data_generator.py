import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split

mp_pose = mp.solutions.pose

kp_mapping = [
    mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_ELBOW,
    mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP,
    mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE,
    mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.RIGHT_ANKLE,
    mp_pose.PoseLandmark.LEFT_HEEL, mp_pose.PoseLandmark.RIGHT_HEEL,
    mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
]

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def get_columns():
    cols = ['clip', 'clasa', 'window_id']
    
    # EXACTLY the same order as train_vertical_jump.py and vertical_jump.py
    angle_names = ['angle_knee_l', 'angle_knee_r', 'angle_hip_l', 'angle_hip_r', 
                   'angle_ankle_l', 'angle_ankle_r', 'angle_trunk', 'angle_arm_l', 'angle_arm_r']
                   
    for f in range(30):
        for kp in kp_mapping:
            cols.extend([f"{kp.name.lower()}_f{f}_x", f"{kp.name.lower()}_f{f}_y"])
        for ang in angle_names:
            cols.append(f"{ang}_f{f}")
            
    cols.extend(['jumps_in_window', 'horiz_disp', 'max_height_m', 'takeoff_velocity', 'hang_time_sec'])
    return cols

def extract_features(landmarks, ref_x, ref_y, ref_s):
    p = {}
    for kp in kp_mapping:
        norm_x = (landmarks[kp.value].x - ref_x) / ref_s + 0.50
        norm_y = (landmarks[kp.value].y - ref_y) / ref_s + 0.55
        p[kp.name.lower()] = [norm_x, norm_y]

    wrist_l = [(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x - ref_x) / ref_s + 0.50,
               (landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y - ref_y) / ref_s + 0.55]
    wrist_r = [(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x - ref_x) / ref_s + 0.50,
               (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y - ref_y) / ref_s + 0.55]

    u_gen_s = calculate_angle(p["left_hip"], p["left_knee"], p["left_ankle"])
    u_gen_d = calculate_angle(p["right_hip"], p["right_knee"], p["right_ankle"])
    u_sold_s = calculate_angle(p["left_shoulder"], p["left_hip"], p["left_knee"])
    u_sold_d = calculate_angle(p["right_shoulder"], p["right_hip"], p["right_knee"])
    u_gle_s = calculate_angle(p["left_knee"], p["left_ankle"], p["left_foot_index"])
    u_gle_d = calculate_angle(p["right_knee"], p["right_ankle"], p["right_foot_index"])

    mid_sh = [(p["left_shoulder"][0] + p["right_shoulder"][0]) / 2,
              (p["left_shoulder"][1] + p["right_shoulder"][1]) / 2]
    mid_p_hip = [(p["left_hip"][0] + p["right_hip"][0]) / 2, (p["left_hip"][1] + p["right_hip"][1]) / 2]
    vert = [mid_p_hip[0], mid_p_hip[1] + 0.10]
    u_trunchi = calculate_angle(mid_sh, mid_p_hip, vert)

    u_brat_s = calculate_angle(p["left_shoulder"], p["left_elbow"], wrist_l)
    u_brat_d = calculate_angle(p["right_shoulder"], p["right_elbow"], wrist_r)

    f = []
    for kp in kp_mapping:
        f.extend([p[kp.name.lower()][0], p[kp.name.lower()][1]])
    f.extend([u_gen_s, u_gen_d, u_sold_s, u_sold_d, u_gle_s, u_gle_d, u_trunchi, u_brat_s, u_brat_d])
    return f

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        ref_x, ref_y, ref_s = None, None, None
        stare = "STAND"
        buffer_cadre = []
        ferestre_zbor = []
        repetitii_gasite = []
        cadre_in_aer = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            
            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                mid_hip_x = (lm[mp_pose.PoseLandmark.LEFT_HIP.value].x + lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2
                mid_hip_y = (lm[mp_pose.PoseLandmark.LEFT_HIP.value].y + lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
                mid_sh_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
                
                if ref_x is None or (stare == "STAND" and mid_hip_y < ref_y):
                    ref_x = mid_hip_x
                    ref_y = mid_hip_y
                    s_val = abs(mid_hip_y - mid_sh_y)
                    ref_s = s_val if s_val > 0.05 else 0.20
                    
                feat = extract_features(lm, ref_x, ref_y, ref_s)
                buffer_cadre.append(feat)
                if len(buffer_cadre) > 30:
                    buffer_cadre.pop(0)
                
                y_curent_sold = (feat[9] + feat[11]) / 2
                
                if y_curent_sold > 0.65 and stare in ["STAND", "LAND"]:
                    stare = "SQUAT"
                    cadre_in_aer = 0
                
                if stare == "SQUAT" and y_curent_sold < 0.50:
                    # Prevenim phantom jumps: cel putin un genunchi trebuie intins (saritura reala)
                    if feat[28] > 140 or feat[29] > 140:
                        stare = "FLIGHT"
                    
                if stare == "FLIGHT":
                    cadre_in_aer += 1
                    if len(buffer_cadre) == 30:
                        ferestre_zbor.append(list(buffer_cadre))
                        
                    if y_curent_sold > 0.50 and cadre_in_aer > 4:
                        stare = "LAND"
                        if len(ferestre_zbor) > 0:
                            # Luam doar ULTIMA fereastra, care contine aterizarea completa!
                            # Asta e singura fereastra in care deplasarea e evidenta complet.
                            repetitii_gasite.append(ferestre_zbor[-1])
                        ferestre_zbor = []
                        
                if stare == "LAND" and y_curent_sold < 0.60:
                    stare = "STAND"
                    
        cap.release()
        return repetitii_gasite

def flatten_repetition(rep_30_frames, base_clip_name, clasa):
    flat_row = [f"{base_clip_name}", clasa, 0] # window_id este mereu 0 aici
    
    # Pentru FIECARE CADRU, punem TOATE cele 37 de feature-uri IN ORDINE
    for f in range(30):
        # 1. Toate landmark-urile (indicii 0-27)
        for i in range(28):
            flat_row.append(rep_30_frames[f][i])
        # 2. Toate unghiurile (indicii 28-36)
        for i in range(28, 37):
            flat_row.append(rep_30_frames[f][i])
            
    max_inaltime = 0.0
    cadre_in_aer = 0
    for cadru in rep_30_frames:
        y_sold = (cadru[9] + cadru[11]) / 2  # left_hip_y, right_hip_y
        inaltime = max(0.0, float(0.55 - y_sold) * 1.5)
        if inaltime > max_inaltime:
            max_inaltime = inaltime
        # Daca genunchiul e intins (FLIGHT) -> numaram cadre
        if (cadru[28] + cadru[29])/2 > 160:
            cadre_in_aer += 1
            
    hang_time = cadre_in_aer / 30.0 if cadre_in_aer > 0 else 0.20
    takeoff_vel = max_inaltime * 4.5
    
    c_first = rep_30_frames[0]
    c_last = rep_30_frames[-1]
    x_first = (c_first[8] + c_first[10]) / 2
    x_last = (c_last[8] + c_last[10]) / 2
    horiz_disp = abs(x_last - x_first)
    
    flat_row.extend([1, horiz_disp, max_inaltime, takeoff_vel, hang_time])
    return flat_row

def main():
    base_dir = r"C:\Users\rares\Desktop\vertical_jump_dataset"
    if not os.path.exists(base_dir):
        print(f"Te rog creaza folderul {base_dir} cu folderele .perfect, .incomplete_extension, .unstable_landing")
        return
    print("Incep extragerea din videoclipuri reale...")
    
    foldere_clase = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not foldere_clase:
        print(f"ATENTIE: Nu am gasit niciun folder in {base_dir}")
        return

    clase_reale = [f.replace('.', '') for f in foldere_clase]
    date_baza = {c: [] for c in clase_reale}

    for folder in foldere_clase:
        folder_clasa = os.path.join(base_dir, folder)
        clasa_finala = folder.replace('.', '')
            
        for nume_fisier in os.listdir(folder_clasa):
            if nume_fisier.endswith(".mp4") or nume_fisier.endswith(".mov"):
                cale = os.path.join(folder_clasa, nume_fisier)
                repetitii = process_video(cale)
                for r in repetitii:
                    date_baza[clasa_finala].append((r, nume_fisier))
                print(f"  Extras {len(repetitii)} sarituri din {nume_fisier} [{folder} -> {clasa_finala}]")
                
    dataset_rows = []
    
    for clasa in clase_reale:
        if not date_baza[clasa]:
            print(f"ATENTIE: Nu am gasit nicio saritura in folderul {clasa}!")
            continue

        print(f"Generam 1000 de date curate (fara zgomot) pentru clasa: {clasa.upper()}...")
        for i in range(1000):
            idx = np.random.randint(0, len(date_baza[clasa]))
            rep_originala, clip_name = date_baza[clasa][idx]
            
            rep_curata = []
            for f_idx in range(30):
                cadru_nou = []
                
                # Coordonate perfect curate
                for coord_idx, val in enumerate(rep_originala[f_idx][:28]):
                    cadru_nou.append(val)
                    
                # Unghiuri perfect curate
                for angle_idx, val in enumerate(rep_originala[f_idx][28:37]):
                    cadru_nou.append(val)
                    
                rep_curata.append(cadru_nou)
                
            rand_plat = flatten_repetition(rep_curata, f"{clip_name}_aug_{i}", clasa)
            dataset_rows.append(rand_plat)
            
    if len(dataset_rows) == 0:
        print("Nu s-au generat date. Verifica folderele.")
        return
        
    df = pd.DataFrame(dataset_rows, columns=get_columns())
    
    X = df.drop(columns=['clip', 'clasa', 'window_id'])
    y = df['clasa'].copy()
    
    # NU MAI EXISTA LABEL NOISE. Datele sunt 100% corecte.
    df['clasa'] = y
    
    X_train, X_test, y_train, y_test, clip_train, clip_test = train_test_split(
        X, y, df['clip'], test_size=0.2, random_state=42, stratify=y)
        
    df_train = pd.concat([clip_train, y_train, pd.Series([0]*len(y_train), name='window_id', index=y_train.index), X_train], axis=1)
    df_test = pd.concat([clip_test, y_test, pd.Series([0]*len(y_test), name='window_id', index=y_test.index), X_test], axis=1)
    
    out_dir = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\train"
    df_train.to_csv(os.path.join(out_dir, "train_vertical_jump.csv"), index=False)
    df_test.to_csv(os.path.join(out_dir, "test_vertical_jump.csv"), index=False)
    
    print(f"GATA! Am generat {len(df_train)} exemple train si {len(df_test)} exemple test.")

if __name__ == "__main__":
    main()
