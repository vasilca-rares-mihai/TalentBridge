import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import random
import math
import os
from sklearn.model_selection import train_test_split

mp_pose = mp.solutions.pose

# =========================================================================
# 1. FUNCTII AJUTATOARE (Matematica Invarianta la Distanta)
# =========================================================================

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def normalizeaza_3d_squat(punct, ref_x, ref_y, ref_z, scale_factor, visibility):
    if scale_factor < 0.001:
        scale_factor = 1.0
    return [
        (punct.x - ref_x) / scale_factor,
        (punct.y - ref_y) / scale_factor,
        (punct.z - ref_z) / scale_factor,
        visibility
    ]

NUME_COLOANE = [
    'l_shoulder_x', 'l_shoulder_y', 'l_shoulder_z', 'l_shoulder_v',
    'r_shoulder_x', 'r_shoulder_y', 'r_shoulder_z', 'r_shoulder_v',
    'l_hip_x', 'l_hip_y', 'l_hip_z', 'l_hip_v',
    'r_hip_x', 'r_hip_y', 'r_hip_z', 'r_hip_v',
    'l_knee_x', 'l_knee_y', 'l_knee_z', 'l_knee_v',
    'r_knee_x', 'r_knee_y', 'r_knee_z', 'r_knee_v',
    'l_ankle_x', 'l_ankle_y', 'l_ankle_z', 'l_ankle_v',
    'r_ankle_x', 'r_ankle_y', 'r_ankle_z', 'r_ankle_v',
    'l_foot_x', 'l_foot_y', 'l_foot_z', 'l_foot_v',
    'r_foot_x', 'r_foot_y', 'r_foot_z', 'r_foot_v',
    'unghi_sold_l', 'unghi_genunchi_l', 'unghi_glezna_l',
    'unghi_sold_r', 'unghi_genunchi_r', 'unghi_glezna_r'
]

# =========================================================================
# 2. EXTRACTIA DATELOR REALE DIN VIDEO
# =========================================================================

def extract_rep_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    
    stare_miscare = "UP"
    constant_scale = 0.0
    cadre_repetitie_curenta = []
    repetitie_gasita = None
    cooldown_frames = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

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

                mid_hip_x = (l_hip.x + r_hip.x) / 2.0
                mid_hip_y = (l_hip.y + r_hip.y) / 2.0
                mid_hip_z = (l_hip.z + r_hip.z) / 2.0

                mid_sh_x = (l_sh.x + r_sh.x) / 2.0
                mid_sh_y = (l_sh.y + r_sh.y) / 2.0
                mid_sh_z = (l_sh.z + r_sh.z) / 2.0
                s_curent = math.sqrt((mid_sh_x - mid_hip_x) ** 2 + (mid_sh_y - mid_hip_y) ** 2 + (mid_sh_z - mid_hip_z) ** 2)

                if stare_miscare == "UP":
                    constant_scale = max(constant_scale, s_curent)
                scale_to_use = constant_scale if constant_scale > 0.001 else s_curent

                features = []
                for lm in [l_sh, r_sh, l_hip, r_hip, l_kn, r_kn, l_an, r_an, l_fi, r_fi]:
                    features.extend(normalizeaza_3d_squat(lm, mid_hip_x, mid_hip_y, mid_hip_z, scale_to_use, lm.visibility))

                unghi_sold_l = calculate_angle([l_sh.x, l_sh.y], [l_hip.x, l_hip.y], [l_kn.x, l_kn.y])
                unghi_genunchi_l = calculate_angle([l_hip.x, l_hip.y], [l_kn.x, l_kn.y], [l_an.x, l_an.y])
                unghi_glezna_l = calculate_angle([l_kn.x, l_kn.y], [l_an.x, l_an.y], [l_fi.x, l_fi.y])

                unghi_sold_r = calculate_angle([r_sh.x, r_sh.y], [r_hip.x, r_hip.y], [r_kn.x, r_kn.y])
                unghi_genunchi_r = calculate_angle([r_hip.x, r_hip.y], [r_kn.x, r_kn.y], [r_an.x, r_an.y])
                unghi_glezna_r = calculate_angle([r_kn.x, r_kn.y], [r_an.x, r_an.y], [r_fi.x, r_fi.y])

                features.extend([unghi_sold_l, unghi_genunchi_l, unghi_glezna_l, unghi_sold_r, unghi_genunchi_r, unghi_glezna_r])

                cadre_repetitie_curenta.append(features)

                # Relaxam la 160 de grade ca sa prindem si genuflexiunile incomplete
                if unghi_genunchi_l < 160 and stare_miscare == "UP":
                    stare_miscare = "DOWN"
                    # Resetam buffer-ul pastrand 10 cadre de UP inainte de miscare pentru context
                    cadre_repetitie_curenta = cadre_repetitie_curenta[-10:]

                # Cand ne-am ridicat inapoi la 165
                if unghi_genunchi_l > 165 and stare_miscare == "DOWN":
                    stare_miscare = "COOLDOWN"
                    # Adaugam un cooldown de 15 cadre (0.5 sec) ca sa prindem postura de "arched_back" de la final
                    cooldown_frames = 15
                    
                if stare_miscare == "COOLDOWN":
                    cooldown_frames -= 1
                    if cooldown_frames <= 0:
                        repetitie_gasita = cadre_repetitie_curenta
                        break

    cap.release()
    
    # Fallback in caz ca nu ajunge la cooldown dar are date
    if repetitie_gasita is None and len(cadre_repetitie_curenta) > 15:
        repetitie_gasita = cadre_repetitie_curenta
        
    return repetitie_gasita

def normalize_to_30_frames(rep_features):
    if not rep_features or len(rep_features) < 5:
        return None
    indici = np.linspace(0, len(rep_features) - 1, 30).astype(int)
    return [rep_features[idx] for idx in indici]

# =========================================================================
# 3. AUGMENTAREA DATELOR REALE (Doar Zgomot Gaussian)
# =========================================================================

def augment_real_data(base_reps, class_name, target_count):
    augmented_rows = []
    
    if not base_reps:
        return []
        
    for _ in range(target_count):
        # Alege o repetare reala aleatoare din clasa
        rep = random.choice(base_reps)

        # variatii PE INTREAGA repetare (simuleaza alt gabarit / alta distanta de camera)
        # BLANDE: zgomot prea mare sterge diferenta de ADANCIME (perfect vs incomplete)
        scale = np.random.uniform(0.92, 1.08)     # scalare globala a coordonatelor
        shift_x = np.random.uniform(-0.03, 0.03)  # mica translatie
        shift_y = np.random.uniform(-0.03, 0.03)

        row_dict = {'clip': 'real_aug', 'clasa': class_name, 'window_id': 0}

        for i in range(30):
            for j, nume_col in enumerate(NUME_COLOANE):
                val = rep[i][j]

                if 'unghi' in nume_col:
                    # zgomot MIC pe unghiuri, ca sa NU stergem granita de adancime
                    val += np.random.normal(0, 5.0)
                elif '_v' in nume_col:
                    pass  # vizibilitatea ramane neatinsa
                else:
                    # coordonate: scalare + translatie + zgomot (mic)
                    val = val * scale + np.random.normal(0, 0.03)
                    if nume_col.endswith('_x'):
                        val += shift_x
                    elif nume_col.endswith('_y'):
                        val += shift_y

                row_dict[f"{nume_col}_{i}"] = val

        augmented_rows.append(row_dict)
        
    return augmented_rows

# =========================================================================
# 4. EXECUTIA PRINCIPALA
# =========================================================================
if __name__ == "__main__":
    # AICI TREBUIE SA FIE VIDEOCLIPURILE TALE
    DATASET_DIR = r"C:\Users\rares\Desktop\squat_dataset"
    
    clase_gasite = {}
    
    if not os.path.exists(DATASET_DIR):
        print(f"Eroare: Folderul {DATASET_DIR} nu exista.")
        print("Creeaza-l si adauga subfolderele: perfect, arched_back, uncompleted, apoi pune clipurile!")
        exit(1)
        
    print(f"=== PAS 1: Extractia Bazei Din Video Reale ===")
    for folder_name in os.listdir(DATASET_DIR):
        folder_path = os.path.join(DATASET_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        # Numele clasei: 'perfect', 'arched_back', 'uncompleted'
        class_name = folder_name.replace('.', '')
        print(f"\nProcesam clasa: {class_name}")
        
        clase_gasite[class_name] = []
        
        for video_file in os.listdir(folder_path):
            if not video_file.endswith(('.mp4', '.mov', '.avi')):
                continue
                
            video_path = os.path.join(folder_path, video_file)
            print(f" -> Se extrage din: {video_file}")
            rep_brut = extract_rep_from_video(video_path)
            
            if rep_brut:
                rep_30 = normalize_to_30_frames(rep_brut)
                if rep_30:
                    clase_gasite[class_name].append(rep_30)
                else:
                    print(f"    [WARN] Nu s-a putut normaliza la 30 de cadre: {video_file}")
            else:
                print(f"    [WARN] Nu am gasit o repetare valida in {video_file}")

    print("\n=== PAS 2: Split pe VIDEO + Augmentare (FARA leakage) ===")
    # Impartim repetarile REALE (pe clip) inainte de augmentare, ca testul sa fie ONEST.
    train_rows, test_rows = [], []

    for class_name, reps in clase_gasite.items():
        if len(reps) == 0:
            print(f"[WARN] Niciun videoclip valid extras pentru {class_name}!")
            continue

        if len(reps) >= 2:
            reps_tr, reps_te = train_test_split(reps, test_size=0.3, random_state=42)
        else:
            # prea putine clipuri reale: testul ar contine aceleasi repetari ca train-ul
            reps_tr, reps_te = reps, reps
            print(f"[WARN] Doar {len(reps)} clip(uri) reale pentru '{class_name}'! "
                  f"Acuratetea pe test va fi FALS de mare (leakage). Filmeaza mai multe clipuri.")

        print(f"  {class_name}: {len(reps_tr)} clip(uri) train -> 1000 | {len(reps_te)} clip(uri) test -> 250")
        train_rows.extend(augment_real_data(reps_tr, class_name, 1000))
        test_rows.extend(augment_real_data(reps_te, class_name, 250))

    if len(train_rows) == 0:
        print("Eroare: Nu s-au putut genera date (fisiere lipsa sau repetari nedetectate).")
        exit(1)

    train_df = pd.DataFrame(train_rows)
    test_df = pd.DataFrame(test_rows)

    print("\n=== PAS 3: Salvare ===")
    OUT_DIR = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\csv"
    os.makedirs(OUT_DIR, exist_ok=True)
    train_df.to_csv(os.path.join(OUT_DIR, 'train_squats.csv'), index=False)
    test_df.to_csv(os.path.join(OUT_DIR, 'test_squats.csv'), index=False)

    print(f"\nSUCCES! {len(train_df)} train si {len(test_df)} test (split pe clipuri, acuratete onesta).")
    print(f"CSV salvate in: {OUT_DIR}")