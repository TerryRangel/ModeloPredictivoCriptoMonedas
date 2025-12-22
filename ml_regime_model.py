import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# =========================
# 1. Cargar dataset base
# =========================
df = pd.read_csv(
    "bitcoin_regime_dataset.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

# =========================
# 2. Features adicionales necesarias
# =========================
df["vol_change"] = df["volatility"].diff()

# =========================
# 3. Crear target futuro (t + 5)
# =========================
HORIZON = 5
df["regime_future"] = df["regime"].shift(-HORIZON)

# =========================
# 4. Selección de variables
# =========================
features = [
    "return_pct",
    "volatility",
    "shock_std",
    "vol_trend_5",
    "ret_5d",
    "vol_change"
]

target = "regime_future"

df = df.dropna(subset=features + [target])

X = df[features]
y = df[target]

# =========================
# 5. Split temporal
# =========================
train_mask = df.index < "2021-01-01"
test_mask  = df.index >= "2021-01-01"

X_train = X.loc[train_mask]
X_test  = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test  = y.loc[test_mask]

print("Observaciones entrenamiento:", X_train.shape[0])
print("Observaciones test:", X_test.shape[0])

# =========================
# 6. Escalado (solo train)
# =========================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# =========================
# 7. Modelo ML
# =========================
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=7,
    min_samples_leaf=40,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)

# =========================
# 8. Evaluación
# =========================
y_pred = model.predict(X_test_scaled)

print("\nREPORTE DE CLASIFICACIÓN (REGIMEN FUTURO)")
print(classification_report(y_test, y_pred))

print("\nMATRIZ DE CONFUSIÓN")
print(confusion_matrix(y_test, y_pred))

# =========================
# 9. Guardar dataset con régimen futuro ML
# =========================
df.loc[X_test.index, "regime_future_ml"] = y_pred
df["regime_future_ml"] = df["regime_future_ml"].fillna(method="ffill")

df.to_csv("bitcoin_regime_dataset_future_ml.csv")

print("\nDataset con régimen futuro ML guardado correctamente")
