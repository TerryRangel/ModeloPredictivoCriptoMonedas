import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# 1. Cargar dataset base
print("Cargando datos...")
df = pd.read_csv(
    "bitcoin_regime_dataset.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

# Features adicionales
df["vol_change"] = df["volatility"].diff()

# 2. Crear target futuro (t + 5)
HORIZON = 5
df["regime_future"] = df["regime"].shift(-HORIZON)

# 3. Selección de variables
features = [
    "return_pct",
    "volatility",
    "shock_std",
    "vol_trend_5",
    "ret_5d",
    "vol_change"
]
target = "regime_future"

# Limpiar NaNs iniciales
df_clean = df.dropna(subset=features + [target]).copy()


# AQUÍ ESTÁ LA CORRECCIÓN: WALK-FORWARD VALIDATION- en el modelo anterior se usaba "train_test_split" que mezcla datos futuros con pasados de  esta manera podemos tener un modelo más realista que simula cómo se comportaría en producción


# Configuración
initial_train_years = 2  # Necesitamos al menos 2 años de historia para empezar
start_year = df_clean.index.year.min() + initial_train_years
final_year = df_clean.index.year.max()

print(f"\nIniciando Walk-Forward Validation...")
print(f"El modelo empezará a predecir desde el año: {start_year}")
print("(Los años anteriores se usan solo para aprender inicialmenten y no tendrán predicción)")

# Contenedor para las predicciones alineadas por fecha
all_predictions = pd.Series(index=df_clean.index, dtype=float)
all_predictions[:] = np.nan  # Llenar de NaNs al inicio

# Bucle Año por Año (Simulando la realidad)
for year in range(start_year, final_year + 1):
    
    # A. DEFINIR VENTANAS TEMPORALES
    # Entrenamiento: Desde el inicio de los tiempos hasta el año anterior (Expanding Window)
    # Ejemplo: Si estamos prediciendo 2018, entrenamos con 2015, 2016, 2017. - asi como si en 2019 usamos 2015-2018  y asi sucesivamente
    train_mask = df_clean.index.year < year
    
    # Test: El año actual que queremos operar
    test_mask = df_clean.index.year == year
    
    # Validar que tengamos datos
    if not any(train_mask) or not any(test_mask):
        continue

    X_train = df_clean.loc[train_mask, features]
    y_train = df_clean.loc[train_mask, target]
    
    X_test = df_clean.loc[test_mask, features]
    
    # B. ESCALADO (¡Importante!: Fit solo en train, Transform en test)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # C. ENTRENAR MODELO (El modelo "olvida" el futuro, solo ve el pasado)
    model = RandomForestClassifier(
        n_estimators=200,    # Reducido un poco para velocidad
        max_depth=5,         # Menos profundidad para evitar overfitting rápido
        min_samples_leaf=20, 
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # D. PREDECIR EL AÑO ACTUAL
    preds = model.predict(X_test_scaled)
    
    # Guardar predicciones en las fechas correspondientes
    all_predictions.loc[test_mask] = preds
    
    print(f"Año {year}: Entrenado con {len(X_train)} días. Predicho para {len(X_test)} días.")

# ==============================================================================

# 4. Guardar resultados
# Asignamos la columna. Los primeros años (2015-2016) quedarán vacíos (NaN).
# Esto es CORRECTO: No puedes operar en 2015 si necesitas datos de 2015 para aprender.
df["regime_future_ml"] = all_predictions

# Llenamos los NaNs iniciales con un valor neutro (ej. 1) o "Peligro" (2) para no operar a ciegas
# Sugerencia: Llenar con 2 (Alta Volatilidad) para que el bot NO opere hasta tener predicciones reales.
df["regime_future_ml"] = df["regime_future_ml"].fillna(2)

df.to_csv("bitcoin_regime_dataset_future_ml.csv")

print("\nDataset guardado correctamente.")
print("Nota: Los primeros años tendrán 'regime_future_ml = 2' para evitar operar sin modelo entrenado.")
print(df[["regime_future_ml"]].tail())