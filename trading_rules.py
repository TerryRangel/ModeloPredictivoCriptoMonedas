import pandas as pd
import numpy as np

#  Cargar dataset con predicciones ML

df = pd.read_csv(
    "bitcoin_regime_dataset_future_ml.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

#  Preparar Variables

# Retornos en escala decimal
df["return"] = df["return_pct"] / 100.0
# Variación de volatilida
df["vol_change"] = df["volatility"].diff()
# Fuerza de la Tendencia (Para detectar Volatilidad Buena vs Mala)
# Si la media de 20 días es positiva, es "Tendencia Alcista"
df["trend_strength"] = df["return"].rolling(20).mean()

# Señales de Entrada y Salida (Lógica Estable)

df["signal"] = 0 # 0 = Neutro, 1 = Comprar, -1 = Vender
# --- CONDICIÓN DE COMPRA ---
# 1. Régimen actual favorable (0)
# 2. ML no predice crisis futura (!= 2)
# 3. Momentum positivo (ret_5d >= 0)
buy_condition = (
    (df["regime"] == 0) &           # Entorno seguro hoy
    (df["regime_future_ml"] != 2) & # Futuro seguro según IA
    (df["ret_5d"] >= 0)             # Precio subiendo
)
# --- CONDICIÓN DE VENTA ---
# Pánico actual o futuro
sell_condition = (
    (df["regime"] == 2) |
    (df["regime_future_ml"] == 2)
)
df.loc[buy_condition, "signal"] = 1
df.loc[sell_condition, "signal"] = -1

# Mantener posición (llenar huecos)
df["signal"] = df["signal"].replace(0, np.nan).ffill().fillna(0)

# 4VOLATILITY TARGETING DINÁMICO 

# A. Volatilidad Realizada
df["realized_vol"] = df["return"].rolling(24).std()
df["realized_vol"] = df["realized_vol"].clip(lower=0.006)
#  Target Dinámico
df["dynamic_target"] = 0.010  
#  VOLATILIDAD BUENA (Tendencia Positiva -> Acelerar)
df.loc[df["trend_strength"] > 0, "dynamic_target"] = 0.030
#  VOLATILIDAD MALA (Tendencia Negativa -> Frenar
df.loc[df["trend_strength"] <= 0, "dynamic_target"] = 0.001
df["position"] = df["dynamic_target"] / df["realized_vol"]
#  Límites de Seguridad (Sin Deuda)
df["position"] = df["position"].clip(lower=0.0, upper=1.0)
# Aplicar salida
df.loc[df["signal"] <= 0, "position"] = 0.0

# Guardar dataset final
df.to_csv("bitcoin_trading_signals.csv")
# . Diagnóstico (CORREGIDO)

print("=== REGLAS (TARGET DINÁMICO) ===")
print("Estrategia: Acelera en subidas, frena en bajadas.")
print("\nDistribución de señal:")
print(df["signal"].value_counts())
print("\nEstadísticas de Exposición (Position):")
print(df["position"].describe())
print("\nPrimeras filas de control:")
print(df[["regime", "trend_strength", "position"]].head())