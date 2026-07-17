"""
Rebuild model SARITURA IN LUNGIME — 3 clase: perfect / fall_landing / no_arm_swing.

Porneste de la dataset_jump.csv (ferestre PERFECTE jump-aligned, deja normalizate
hip-centric/torso de catre extractor) si fabrica sintetic cele 2 greseli:

  - fall_landing : in faza de aterizare (cadre 22..29) picioarele se prabusesc
                   (genunchi/sold se inchid, gleznele urca spre sold, umerii cad pe spate)
  - no_arm_swing : pe TOATE cadrele bratele (coate+incheieturi) sunt aproape statice
                   (fara balans inainte de saritura), unghiurile cot/brat ~ constante

Output (direct in backend):
    data/model_jump_30f.h5
    data/clase_jump_30f.npy
    data/scaler_jump_30f.pkl
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D,
                                      GlobalAveragePooling1D, Dense, Dropout, BatchNormalization)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib

BASE_CSV = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\date_sintetice\dataset_jump.csv"
DATA_DIR = r"C:\Users\rares\Desktop\TalentBridge\src\service\analysis_worker\app\analyzers\data"

WINDOW_SIZE = 30
FEATS = 64  # 14 lm * 4 + 8 unghiuri

# ---- index-uri in vectorul de 64 (TREBUIE sa corespunda extractorului/analyzer-ului) ----
# landmark m: x=4m, y=4m+1, z=4m+2, v=4m+3
LM_ORDER = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
            'left_foot_index', 'right_foot_index']
mi = {n: i for i, n in enumerate(LM_ORDER)}

def cx(n): return 4 * mi[n]
def cy(n): return 4 * mi[n] + 1
def cz(n): return 4 * mi[n] + 2

A_KNEE_L, A_KNEE_R = 56, 57
A_HIP_L,  A_HIP_R  = 58, 59
A_COT_L,  A_COT_R  = 60, 61
A_BRAT_L, A_BRAT_R = 62, 63

LAND_FR = range(22, 30)   # faza de aterizare

if not os.path.exists(BASE_CSV):
    print(f"Nu gasesc baza: {BASE_CSV}")
    raise SystemExit

print("Incarcam baza reala (perfect, jump-aligned)...")
df = pd.read_csv(BASE_CSV)
feat_per_frame = (df.shape[1] - 3) // WINDOW_SIZE
print(f"  {len(df)} ferestre, {feat_per_frame} features/cadru (trebuie {FEATS})")
assert feat_per_frame == FEATS, "Numar gresit de features/cadru! Re-ruleaza extractorul."

base = df.iloc[:, 3:].values.astype(np.float32).reshape(-1, WINDOW_SIZE, FEATS)
print(f"  tensor baza: {base.shape}")


def make(n, clasa, rng):
    out = np.empty((n, WINDOW_SIZE, FEATS), dtype=np.float32)
    for r in range(n):
        w = base[rng.integers(0, len(base))].copy()  # (30,64)

        if clasa == 'fall_landing':
            for f in LAND_FR:
                w[f, A_KNEE_L] = np.clip(w[f, A_KNEE_L] - rng.uniform(35, 55), 20, 180)
                w[f, A_KNEE_R] = np.clip(w[f, A_KNEE_R] - rng.uniform(35, 55), 20, 180)
                w[f, A_HIP_L]  = np.clip(w[f, A_HIP_L]  - rng.uniform(25, 45), 20, 180)
                w[f, A_HIP_R]  = np.clip(w[f, A_HIP_R]  - rng.uniform(25, 45), 20, 180)
                # picioarele se pliaza: gleznele/genunchii urca spre sold (y -> spre 0)
                for n_lm in ['left_ankle', 'right_ankle', 'left_knee', 'right_knee',
                             'left_foot_index', 'right_foot_index']:
                    w[f, cy(n_lm)] *= rng.uniform(0.3, 0.6)
                # umerii cad pe spate/jos
                w[f, cy('left_shoulder')]  += rng.uniform(0.10, 0.30)
                w[f, cy('right_shoulder')] += rng.uniform(0.10, 0.30)

        elif clasa == 'no_arm_swing':
            # inghetam bratele la postura medie a ferestrei (fara balans)
            for n_lm in ['left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']:
                for axis in (cx(n_lm), cy(n_lm), cz(n_lm)):
                    m = w[:, axis].mean()
                    w[:, axis] = m + rng.normal(0, 0.01, WINDOW_SIZE)
            # unghiuri brat ~ constante (brate pe langa corp)
            w[:, A_COT_L]  = 165 + rng.normal(0, 4, WINDOW_SIZE)
            w[:, A_COT_R]  = 165 + rng.normal(0, 4, WINDOW_SIZE)
            w[:, A_BRAT_L] = 18  + rng.normal(0, 4, WINDOW_SIZE)
            w[:, A_BRAT_R] = 18  + rng.normal(0, 4, WINDOW_SIZE)

        # zgomot natural general
        w[:, 56:64] += rng.normal(0, 1.5, (WINDOW_SIZE, 8))      # unghiuri
        coord_mask = np.array([j % 4 != 3 and j < 56 for j in range(FEATS)])
        w[:, coord_mask] += rng.normal(0, 0.02, (WINDOW_SIZE, int(coord_mask.sum())))

        out[r] = w
    return out, [clasa] * n


print("Generam date echilibrate (2 x 1500)...")
rng = np.random.default_rng(42)
X_parts, y_parts = [], []
for clasa in ['perfect', 'fall_landing']:
    Xc, yc = make(1500, clasa, rng)
    X_parts.append(Xc); y_parts.extend(yc)
X = np.vstack(X_parts).reshape(-1, WINDOW_SIZE * FEATS)
y_text = np.array(y_parts)

le = LabelEncoder()
y = le.fit_transform(y_text)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train = X_train.reshape(-1, WINDOW_SIZE, FEATS)
X_test = X_test.reshape(-1, WINDOW_SIZE, FEATS)

model = Sequential([
    Input(shape=(WINDOW_SIZE, FEATS)),
    Conv1D(64, 3, padding='same', activation='relu'),
    BatchNormalization(),
    MaxPooling1D(2),
    Conv1D(128, 3, padding='same', activation='relu'),
    BatchNormalization(),
    GlobalAveragePooling1D(),
    Dense(128, activation='relu'),
    Dropout(0.4),
    Dense(len(le.classes_), activation='softmax'),
])
model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print("\nAntrenam...")
model.fit(X_train, y_train, epochs=120, batch_size=32,
          validation_data=(X_test, y_test), verbose=1)

os.makedirs(DATA_DIR, exist_ok=True)
model.save(os.path.join(DATA_DIR, 'model_jump_30f.h5'))
np.save(os.path.join(DATA_DIR, 'clase_jump_30f.npy'), le.classes_)
joblib.dump(scaler, os.path.join(DATA_DIR, 'scaler_jump_30f.pkl'))

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print("\n=========================================")
print(f"ACURATETE TEST: {acc*100:.2f}%  | clase: {list(le.classes_)}")
print("Salvat in:", DATA_DIR)
print("=========================================")
