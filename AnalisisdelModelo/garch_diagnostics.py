import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import het_arch

# Cargar datos
df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
)

df = df.sort_index()

# Rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()
returns_pct = returns * 100

# Ajustar GARCH(1,1)
model = arch_model(
    returns_pct,
    mean="Constant",
    vol="GARCH",
    p=1,
    q=1,
    dist="normal"
)

result = model.fit(disp="off")

# Residuos estandarizados
std_resid = result.std_resid

print("Media de residuos estandarizados:", std_resid.mean())
print("Varianza de residuos estandarizados:", std_resid.var())

# ACF de residuos estandarizados
plot_acf(std_resid, lags=20)
plt.title("ACF de residuos estandarizados")
plt.show()

# ACF de residuos estandarizados al cuadrado
plot_acf(std_resid ** 2, lags=20)
plt.title("ACF de residuos estandarizados al cuadrado")
plt.show()

# Prueba ARCH-LM sobre residuos estandarizados
arch_test = het_arch(std_resid)

print("\nPrueba ARCH-LM sobre residuos estandarizados")
print("LM statistic:", arch_test[0])
print("p-value:", arch_test[1])
