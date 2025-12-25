import pandas as pd
import numpy as np
from arch import arch_model

# Cargar datos
df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
)

df = df.sort_index()

# Rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()

# GARCH trabaja mejor con porcentajes
returns_pct = returns * 100

# Modelo GARCH(1,1) con media constante
model = arch_model(
    returns_pct,
    mean="Constant",
    vol="GARCH",
    p=1,
    q=1,
    dist="skewt"#si es demasiado riesgoso usar normal
)

result = model.fit(disp="off")

print(result.summary())

# Extraer volatilidad condicional
conditional_vol = result.conditional_volatility

print("\nPrimeros valores de volatilidad condicional:")
print(conditional_vol.head())

print("\nÚltimos valores de volatilidad condicional:")
print(conditional_vol.tail())
