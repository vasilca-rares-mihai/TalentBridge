import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Input,
    Conv1D,
    MaxPooling1D,
    GlobalAveragePooling1D,
    Dense,
    Dropout,
    BatchNormalization
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os
import joblib

print("Incarcam datele din CSV-ul nou (corectat)...")

nume_csv = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\csv\dataset_pushups_fixed.csv"

if not os.path.exists(nume_csv):
    print(f"Eroare: Nu gasesc fisierul {nume_csv}.")
    exit()

df = pd.read_csv(nume_csv)

etichete_text = df['clasa'].values
label_encoder = LabelEncoder()
etichete_numerice = label_encoder.fit_transform(etichete_text)

# Coloanele: clip, clasa, window_id (primele 3)
date_numerice = df.iloc[:, 3:].values

WINDOW_SIZE = 30

nr_total_caracteristici = date_numerice.shape[1]
caracteristici_per_cadru = int(nr_total_caracteristici / WINDOW_SIZE)

print(f"Caracteristici per cadru: {caracteristici_per_cadru} (trebuie sa fie 19)")

scaler = StandardScaler()
date_scalate = scaler.fit_transform(date_numerice)

output_dir = r"C:\Users\rares\Desktop\TalentBridge\src\service\analysis_worker\app\analyzers\data"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

joblib.dump(scaler, os.path.join(output_dir, 'scaler_flotari.pkl'))

X = date_scalate.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)
y = etichete_numerice

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Date pregatite cu succes!")
print(f"Train: {len(X_train)}")
print(f"Test: {len(X_test)}")

numar_clase = len(np.unique(y))

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

optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(
    optimizer=optimizer,
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

model.save(os.path.join(output_dir, 'model_flotari.h5'))
np.save(os.path.join(output_dir, 'clase.npy'), label_encoder.classes_)

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

print("\n=========================================")
print(f"ACURATETEA FINALA PE TESTARE: {accuracy * 100:.2f}%")
print("=========================================")
print("Modelele au fost salvate direct in folderul backend-ului!")
