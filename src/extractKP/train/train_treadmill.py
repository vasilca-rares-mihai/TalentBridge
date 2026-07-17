import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv1D, MaxPooling1D, GlobalAveragePooling1D,
    Dense, Dropout, BatchNormalization, Concatenate
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

TRAIN_CSV    = "train_run.csv"
TEST_CSV     = "test_run.csv"
WINDOW_SIZE  = 30
EPOCHS       = 150
BATCH_SIZE   = 32
LEARNING_RATE = 0.001

GLOBAL_METRIC_COLS = [
    "steps_in_window",
    "window_duration_sec",
    "cadence_spm",
    "estimated_speed_ms",
    "estimated_distance_m",
]
print("  ANTRENARE CNN — CLASIFICARE ALERGARE")

for f in [TRAIN_CSV, TEST_CSV]:
    if not os.path.exists(f):
        print(f"\nEroare: Nu gasesc fisierul '{f}'.")
        print("Ruleaza mai intai generate_run_dataset.py")
        exit(1)

print(f"\n[1] Incarcam datele...")
df_train = pd.read_csv(TRAIN_CSV)
df_test  = pd.read_csv(TEST_CSV)
print(f"    Train: {len(df_train)} exemple")
print(f"    Test : {len(df_test)} exemple")


print(f"\n[2] Pregatim feature-urile...")

def extract_features(df):
    per_frame_cols = sorted(
        [c for c in df.columns if any(c.endswith(f"_{i}") for i in range(WINDOW_SIZE))],
        key=lambda c: int(c.rsplit("_", 1)[-1])
    )

    assert len(per_frame_cols) % WINDOW_SIZE == 0, \
        f"Numar coloane per-frame ({len(per_frame_cols)}) nu e multiplu de {WINDOW_SIZE}"

    features_per_frame = len(per_frame_cols) // WINDOW_SIZE
    print(f"    Features per frame : {features_per_frame}  "
          f"(28 coordonate + 9 unghiuri)")
    print(f"    Metrici globali    : {len(GLOBAL_METRIC_COLS)}")

    data_flat = df[per_frame_cols].values.astype(np.float32)
    X_seq = data_flat.reshape(-1, WINDOW_SIZE, features_per_frame)

    X_meta = df[GLOBAL_METRIC_COLS].values.astype(np.float32)

    y = df["clasa"].values
    return X_seq, X_meta, y


X_train_seq,  X_train_meta, y_train_raw = extract_features(df_train)
X_test_seq,   X_test_meta,  y_test_raw  = extract_features(df_test)


label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(y_train_raw)
y_test  = label_encoder.transform(y_test_raw)

print(f"\n    Clase detectate: {list(label_encoder.classes_)}")
print(f"    Distributie train: ", end="")
for cls, idx in zip(label_encoder.classes_,
                    range(len(label_encoder.classes_))):
    print(f"{cls}={np.sum(y_train==idx)}", end="  ")
print()

print(f"\n[3] Normalizam datele...")

N_tr, T, F = X_train_seq.shape
scaler_seq = StandardScaler()
X_train_seq_sc = scaler_seq.fit_transform(
    X_train_seq.reshape(-1, F)).reshape(N_tr, T, F)
X_test_seq_sc  = scaler_seq.transform(
    X_test_seq.reshape(-1, F)).reshape(len(X_test_seq), T, F)

scaler_meta = StandardScaler()
X_train_meta_sc = scaler_meta.fit_transform(X_train_meta)
X_test_meta_sc  = scaler_meta.transform(X_test_meta)

joblib.dump(scaler_seq,  "scaler_seq.pkl")
joblib.dump(scaler_meta, "scaler_meta.pkl")
print("    scaler_seq.pkl  salvat")
print("    scaler_meta.pkl salvat")

print(f"\n[4] Construim modelul...")

numar_clase = len(label_encoder.classes_)

seq_input = Input(shape=(WINDOW_SIZE, F), name="input_sequence")

x = Conv1D(64, 3, padding="same", activation="relu")(seq_input)
x = BatchNormalization()(x)
x = MaxPooling1D(2)(x)

x = Conv1D(128, 3, padding="same", activation="relu")(x)
x = BatchNormalization()(x)
x = MaxPooling1D(2)(x)

x = Conv1D(64, 3, padding="same", activation="relu")(x)
x = BatchNormalization()(x)
x = GlobalAveragePooling1D()(x)
meta_input = Input(shape=(len(GLOBAL_METRIC_COLS),), name="input_meta")
m = Dense(32, activation="relu")(meta_input)
m = BatchNormalization()(m)
merged = Concatenate()([x, m])
out = Dense(128, activation="relu")(merged)
out = Dropout(0.4)(out)
out = Dense(numar_clase, activation="softmax", name="output")(out)

model = Model(inputs=[seq_input, meta_input], outputs=out)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

print(f"\n[5] Antrenam modelul ({EPOCHS} epoci)...")

early_stop = tf.keras.callbacks.EarlyStopping(
    monitor="val_accuracy",
    patience=15,
    restore_best_weights=True,
    verbose=1
)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=7,
    min_lr=1e-6,
    verbose=1
)

istoric = model.fit(
    [X_train_seq_sc, X_train_meta_sc], y_train,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_data=([X_test_seq_sc, X_test_meta_sc], y_test),
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

model.save("model_run.h5")
np.save("clase_run.npy", label_encoder.classes_)
print("\n    model_run.h5   salvat")
print("    clase_run.npy  salvat")
loss, accuracy = model.evaluate(
    [X_test_seq_sc, X_test_meta_sc], y_test, verbose=0)

print(f"  ACURATETEA FINALA PE TESTARE: {accuracy * 100:.2f}%")

epoci_rulate = len(istoric.history["accuracy"])

plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(istoric.history["accuracy"],     label="Train")
plt.plot(istoric.history["val_accuracy"], label="Validare")
plt.title("Evolutia Acuratetei")
plt.xlabel("Epoci")
plt.ylabel("Acuratete")
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(istoric.history["loss"],     label="Train")
plt.plot(istoric.history["val_loss"], label="Validare")
plt.title("Evolutia Loss-ului")
plt.xlabel("Epoci")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)

plt.suptitle(f"Antrenare CNN — Alergare  ({epoci_rulate} epoci)", y=1.02)
plt.tight_layout()
plt.savefig("antrenare_run.png", dpi=150, bbox_inches="tight")
plt.show()


print("\n[6] Generam matricea de confuzie...")

predictii  = model.predict([X_test_seq_sc, X_test_meta_sc], verbose=0)
y_pred     = np.argmax(predictii, axis=1)
cm         = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Greens",
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_,
    cbar=False,
    linewidths=0.5,
)
plt.xlabel("Clasa Prezisa")
plt.ylabel("Clasa Reala")
plt.title(f"Matrice de Confuzie — Accuracy: {accuracy * 100:.2f}%")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("matrice_confuzie_run.png", dpi=300)
plt.show()

print("\nRaport per clasa:")
print(classification_report(
    y_test, y_pred,
    target_names=label_encoder.classes_
))

print("\nFisiere salvate:")
print("  model_run.h5")
print("  scaler_seq.pkl")
print("  scaler_meta.pkl")
print("  clase_run.npy")
print("  matrice_confuzie_run.png")
print("  antrenare_run.png")