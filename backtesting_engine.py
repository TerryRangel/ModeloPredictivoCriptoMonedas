import pandas as pd
import numpy as np


# Cargar datos

df = pd.read_csv(
    "bitcoin_trading_signals.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()


#  Construir retornos correctos

# return_pct está en porcentaje → convertir a decimal
df["return"] = df["return_pct"] / 100.0

# Verificación obligatoria
print("\nVERIFICACIÓN DE RETORNOS (ESCALA DECIMAL)")
print(df["return"].describe())
print("Min:", df["return"].min())
print("Max:", df["return"].max())


#  Posición

# position ya existe y representa exposición fraccionaria (0.0 – 1.0)
if "position" not in df.columns:
    raise ValueError("La columna 'position' no existe. Verifica trading_rules.py")


#  Retornos de la estrategia

# Entrada al día siguiente (evita look-ahead bias)
df["strategy_return"] = df["position"].shift(1) * df["return"]
df["strategy_return"] = df["strategy_return"].fillna(0)


# Curvas de capital

df["equity_market"] = (1 + df["return"]).cumprod()
df["equity_strategy"] = (1 + df["strategy_return"]).cumprod()


# . Métricas clave

total_return_strategy = df["equity_strategy"].iloc[-1] - 1
total_return_market = df["equity_market"].iloc[-1] - 1

max_drawdown_strategy = (
    df["equity_strategy"] / df["equity_strategy"].cummax() - 1
).min()

max_drawdown_market = (
    df["equity_market"] / df["equity_market"].cummax() - 1
).min()

# Días efectivamente invertido (exposición > 0)
days_in_market = int((df["position"] > 0).sum())

#  Resultados

print("\nRESULTADOS")
print("-" * 45)
print(f"Retorno total estrategia: {total_return_strategy:.2%}")
print(f"Retorno total mercado:    {total_return_market:.2%}")
print()
print(f"Drawdown máximo estrategia: {max_drawdown_strategy:.2%}")
print(f"Drawdown máximo mercado:    {max_drawdown_market:.2%}")
print()
print(f"Días invertido: {days_in_market} de {len(df)}")
