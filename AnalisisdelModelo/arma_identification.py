import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf

# Cargar datos
df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
)

df = df.sort_index()

# Rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()

print("Número de observaciones:", len(returns))
print("Media:", returns.mean())
print("Varianza:", returns.var())
print("Desviación estándar:", returns.std())

# Calcular ACF y PACF numéricamente
acf_values = acf(returns, nlags=10)
pacf_values = pacf(returns, nlags=10)

print("\nACF (primeros 10 rezagos):")
for i, val in enumerate(acf_values):
    print(f"Lag {i}: {val}")

print("\nPACF (primeros 10 rezagos):")
for i, val in enumerate(pacf_values):
    print(f"Lag {i}: {val}")

# Gráficas
plot_acf(returns, lags=20)
plt.title("ACF de rendimientos de Bitcoin")
plt.show()

plot_pacf(returns, lags=20)
plt.title("PACF de rendimientos de Bitcoin")
plt.show()
