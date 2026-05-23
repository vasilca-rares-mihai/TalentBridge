import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split

df = pd.read_csv('dataset_squats.csv')
frames = 30

# Referinta pentru cadru 0
stand_row = df.iloc[0]
standing_dict = {col: stand_row[col.replace(col.split('_')[-1], '0')] for col in df.columns if
                 col not in ['clip', 'clasa', 'window_id']}

# Impartim baza
train_base, test_base = train_test_split(df, test_size=0.3, random_state=42)


def augment_dataset(base_df, num_perfect, num_incomplete, num_arched):
    new_rows = []

    def apply_transformations(row, class_name):
        new_row = row.copy()
        new_row['clasa'] = class_name

        # 1. Shiftari masive
        shift_x = random.uniform(-0.15, 0.15)
        shift_y = random.uniform(-0.15, 0.15)

        # 2. Scalare (de la pitic la urias, foarte aproape de camera sau f departe)
        scale = random.uniform(0.65, 1.35)

        # 3. Definim viteza executiei (asincronicitate / phase shift)
        # Alegem un cadru random de start (ca sa nu inceapa mereu din picioare)
        start_frame_offset = random.randint(0, 5)

        # 4. Factori aleatorii, neliniari pt erori
        inc_factor = random.uniform(0.15, 0.65) if class_name == 'incomplete' else 1.0
        arched_aggressiveness = random.uniform(0.4, 1.5)  # cat de cocosat e

        for i in range(frames):
            # Cautam frame-ul original decalat
            orig_i = min(i + start_frame_offset, frames - 1)

            orig_knee = new_row[f'unghi_genunchi_l_{orig_i}']
            depth_ratio = max(0, min(1, (175 - orig_knee) / (175 - 60)))

            # Calculam distorsiunile de arched_back *bazate pe o curba neliniara (patratica)*
            arched_shift_x = random.uniform(0.15, 0.40) * (
                        depth_ratio ** arched_aggressiveness) if class_name == 'arched_back' else 0
            arched_angle_drop = random.uniform(30, 70) * (
                        depth_ratio ** arched_aggressiveness) if class_name == 'arched_back' else 0

            for col in base_df.columns:
                if col not in ['clip', 'clasa', 'window_id'] and col.endswith(f'_{i}'):

                    # Luam valoarea din frame-ul decalat temporal
                    val_col = col.replace(f'_{i}', f'_{orig_i}')
                    val = new_row[val_col]

                    # Distorsiunea pentru INCOMPLETE (trunchiem miscarea)
                    if class_name == 'incomplete':
                        stand_val = standing_dict[col.replace(f'_{i}', '_0')]
                        # Amestecam partial cu pozitia de stand
                        val = stand_val + inc_factor * (val - stand_val)

                    # ZGOMOT si MODIFICARI FINALE
                    if 'unghi' in col:
                        # Zgomot extrem (tremura picioarele de oboseala / unghiuri prost calculate de MediaPipe)
                        noise = np.random.normal(0, 7.5)  # pana la 7.5 grade!

                        if class_name == 'arched_back' and 'unghi_sold' in col:
                            val -= arched_angle_drop

                        # Daca genoflexiunea e perfecta, uneori mai adaugam niste mici nereguli sa nu fie prea perfecta
                        if class_name == 'perfect' and random.random() < 0.1:
                            val += random.uniform(-10, 10)

                        new_row[col] = val + noise

                    else:
                        # Zgomot pe puncte (coordonate)
                        noise = np.random.normal(0, 0.04)  # zgomot urias pe pixeli

                        if '_x_' in col:
                            if class_name == 'arched_back' and 'shoulder_x' in col:
                                val -= arched_shift_x
                            new_row[col] = 0.5 + (val - 0.5) * scale + shift_x + noise
                        elif '_y_' in col:
                            new_row[col] = 0.5 + (val - 0.5) * scale + shift_y + noise
                        else:
                            new_row[col] = val + noise
        return new_row

    for _ in range(num_perfect):
        idx = random.randint(0, len(base_df) - 1)
        new_rows.append(apply_transformations(base_df.iloc[idx], 'perfect'))
    for _ in range(num_incomplete):
        idx = random.randint(0, len(base_df) - 1)
        new_rows.append(apply_transformations(base_df.iloc[idx], 'incomplete'))
    for _ in range(num_arched):
        idx = random.randint(0, len(base_df) - 1)
        new_rows.append(apply_transformations(base_df.iloc[idx], 'arched_back'))

    return pd.DataFrame(new_rows)


print("Generam date TRAIN AGRESIV izolate...")
df_train = augment_dataset(train_base, 800, 800, 800)  # 2400 raduri train
print("Generam date TEST AGRESIV izolate...")
df_test = augment_dataset(test_base, 200, 200, 200)  # 600 randuri test

df_train.to_csv('train_squats.csv', index=False)
df_test.to_csv('test_squats.csv', index=False)
print("Fisierele 'train_squats.csv' si 'test_squats.csv' au fost salvate cu un nivel de zgomot INTENS!")