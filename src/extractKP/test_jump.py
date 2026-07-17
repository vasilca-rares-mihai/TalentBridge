import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
video_path = r"C:\Users\rares\Desktop\vertical_jump_dataset\.perfect\WhatsApp Video 2026-06-14 at 13.18.47.mp4"

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

cap = cv2.VideoCapture(video_path)
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    ref_x, ref_y, ref_s = None, None, None
    stare = "STAND"
    cadre_in_aer = 0
    frame_idx = 0
    
    print("FRAME | STARE  | U_GEN  | Y_SOLD | U_ANKLE")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame_idx += 1
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
            
            u_gen = (feat[24] + feat[25]) / 2  
            y_curent_sold = (feat[9] + feat[11]) / 2
            u_ankle = (feat[28] + feat[29]) / 2

            print(f"{frame_idx:03d}   | {stare:6s} | {u_gen:6.1f} | {y_curent_sold:6.3f} | {u_ankle:6.1f}")
            
            if u_gen < 155 and stare in ["STAND", "LAND"]:
                stare = "SQUAT"
                cadre_in_aer = 0
            
            if stare == "SQUAT" and u_gen > 160 and y_curent_sold < 0.50:
                stare = "FLIGHT"
                
            if stare == "FLIGHT":
                cadre_in_aer += 1
                if u_gen < 155 and y_curent_sold > 0.50 and cadre_in_aer > 4:
                    stare = "LAND"
                    print("--> LAND DETECTED!")
                    
            if stare == "LAND" and u_gen > 165:
                stare = "STAND"
cap.release()
