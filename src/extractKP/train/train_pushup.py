import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Dropout, \
    BatchNormalization
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt
import os
import joblib

print("Incarcam datele din CSV...")
nume_csv = '../csv/dataset_xyz_unghiuri_varianta3.csv'

if not os.path.exists(nume_csv):
    print(f"Eroare: Nu gasesc fisierul {nume_csv}.")
    exit()

df = pd.read_csv(nume_csv)
etichete_text = df['clasa'].values

label_encoder = LabelEncoder()
etichete_numerice = label_encoder.fit_transform(etichete_text)

date_numerice = df.iloc[:, 3:].values
WINDOW_SIZE = 30
nr_total_caracteristici = date_numerice.shape[1]
caracteristici_per_cadru = int(nr_total_caracteristici / WINDOW_SIZE)

scaler = StandardScaler()
date_scalate = scaler.fit_transform(date_numerice)

joblib.dump(scaler, 'scaler_flotari.pkl')

X = date_scalate.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)
y = etichete_numerice

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Date pregatite cu succes!")
print(f"Avem {len(X_train)} mostre pentru invatare si {len(X_test)} pentru testare.")

print("\nConstruim arhitectura modelului...")
numar_clase = len(np.unique(y))

model = Sequential([
    Input(shape=(WINDOW_SIZE, caracteristici_per_cadru)),

    Conv1D(filters=64, kernel_size=3, padding='same', activation='relu'),
    BatchNormalization(),
    MaxPooling1D(pool_size=2),

    Conv1D(filters=128, kernel_size=3, padding='same', activation='relu'),
    BatchNormalization(),

    GlobalAveragePooling1D(),

    Dense(128, activation='relu'),
    Dropout(0.4),
    Dense(numar_clase, activation='softmax')
])

optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(optimizer=optimizer,
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

print("\nIncepem antrenarea...")
istoric = model.fit(X_train, y_train,
                    epochs=150,
                    batch_size=32,
                    validation_data=(X_test, y_test))

model.save('model_flotari.h5')
np.save('clase.npy', label_encoder.classes_)

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\n=========================================")
print(f"ACURATETEA FINALA PE TESTARE: {accuracy * 100:.2f}%")
print(f"=========================================")

plt.figure(figsize=(8, 5))
plt.plot(istoric.history['accuracy'], label='Acuratete Antrenare')
plt.plot(istoric.history['val_accuracy'], label='Acuratete Testare')
plt.title('Evolutia Acuratetei Modelului de Flotari (Cu Scalare)')
plt.xlabel('Epoci (Iteratii de invatare)')
plt.ylabel('Acuratete')
plt.legend()
plt.grid(True)
plt.show()

from sklearn.metrics import confusion_matrix
import seaborn as sns

print("\nGeneram matricea de confuzie REALA...")
predictii_brute = model.predict(X_test, verbose=0)
y_pred = np.argmax(predictii_brute, axis=1)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(9, 7))

nume_clase = label_encoder.classes_

sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=nume_clase, yticklabels=nume_clase,
            annot_kws={"size": 13, "weight": "bold"}, cbar=False)

plt.xlabel('Clasa Prezisa (Predictie AI)', fontweight='bold', fontsize=12)
plt.ylabel('Clasa Reala (Adevarul)', fontweight='bold', fontsize=12)
plt.title(f'Matrice de Confuzie - Flotari (Acuratete: {accuracy * 100:.2f}%)', fontweight='bold', fontsize=14)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.savefig('matrice_confuzie_pushups.png', dpi=300)
print("Succes! Poza a fost salvata ca 'matrice_confuzie_pushups.png' in folderul curent.")