import pandas as pd
import matplotlib.pyplot as plt
import sys

def run_split_simulation():
    print("==================================================================================")
    print("   SIMULADOR DESGLOSADO: BITCOIN vs DÓLARES (CONTROL TOTAL)   ")
    print("==================================================================================")


    # 1. CARGAR DATOS
    try:
        df = pd.read_csv(
            "bitcoin_trading_signals.csv", 
            parse_dates=["Date"], 
            index_col="Date"
        ).sort_index()
    except FileNotFoundError:
        print("\n[ERROR] Falta 'bitcoin_trading_signals.csv'. Ejecuta run.py primero.")
        return

    # 2. CONFIGURACIÓN
    min_date = df.index.min().strftime('%Y-%m-%d')
    max_date = df.index.max().strftime('%Y-%m-%d')
    print(f"Rango disponible: {min_date} al {max_date}")

    start_date = input(f"Fecha inicio [Enter para {min_date}]: ") or min_date
    end_date = input(f"Fecha fin    [Enter para {max_date}]: ") or max_date
    initial_capital = float(input("Capital inicial USD [Default 10000]: ") or 10000)

    sim_data = df.loc[(df.index >= start_date) & (df.index <= end_date)].copy()
    if sim_data.empty: return

    # 3. INICIALIZACIÓN DE BILLETERAS
    # Empezamos 100% en Dólares (Cash)
    cash_balance = initial_capital
    btc_units = 0.0
    
    equity_curve = []
    
    print(f"\nIniciando con ${initial_capital:,.2f} USD...")
    print("-" * 155)
    # Encabezados con desglose claro
    header = f"{'FECHA':<11} | {'PRECIO':<8} | {'RIESGO':<6} | {' TOTAL (USD)':<14} | {' EN BITCOIN ($)':<18} | {' EN DÓLARES ($)':<18} | {'ORDEN DE TRADING'}"
    print(header)
    print("-" * 155)

    last_signal = 0 

    for i in range(len(sim_data)):
        date = sim_data.index[i]
        row = sim_data.iloc[i]
        price = row["price"]
        target_risk = row["position"] # % que deberíamos tener en BTC hoy
        
      
        current_btc_value = btc_units * price
        total_portfolio = current_btc_value + cash_balance
        equity_curve.append(total_portfolio)

        target_btc_value = total_portfolio * target_risk
        
        trade_usd = target_btc_value - current_btc_value
        
        action_msg = ""
        color = ""
        
        if abs(trade_usd) > 10: # Filtro de ruido ($10 usd)
            if trade_usd > 0:
                trade_btc = trade_usd / price
                action_msg = f"🟢 COMPRA: ${trade_usd:,.0f} ({trade_btc:.4f} BTC)"
                color = "\033[92m" # Verde
            else:
                trade_btc = abs(trade_usd) / price
                action_msg = f"🔴 VENDE:  ${abs(trade_usd):,.0f} ({trade_btc:.4f} BTC)"
                color = "\033[91m" # Rojo
        else:
            action_msg = "⚪ Mantener"
            color = "\033[90m" # Gris

        # Señales Fuertes (Cambio de tendencia)
        if row["signal"] == 1 and last_signal != 1:
            action_msg += " [ENTRADA]"
        elif row["signal"] == -1 and last_signal != -1:
            action_msg += " [SALIDA]"
            
        last_signal = row["signal"]

       
        print(f"{date.date()} | ${price:<7.0f} | {target_risk:>4.0%}   | ${total_portfolio:<13,.0f} | ${current_btc_value:<16,.0f} | ${cash_balance:<16,.0f} | {color}{action_msg}\033[0m")

        
        if trade_usd != 0:
            btc_units += trade_usd / price
            cash_balance -= trade_usd

   
    final_equity = equity_curve[-1]
    total_return = (final_equity - initial_capital) / initial_capital * 100
    
    print("-" * 155)
    print(f"CAPITAL FINAL: ${final_equity:,.2f}  (Retorno: {total_return:.2f}%)")
    print(f"Desglose Final -> Bitcoin: ${btc_units*price:,.2f} | Dólares: ${cash_balance:,.2f}")

    
    sim_data["Equity"] = equity_curve
   
    sim_data["BTC_Value"] = sim_data["Equity"] * sim_data["position"]
    sim_data["Cash_Value"] = sim_data["Equity"] * (1 - sim_data["position"])

    plt.figure(figsize=(12, 6))
    plt.stackplot(sim_data.index, sim_data["Cash_Value"], sim_data["BTC_Value"], 
                  labels=["En Dólares (Cash)", "En Bitcoin"], colors=["#85bb65", "orange"], alpha=0.6)
    plt.plot(sim_data.index, sim_data["Equity"], color="black", linewidth=1, label="Total")
    
    plt.title("Composición de tu Portafolio (Bitcoin vs Dólares)")
    plt.legend(loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    run_split_simulation()