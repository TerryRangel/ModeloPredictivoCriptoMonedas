import pandas as pd
import numpy as np

# =========================
# 1. Cargar dataset de regímenes
# =========================
df = pd.read_csv(
    "bitcoin_regime_dataset.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

# =========================
# 2. Variación de volatilidad
# =========================
df["vol_change"] = df["volatility"].diff()

# =========================
# 3. Inicializar señal
# =========================
df["signal"] = 0  # Neutro por defecto

# =========================
# 4. Regla de COMPRA / MANTENER
# =========================
buy_condition = (
    (df["regime"] == 0) &
    (df["vol_change"] <= 0) &
    (df["ret_5d"] >= 0)
)

df.loc[buy_condition, "signal"] = 1

# =========================
# 5. Regla de SALIDA
# =========================
sell_condition = (
    (df["regime"] == 2) |
    (df["vol_change"] > df["volatility"].rolling(5).std())
)

df.loc[sell_condition, "signal"] = -1

# =========================
# 6. Guardar señales
# =========================
df.to_csv("bitcoin_trading_signals.csv")

print("Reglas de trading aplicadas correctamente")
print("\nDistribución de señales:")
print(df["signal"].value_counts())
print("\nPrimeras filas:")
print(df[["return_pct", "volatility", "regime", "signal"]].head())
