import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Dropout, BatchNormalization
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt
import os
import joblib
from sklearn.metrics import confusion_matrix
import seaborn as sns

print("Incarcam seturile izolate de Train si Test...")

CSV_DIR = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\csv"
DATA_DIR = r"C:\Users\rares\Desktop\TalentBridge\src\service\analysis_worker\app\analyzers\data"
os.makedirs(DATA_DIR, exist_ok=True)

df_train = pd.read_csv(os.path.join(CSV_DIR, 'train_squats.csv'))
df_test = pd.read_csv(os.path.join(CSV_DIR, 'test_squats.csv'))

label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(df_train['clasa'].values)

y_test = label_encoder.transform(df_test['clasa'].values)

date_numerice_train = df_train.iloc[:, 3:].values
date_numerice_test = df_test.iloc[:, 3:].values

WINDOW_SIZE = 30
nr_total_caracteristici = date_numerice_train.shape[1]
caracteristici_per_cadru = int(nr_total_caracteristici / WINDOW_SIZE)

scaler = StandardScaler()
date_scalate_train = scaler.fit_transform(date_numerice_train)
date_scalate_test = scaler.transform(date_numerice_test)

joblib.dump(scaler, os.path.join(DATA_DIR, 'scaler_squats_30f.pkl'))

X_train = date_scalate_train.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)
X_test = date_scalate_test.reshape(-1, WINDOW_SIZE, caracteristici_per_cadru)

print(f"Train izolat: {len(X_train)} ferestre")
print(f"Test izolat: {len(X_test)} ferestre")
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

model.save(os.path.join(DATA_DIR, 'model_squats_30f.h5'))
np.save(os.path.join(DATA_DIR, 'clase_squats_30f.npy'), label_encoder.classes_)
print(f"Model + clase + scaler salvate DIRECT in: {DATA_DIR}")

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

print("\n=========================================")
print(f"ACURATETEA FINALA PE TESTARE: {accuracy * 100:.2f}%")
print("=========================================")

plt.figure(figsize=(8, 5))
plt.plot(istoric.history['accuracy'], label='Train Accuracy')
plt.plot(istoric.history['val_accuracy'], label='Validation Accuracy')
plt.title('Evolutia Acuratetei - Genoflexiuni')
plt.xlabel('Epoci')
plt.ylabel('Acuratete')
plt.legend()
plt.grid(True)
plt.show()

print("\nGeneram matricea de confuzie...")
predictii = model.predict(X_test, verbose=0)
y_pred = np.argmax(predictii, axis=1)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(9, 7))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_,
    cbar=False
)

plt.xlabel('Clasa Prezisa')
plt.ylabel('Clasa Reala')
plt.title(f'Matrice de Confuzie Squats - Accuracy: {accuracy * 100:.2f}%')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('matrice_confuzie_squats_30f.png', dpi=300)
plt.show()

print("Modelul si matricea pentru genoflexiuni au fost salvate cu succes.")