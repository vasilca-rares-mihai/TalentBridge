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
import matplotlib.pyplot as plt
import os
import joblib
from sklearn.metrics import confusion_matrix
import seaborn as sns

print("Incarcam datele din CSV...")

nume_csv = '../csv/dataset_unghiuri_60frames.csv'

if not os.path.exists(nume_csv):
    print(f"Eroare: Nu gasesc fisierul {nume_csv}.")
    exit()

df = pd.read_csv(nume_csv)

# Etichete
etichete_text = df['clasa'].values
label_encoder = LabelEncoder()
etichete_numerice = label_encoder.fit_transform(etichete_text)

# Features numerice
date_numerice = df.iloc[:, 3:].values

# IMPORTANT: 60 frame-uri
WINDOW_SIZE = 60

nr_total_caracteristici = date_numerice.shape[1]
caracteristici_per_cadru = int(nr_total_caracteristici / WINDOW_SIZE)

print(f"Caracteristici per cadru: {caracteristici_per_cadru}")

# Normalizare
scaler = StandardScaler()
date_scalate = scaler.fit_transform(date_numerice)

joblib.dump(scaler, 'scaler_flotari_60f.pkl')

# Reshape pentru CNN 1D
X = date_scalate.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)
y = etichete_numerice

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Date pregatite cu succes!")
print(f"Train: {len(X_train)}")
print(f"Test: {len(X_test)}")

# Model
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

# Salvare
model.save('model_flotari_60f.h5')
np.save('clase_60f.npy', label_encoder.classes_)

# Evaluare
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

print("\n=========================================")
print(f"ACURATETEA FINALA PE TESTARE: {accuracy * 100:.2f}%")
print("=========================================")

# Plot accuracy
plt.figure(figsize=(8, 5))
plt.plot(istoric.history['accuracy'], label='Train Accuracy')
plt.plot(istoric.history['val_accuracy'], label='Validation Accuracy')
plt.title('Evolutia Acuratetei')
plt.xlabel('Epoci')
plt.ylabel('Acuratete')
plt.legend()
plt.grid(True)
plt.show()

# Confusion matrix
print("\nGeneram matricea de confuzie...")
predictii = model.predict(X_test, verbose=0)
y_pred = np.argmax(predictii, axis=1)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(9, 7))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Greens',
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_,
    cbar=False
)

plt.xlabel('Clasa Prezisa')
plt.ylabel('Clasa Reala')
plt.title(f'Matrice de Confuzie - Accuracy: {accuracy * 100:.2f}%')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('matrice_confuzie_60f.png', dpi=300)
plt.show()

print("Modelul si matricea au fost salvate cu succes.")