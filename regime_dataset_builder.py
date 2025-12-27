import pandas as pd
import numpy as np
from arch import arch_model

# Cargar datos

df = pd.read_csv(
    "bitcoin_prices.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

# Rendimientos logarítmicos
returns = np.log(df["price"]).diff().dropna()
returns_pct = returns * 100

#  Ajustar GARCH(1,1)

model = arch_model(
    returns_pct,
    mean="Constant",
    vol="GARCH",
    p=1,
    q=1,
    dist="skewt"#si es demasiado riesgoso usar normal
)
#nota al usar dist="skewt" el modelo captura mejor los eventos extremos y nos ayuda 
#a tener un mejor retorno total aumentando casi por el doble 
#sin aumentar significativamente el drawdown máximo

result = model.fit(disp="off")


#  Extraer variables clave

sigma = result.conditional_volatility
z = result.std_resid

#  Construir dataset base

data = pd.DataFrame({
    "return_pct": returns_pct,
    "volatility": sigma,
    "shock_std": z
})

# Tendencia de volatilidad (media móvil 5 días)
data["vol_trend_5"] = data["volatility"].rolling(5).mean()

# Retorno acumulado corto (5 días)
data["ret_5d"] = data["return_pct"].rolling(5).sum()

data = data.dropna()


#  Definir regímenes por percentiles
min_periods = 365

# Calcular percentiles día a día usando solo información pasada
data['p30_dynamic'] = data['volatility'].expanding(min_periods=min_periods).quantile(0.30)
data['p70_dynamic'] = data['volatility'].expanding(min_periods=min_periods).quantile(0.70)

def classify_regime_dynamic(row):
    # Si no hay suficientes datos aún (primer año), asumimos regimen medio (1) por seguridad
    if pd.isna(row['p30_dynamic']):
        return 1 
        
    if row['volatility'] <= row['p30_dynamic']:
        return 0 # Baja volatilidad (respecto al pasado conocido)
    elif row['volatility'] <= row['p70_dynamic']:
        return 1 # Media
    else:
        return 2 # Alta

data['regime'] = data.apply(classify_regime_dynamic, axis=1)


#  Guardar dataset

data.to_csv("bitcoin_regime_dataset.csv")

print("Dataset de regímenes creado correctamente")
print(data.head())
print("\nDistribución de regímenes:")
print(data["regime"].value_counts())
