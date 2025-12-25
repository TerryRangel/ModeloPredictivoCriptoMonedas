import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# . Cargar dataset base

df = pd.read_csv(
    "bitcoin_regime_dataset.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

# 2. Features adicionales
df["vol_change"] = df["volatility"].diff()


# 3. Crear target futuro (t + 5)
HORIZON = 5
df["regime_future"] = df["regime"].shift(-HORIZON)

# 4. Selección de variables

features = [
    "return_pct",
    "volatility",
    "shock_std",
    "vol_trend_5",
    "ret_5d",
    "vol_change"
]

target = "regime_future"

df_train_valid = df.dropna(subset=features + [target]).copy()
df = df.dropna(subset=features) 

X = df_train_valid[features]
y = df_train_valid[target]


# Split temporal (Solo para validar calidad)

split_date = "2023-01-01"
train_mask = df_train_valid.index < split_date
test_mask  = df_train_valid.index >= split_date

X_train = X.loc[train_mask]
X_test  = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test  = y.loc[test_mask]

print(f"Entrenamiento: {X_train.shape[0]} muestras")
print(f"Validación:    {X_test.shape[0]} muestras")

#  Escalado

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

X_all_scaled = scaler.transform(df[features])
X_test_scaled = scaler.transform(X_test) # Solo para reporte de métricas


#  Modelo ML

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=7,
    min_samples_leaf=40,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)


# Evaluación (Solo sobre datos pasados conocidos)

y_pred_test = model.predict(X_test_scaled)

print("\nREPORTE DE CLASIFICACIÓN (VALIDACIÓN HISTÓRICA)")
print(classification_report(y_test, y_pred_test))


#  Guardar dataset con predicción 

# Predecimos sobre todo 'df'
all_predictions = model.predict(X_all_scaled)
df["regime_future_ml"] = all_predictions

# Guardamos
df.to_csv("bitcoin_regime_dataset_future_ml.csv")

print("\nDataset guardado. .")
print("Últimas 5 predicciones :")
print(df[["regime_future_ml"]].tail(5))