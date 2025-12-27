import pandas as pd
import numpy as np

# 1. Cargar datasets
# Necesitamos precios originales para calcular la Media Móvil (SMA)
df_prices = pd.read_csv("bitcoin_prices.csv", parse_dates=["Date"], index_col="Date").sort_index()
df = pd.read_csv("bitcoin_regime_dataset_future_ml.csv", parse_dates=["Date"], index_col="Date").sort_index()

# Unir precio al dataset principal si no está
if "price" not in df.columns:
    df = df.join(df_prices["price"], how="left")

# 2. CALCULAR INDICADORES DE TENDENCIA (LA CLAVE DEL ÉXITO)
# SMA 50: Filtro de tendencia de mediano plazo
df["sma_50"] = df["price"].rolling(window=50).mean()
# Distancia al SMA (Positiva = Tendencia Alcista, Negativa = Bajista)
df["trend_dist"] = (df["price"] - df["sma_50"]) / df["sma_50"]


# 3. Preparar Variables Base
df["return"] = df["return_pct"] / 100.0
df["vol_change"] = df["volatility"].diff()
df["trend_strength"] = df["return"].rolling(20).mean() # Momentum corto


# ==============================================================================
# LÓGICA DE SEÑALES (FILTRO DE TENDENCIA + ML)
# ==============================================================================

df["signal"] = 0 # 0 = Neutro, 1 = Comprar, -1 = Vender

# --- CONDICIÓN DE COMPRA ROBUSTA ---
# 1. Régimen: Aceptamos Volatilidad Baja (0) y Media (1)
# 2. ML: El modelo no predice crisis futura (!= 2)
# 3. TENDENCIA (NUEVO): EL PRECIO DEBE ESTAR SOBRE LA MEDIA DE 50 DÍAS
#    Esto nos salva de los mercados bajistas de 2018 y 2022.

buy_condition = (
    (df["regime"] <= 1) &           # Entorno de volatilidad aceptable
    (df["regime_future_ml"] != 2) & # IA dice que es seguro
    (df["price"] > df["sma_50"])    # <--- FILTRO MAESTRO: Solo operar en tendencia alcista
)

# --- CONDICIÓN DE VENTA ---
# Salir si:
# 1. Entramos en régimen de pánico (2)
# 2. La IA predice pánico
# 3. Perdemos la tendencia (El precio cruza abajo de la SMA 50)
sell_condition = (
    (df["regime"] == 2) |
    (df["regime_future_ml"] == 2) |
    (df["price"] < df["sma_50"])    # <--- SALIDA RÁPIDA si la tendencia se rompe
)

df.loc[buy_condition, "signal"] = 1
df.loc[sell_condition, "signal"] = -1


# --- FRENO DE EMERGENCIA (Crash Protection) ---
# Se mantiene por seguridad para "Flash Crashes" que ocurren ENCIMA de la SMA
rolling_3d_ret = df["return"].rolling(3).sum()
vol_threshold = df["volatility"] * -3.0 
emergency_exit = (rolling_3d_ret < vol_threshold)
df.loc[emergency_exit, "signal"] = -1


# Llenar huecos
df["signal"] = df["signal"].replace(0, np.nan).ffill().fillna(0)


# ==============================================================================
# GESTIÓN DE RIESGO (VOLATILITY TARGETING)
# ==============================================================================

df["realized_vol"] = df["return"].rolling(24).std()
df["realized_vol"] = df["realized_vol"].clip(lower=0.006)

# Target Base
df["dynamic_target"] = 0.010

# Si la tendencia es MUY fuerte (Precio > 10% sobre SMA 50), aumentamos apuesta
# Esto nos permite ganar más en los "Bull Runs" como 2020-2021
strong_uptrend = (df["trend_dist"] > 0.10)
df.loc[strong_uptrend, "dynamic_target"] = 0.035 # Aumentamos agresividad en subida libre

# Si estamos cerca de perder la media (Precio < 2% sobre SMA), reducimos riesgo
weak_uptrend = (df["trend_dist"] < 0.02)
df.loc[weak_uptrend, "dynamic_target"] = 0.005 


df["position"] = df["dynamic_target"] / df["realized_vol"]
df["position"] = df["position"].clip(lower=0.0, upper=1.0)
df.loc[df["signal"] <= 0, "position"] = 0.0


# Guardar
df.to_csv("bitcoin_trading_signals.csv")

print("=== REGLAS ACTUALIZADAS (CON FILTRO SMA 50) ===")
print("1. Filtro de Tendencia: Solo compra si Precio > SMA 50.")
print("2. Crash Protection: Activo.")
print("3. Target Dinámico: Agresivo en subida libre, conservador cerca de la media.")
print("\nEstadísticas de Exposición:")
print(df["position"].describe())