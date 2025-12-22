import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller

# Cargar datos
df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
)

# Asegurar orden temporal
df = df.sort_index()

# Calcular rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()

# Gráfica
returns.plot(title="Rendimientos logarítmicos de Bitcoin")
plt.show()

# Estadísticos descriptivos
print("Estadísticos descriptivos")
print(returns.describe())
print("Curtosis:", returns.kurtosis())
print("Asimetría:", returns.skew())

# Prueba ADF
adf = adfuller(returns)

print("\nPrueba Dickey-Fuller Aumentada")
print("ADF statistic:", adf[0])
print("p-value:", adf[1])
