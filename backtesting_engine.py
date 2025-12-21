import pandas as pd
import numpy as np

# 1. Cargar datos
df = pd.read_csv(
    "bitcoin_trading_signals.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()


# 2. Construir retornos correctos

# return_pct está en porcentaje → convertir a decimal
df["return"] = df["return_pct"] / 100.0

# Verificación obligatoria
print("\nVERIFICACIÓN DE RETORNOS (ESCALA DECIMAL)")
print(df["return"].describe())
print("Min:", df["return"].min())
print("Max:", df["return"].max())

#  Definir posición
# 1 = invertido, 0 = fuera
df["position"] = df["signal"].map({1: 1, -1: 0}).fillna(0)


# 4. Retornos de la estrategia
# Entrada al día siguiente de la señal
df["strategy_return"] = df["position"].shift(1) * df["return"]
df["strategy_return"] = df["strategy_return"].fillna(0)

# 5. Curvas de capital
df["equity_market"] = (1 + df["return"]).cumprod()
df["equity_strategy"] = (1 + df["strategy_return"]).cumprod()

# 6. Métricas clave
total_return_strategy = df["equity_strategy"].iloc[-1] - 1
total_return_market = df["equity_market"].iloc[-1] - 1

max_drawdown_strategy = (
    df["equity_strategy"] / df["equity_strategy"].cummax() - 1
).min()

max_drawdown_market = (
    df["equity_market"] / df["equity_market"].cummax() - 1
).min()

days_in_market = int(df["position"].sum())

# 7. Resultados
print("\nRESULTADOS ")
print("-" * 45)
print(f"Retorno total estrategia: {total_return_strategy:.2%}")
print(f"Retorno total mercado:    {total_return_market:.2%}")
print()
print(f"Drawdown máximo estrategia: {max_drawdown_strategy:.2%}")
print(f"Drawdown máximo mercado:    {max_drawdown_market:.2%}")
print()
print(f"Días invertido: {days_in_market} de {len(df)}")
