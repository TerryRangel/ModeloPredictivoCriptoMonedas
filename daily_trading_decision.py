import pandas as pd

#  Cargar dataset con señales

df = pd.read_csv(
    "bitcoin_trading_signals.csv",
    parse_dates=["Date"],
    index_col="Date"
).sort_index()


#  Inicializar estado de posición

# 0 = fuera del mercado
# 1 = invertido
position = 0
decisions = []


#  Generar decisión diaria

for date, row in df.iterrows():
    signal = row["signal"]

    if signal == 1 and position == 0:
        decision = "COMPRAR"
        position = 1

    elif signal == -1 and position == 1:
        decision = "SALIR"
        position = 0

    else:
        decision = "MANTENER"

    decisions.append(decision)


#  Guardar decisiones

df["decision"] = decisions

df[[
    "decision",
    "regime",
    "volatility",
    "vol_trend_5",
    "ret_5d"
]].to_csv("bitcoin_daily_decisions.csv")


# 5. Mostrar últimos días

print("\nDECISIONES MÁS RECIENTES")
print("-" * 40)
print(df[[
    "decision",
    "regime",
    "volatility",
    "vol_trend_5",
    "ret_5d"
]].tail(10))
