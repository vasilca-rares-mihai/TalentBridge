"""
Antrenare model PULLUP (CNN 1D, aceeasi arhitectura ca la pushup).
Citeste train_pullup.csv / test_pullup.csv (generate de date_sintetice/pullups.py).

Salveaza direct in folderul backend-ului:
    data/model_pullup.h5
    data/clase_pullup.npy
    data/scaler_pullup.pkl
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Input, Conv1D, MaxPooling1D, GlobalAveragePooling1D,
    Dense, Dropout, BatchNormalization
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib

WINDOW_SIZE = 30

CALE_TRAIN = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\date_sintetice\train_pullup.csv"
CALE_TEST = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\date_sintetice\test_pullup.csv"

OUTPUT_DIR = r"C:\Users\rares\Desktop\TalentBridge\src\service\analysis_worker\app\analyzers\data"

for cale in (CALE_TRAIN, CALE_TEST):
    if not os.path.exists(cale):
        print(f"Eroare: nu gasesc {cale}. Ruleaza intai date_sintetice/pullups.py")
        exit()

print("Incarcam datele...")
df_train = pd.read_csv(CALE_TRAIN)
df_test = pd.read_csv(CALE_TEST)

# Etichete (fit pe train, aplicat pe ambele)
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(df_train['clasa'].values)
y_test = label_encoder.transform(df_test['clasa'].values)

# Features numerice (sar peste clip, clasa, window_id)
X_train_flat = df_train.iloc[:, 3:].values
X_test_flat = df_test.iloc[:, 3:].values

nr_total = X_train_flat.shape[1]
caracteristici_per_cadru = int(nr_total / WINDOW_SIZE)
print(f"Caracteristici per cadru: {caracteristici_per_cadru} (trebuie 19)")

# Scaler fit DOAR pe train -> evitam leakage
scaler = StandardScaler()
X_train_flat = scaler.fit_transform(X_train_flat)
X_test_flat = scaler.transform(X_test_flat)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
joblib.dump(scaler, os.path.join(OUTPUT_DIR, 'scaler_pullup.pkl'))

X_train = X_train_flat.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)
X_test = X_test_flat.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)

print(f"Train: {len(X_train)} | Test: {len(X_test)}")

numar_clase = len(np.unique(y_train))

model = Sequential([
    Input(shape=(WINDOW_SIZE, caracteristici_per_cadru)),

    Conv1D(64, 3, padding='same', activation='relu'),
    BatchNormalization(),
    MaxPooling1D(2),

    Conv1D(128, 3, padding='same', activation='relu'),
    BatchNormalization(),

    GlobalAveragePooling1D(),

    Dense(128, activation='relu'),
    Dropout(0.4),

    Dense(numar_clase, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\nIncepem antrenarea...")
istoric = model.fit(
    X_train, y_train,
    epochs=150,
    batch_size=32,
    validation_data=(X_test, y_test),
    verbose=1
)

# Salvare in backend
model.save(os.path.join(OUTPUT_DIR, 'model_pullup.h5'))
np.save(os.path.join(OUTPUT_DIR, 'clase_pullup.npy'), label_encoder.classes_)

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print("\n=========================================")
print(f"ACURATETEA FINALA PE TESTARE: {accuracy * 100:.2f}%")
print("=========================================")
print(f"Clase: {list(label_encoder.classes_)}")

# Matrice de confuzie
y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_, cbar=False)
plt.xlabel('Clasa Prezisa')
plt.ylabel('Clasa Reala')
plt.title(f'Matrice Confuzie Pullup - Acc: {accuracy * 100:.2f}%')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('matrice_confuzie_pullup.png', dpi=300)
print("Modelul si matricea au fost salvate.")
