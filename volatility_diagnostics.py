import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.diagnostic import het_arch
from statsmodels.graphics.tsaplots import plot_acf

# Cargar datos
df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
)

df = df.sort_index()

# Rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()

# Residuo del modelo AR(0): retorno menos media
residuals = returns - returns.mean()

print("Media de los residuos:", residuals.mean())
print("Varianza de los residuos:", residuals.var())

# Residuos al cuadrado
squared_residuals = residuals ** 2

# ACF de residuos al cuadrado
plot_acf(squared_residuals, lags=20)
plt.title("ACF de residuos al cuadrado")
plt.show()

# Prueba ARCH-LM
arch_test = het_arch(residuals)

print("\nPrueba ARCH-LM")
print("LM statistic:", arch_test[0])
print("p-value:", arch_test[1])
