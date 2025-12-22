import yfinance as yf
import pandas as pd

btc = yf.download(
    tickers="BTC-USD",
    start="2020-01-01",
    progress=False
)

btc = btc[["Close"]]
btc.columns = ["price"]

btc.to_csv("bitcoin_prices.csv")

print("Datos descargados correctamente")
print(btc.head())
print(btc.tail())
