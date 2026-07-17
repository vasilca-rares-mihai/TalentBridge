"""
Augmentare sintetica pentru PULLUP (reteta de la long_jumps.py).
Porneste de la un CSV REAL de baza (extras cu extract_pullups.py) si fabrica
clasele de greseli aplicand penalizari de unghi pe faze, + zgomot natural.

Clase generate:
    perfect            -> doar zgomot mic (repetare corecta)
    uncompleted        -> barbia nu trece bara: cotul nu se inchide la varf
    no_full_extension  -> jos: bratele nu se intind complet (half rep la baza)

Input : dataset_pullups.csv (real)
Output: train_pullup.csv / test_pullup.csv
"""

import pandas as pd
import numpy as np
import random
import os
from sklearn.model_selection import train_test_split

CALE_BAZA = r"C:\Users\rares\Desktop\TalentBridge\src\extractKP\csv\dataset_pullups.csv"
FRAMES = 30

if not os.path.exists(CALE_BAZA):
    print(f"Nu gasesc CSV-ul de baza: {CALE_BAZA}")
    print("Ruleaza intai extract_pullups.py pe clipurile reale.")
    exit()

df = pd.read_csv(CALE_BAZA)
print(f"CSV de baza incarcat: {len(df)} ferestre reale.")

META_COLS = ['clip', 'clasa', 'window_id']

# Impartim baza inainte de augmentare (ca sa nu avem leakage)
train_base, test_base = train_test_split(df, test_size=0.3, random_state=42)


def este_unghi(col):
    return col.startswith('unghi_')


def axa(col):
    c = col.lower()
    if '_x_' in c:
        return 'x'
    if '_y_' in c:
        return 'y'
    if '_z_' in c:
        return 'z'
    return None


def augment_dataset(base_df, num_perfect, num_uncompleted, num_no_ext):
    new_rows = []
    cols = base_df.columns

    def apply_transformations(row, class_name):
        new_row = row.copy()
        new_row['clasa'] = class_name

        # Variatii spatiale blande (anti-overfitting)
        shift_x = random.uniform(-0.05, 0.05)
        shift_y = random.uniform(-0.05, 0.05)
        scale = random.uniform(0.90, 1.10)

        # Offset temporal mic
        start_frame_offset = random.randint(0, 2)

        # Penalizari (grade)
        uncompleted_penalty = random.uniform(35, 55)   # cotul ramane deschis la varf
        no_ext_penalty = random.uniform(35, 50)        # cotul ramane indoit jos

        for i in range(FRAMES):
            orig_i = min(i + start_frame_offset, FRAMES - 1)

            # Faze in fereastra (simplificat, ca la long_jumps):
            #   varf  = mijloc (contractie, barbia spre bara)
            #   baza  = marginile (atarnat, brate intinse)
            is_top_phase = (10 <= i <= 20)
            is_bottom_phase = (i < 8 or i > 22)

            for col in cols:
                if col in META_COLS or not col.endswith(f'_{i}'):
                    continue

                val_col = col.replace(f'_{i}', f'_{orig_i}')
                val = new_row[val_col]

                if este_unghi(col):
                    # --- UNCOMPLETED: la varf cotul NU se inchide ---
                    if class_name == 'uncompleted' and is_top_phase and 'unghi_cot' in col:
                        val += uncompleted_penalty
                        val = min(val, 175)

                    # --- NO_FULL_EXTENSION: jos cotul ramane indoit ---
                    if class_name == 'no_full_extension' and is_bottom_phase and 'unghi_cot' in col:
                        val -= no_ext_penalty
                        val = max(val, 30)

                    # Zgomot natural fin
                    val += np.random.normal(0, 1.5)
                    new_row[col] = val
                else:
                    # Coordonate normalizate: scalare/shift + zgomot
                    noise = np.random.normal(0, 0.01)
                    a = axa(col)

                    if a == 'x':
                        new_row[col] = 0.5 + (val - 0.5) * scale + shift_x + noise
                    elif a == 'y':
                        new_row[col] = 0.5 + (val - 0.5) * scale + shift_y + noise
                    else:
                        new_row[col] = val + noise

        return new_row

    plan = [
        ('perfect', num_perfect),
        ('uncompleted', num_uncompleted),
        ('no_full_extension', num_no_ext),
    ]

    for class_name, n in plan:
        for _ in range(n):
            idx = random.randint(0, len(base_df) - 1)
            new_rows.append(apply_transformations(base_df.iloc[idx], class_name))

    return pd.DataFrame(new_rows)


print("Generam date de ANTRENARE echilibrate (3x1000)...")
df_train = augment_dataset(train_base, 1000, 1000, 1000)

print("Generam date de TEST echilibrate (3x250)...")
df_test = augment_dataset(test_base, 250, 250, 250)

out_dir = os.path.dirname(os.path.abspath(__file__))
df_train.to_csv(os.path.join(out_dir, 'train_pullup.csv'), index=False)
df_test.to_csv(os.path.join(out_dir, 'test_pullup.csv'), index=False)

print("Gata! train_pullup.csv si test_pullup.csv au fost salvate.")
print(df_train['clasa'].value_counts())
