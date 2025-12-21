

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# Cargar datos
df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
)

df = df.sort_index()

# Rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()

models = {
    "AR(0)": ARIMA(returns, order=(0, 0, 0)),
    "AR(1)": ARIMA(returns, order=(1, 0, 0)),
    "ARMA(1,1)": ARIMA(returns, order=(1, 0, 1))
}

results = {}

for name, model in models.items():
    fitted = model.fit()
    results[name] = {
        "AIC": fitted.aic,
        "BIC": fitted.bic
    }
    print(f"\nModelo: {name}")
    print(f"AIC: {fitted.aic}")
    print(f"BIC: {fitted.bic}")
