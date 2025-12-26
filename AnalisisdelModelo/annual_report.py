import pandas as pd
import numpy as np

# Cargar las señales y preparar datos
df = pd.read_csv(
    "../bitcoin_trading_signals.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()

# Convertir porcentaje a decimal si es necesario
if "return_pct" in df.columns:
    df["return"] = df["return_pct"] / 100.0

# Calcular retorno de estrategia (con shift para evitar mirar al futuro)
df["strategy_return"] = df["position"].shift(1) * df["return"]
df["strategy_return"] = df["strategy_return"].fillna(0)

#  Función para calcular métricas de un periodo
def calculate_metrics(series):
    # Retorno Total Compuesto
    total_return = (1 + series).prod() - 1
    
    # Curva de capital para Drawdown
    equity_curve = (1 + series).cumprod()
    drawdown = (equity_curve / equity_curve.cummax()) - 1
    max_dd = drawdown.min()
    
    return total_return, max_dd

# Agrupar por año y calcular
years = df.index.year.unique()
report_data = []

print(f"{'AÑO':<6} | {'ESTRATEGIA':<12} | {'MERCADO':<12} | {'DIFF':<10} | {'DD ESTRAT.':<12} | {'DD MERCADO':<12}")
print("-" * 85)

for year in years:
    # Filtrar datos del año
    df_year = df[df.index.year == year]
    
    # Calcular métricas
    strat_ret, strat_dd = calculate_metrics(df_year["strategy_return"])
    mkt_ret, mkt_dd = calculate_metrics(df_year["return"])
    
    # Diferencia (Alpha)
    diff = strat_ret - mkt_ret
    
    # Guardar para análisis
    report_data.append({
        "Año": year,
        "Estrategia %": strat_ret,
        "Mercado %": mkt_ret,
        "Diferencia": diff,
        "Max DD Estrategia": strat_dd,
        "Max DD Mercado": mkt_dd
    })
    
    # Imprimir fila formateada
    print(f"{year:<6} | {strat_ret:>10.2%}   | {mkt_ret:>10.2%}   | {diff:>8.2%}   | {strat_dd:>10.2%}   | {mkt_dd:>10.2%}  ")

print("-" * 85)


df_report = pd.DataFrame(report_data).set_index("Año")
df_report.to_csv("reporte_anual.csv")