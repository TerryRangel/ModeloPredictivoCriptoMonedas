import pandas as pd
import numpy as np
#  Cargar dataset con régimen futuro ML

df = pd.read_csv(
    "bitcoin_regime_dataset_future_ml.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

#  Retornos en escala decimal
df["return"] = df["return_pct"] / 100.0
#  Variación de volatilidad
df["vol_change"] = df["volatility"].diff()
# señal base (direccional)

df["signal"] = 0

buy_condition = (
    (df["regime"] == 0) &                     # Régimen actual favorable
    (df["regime_future_ml"] != 2) &           # No se anticipa crisis
    #(df["vol_change"] <= 0) &                 # Volatilidad contenida
    (df["ret_5d"] >= 0)                       # Momentum positivo
)

sell_condition = (
    (df["regime"] == 2) |                     # Régimen actual adverso
    (df["regime_future_ml"] == 2)             # Régimen futuro adverso
)

df.loc[buy_condition, "signal"] = 1
df.loc[sell_condition, "signal"] = -1

# Mantener posición (clásico)
df["signal"] = df["signal"].replace(0, np.nan).ffill().fillna(0)
#  VOLATILITY TARGETING (CLAVE DEL CONTROL DE DD)
# Volatilidad realizada (20 días)
df["realized_vol"] = df["return"].rolling(20).std()

# Piso de volatilidad para evitar apalancamiento extremo
df["realized_vol"] = df["realized_vol"].clip(lower=0.006)

# Target de riesgo diario (CONSERVADOR)
TARGET_VOL = 0.018   # 1.8% diario → enfocado en drawdown

# Posición dinámica
df["position"] = TARGET_VOL / df["realized_vol"]

# Límites estrictos de exposición
df["position"] = df["position"].clip(lower=0.0, upper=1.3)

# Aplicar señal direccional
df.loc[df["signal"] <= 0, "position"] = 0.0
# 6. Guardar dataset final
df.to_csv("bitcoin_trading_signals.csv")

# 7. Diagnóstico mínimo

print("Reglas de trading con control de drawdown aplicadas correctamente\n")
print("Distribución de señal:")
print(df["signal"].value_counts(), "\n")
print("Distribución de exposición:")
print(df["position"].describe(), "\n")
print("Primeras filas:")
print(df[["regime", "regime_future_ml", "realized_vol", "position"]].head())
