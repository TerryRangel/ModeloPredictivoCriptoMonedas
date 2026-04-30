from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import subprocess
import sys

app = FastAPI(title="Centinela API")

# Allow CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------
# DATA LOADING
# -----------------
def load_daily_decisions():
    try:
        df = pd.read_csv("bitcoin_daily_decisions.csv", parse_dates=["Date"])
        df.sort_values(by="Date", inplace=True)
        return df
    except Exception as e:
        print(f"Error loading daily decisions: {e}")
        return None

def load_trading_signals():
    try:
        df = pd.read_csv("bitcoin_trading_signals.csv", parse_dates=["Date"])
        df.sort_values(by="Date", inplace=True)
        return df
    except Exception as e:
        print(f"Error loading trading signals: {e}")
        return None

# -----------------
# SYSTEM ACTIONS
# -----------------
@app.post("/api/actions/retrain")
def action_retrain():
    try:
        subprocess.run([sys.executable, "run.py"], check=True)
        return {"message": "¡Modelo re-entrenado exitosamente!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el re-entrenamiento: {str(e)}")

@app.post("/api/actions/update")
def action_update():
    try:
        subprocess.run([sys.executable, "update_only.py"], check=True)
        return {"message": "¡Datos actualizados exitosamente!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar datos: {str(e)}")

# -----------------
# ENDPOINTS
# -----------------

@app.get("/api/dashboard/current")
def get_current_dashboard():
    df = load_daily_decisions()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Data not found")
    
    ultima_fila = df.iloc[-1]
    
    return {
        "date": ultima_fila["Date"].strftime("%Y-%m-%d"),
        "decision": ultima_fila["decision"],
        "regime": int(ultima_fila["regime"]),
        "volatility": float(ultima_fila["volatility"]),
        "vol_trend_5": float(ultima_fila["vol_trend_5"])
    }

@app.get("/api/dashboard/history")
def get_dashboard_history():
    df = load_daily_decisions()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Data not found")
    
    df_recent = df.tail(100).copy()
    
    history = []
    for _, row in df_recent.iterrows():
        history.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "volatility": float(row["volatility"]),
            "decision": row["decision"],
            "regime": int(row["regime"])
        })
        
    return {"history": history}

@app.get("/api/dashboard/recent-decisions")
def get_recent_decisions():
    df = load_daily_decisions()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Data not found")
    
    df_recent = df.tail(10).copy()
    decisions = []
    for _, row in df_recent.iterrows():
        decisions.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "price": float(row["price"]) if "price" in row and not pd.isna(row["price"]) else 0.0,
            "volatility": float(row["volatility"]),
            "regime": int(row["regime"]),
            "decision": row["decision"]
        })
    decisions.reverse() 
    return {"decisions": decisions}

@app.get("/api/dashboard/all-decisions")
def get_all_decisions():
    df = load_daily_decisions()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Data not found")
    
    decisions = []
    for _, row in df.iterrows():
        decisions.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "price": float(row["price"]) if "price" in row and not pd.isna(row["price"]) else 0.0,
            "volatility": float(row["volatility"]),
            "regime": int(row["regime"]),
            "decision": row["decision"]
        })
    decisions.reverse()
    return {"decisions": decisions}

class SimulationRequest(BaseModel):
    start_date: str
    end_date: str
    initial_capital: float

@app.post("/api/simulator/run")
def run_simulation(req: SimulationRequest):
    df = load_trading_signals()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Trading signals data not found")
        
    mask = (df["Date"] >= req.start_date) & (df["Date"] <= req.end_date)
    sim_data = df.loc[mask].copy()
    
    if sim_data.empty:
        raise HTTPException(status_code=400, detail="No data available for the given date range")
        
    cash_balance = req.initial_capital
    btc_units = 0.0
    
    # Buy and Hold logic
    initial_price = sim_data.iloc[0]["price"]
    buy_hold_btc_units = req.initial_capital / initial_price
    
    equity_curve = []
    trades = []
    last_signal = 0
    
    yearly_stats_dict = {}
    
    # Drawdown tracking (Global)
    peak_equity = req.initial_capital
    peak_bh_equity = req.initial_capital
    max_dd_equity = 0.0
    max_dd_bh = 0.0
    
    for i in range(len(sim_data)):
        row = sim_data.iloc[i]
        date_obj = row["Date"]
        date_str = date_obj.strftime("%Y-%m-%d")
        year_str = str(date_obj.year)
        
        price = row["price"]
        target_risk = row["position"]
        
        current_btc_value = btc_units * price
        total_portfolio = current_btc_value + cash_balance
        
        target_btc_value = total_portfolio * target_risk
        trade_usd = target_btc_value - current_btc_value
        
        buy_hold_value = buy_hold_btc_units * price
        
        # Track peaks and Global Drawdowns
        if total_portfolio > peak_equity: peak_equity = total_portfolio
        if buy_hold_value > peak_bh_equity: peak_bh_equity = buy_hold_value
        
        dd_equity = (peak_equity - total_portfolio) / peak_equity
        dd_bh = (peak_bh_equity - buy_hold_value) / peak_bh_equity
        
        if dd_equity > max_dd_equity: max_dd_equity = dd_equity
        if dd_bh > max_dd_bh: max_dd_bh = dd_bh
        
        action_msg = "Mantener"
        trade_type = "NONE"
        
        if abs(trade_usd) > 10:
            if trade_usd > 0:
                trade_btc = trade_usd / price
                action_msg = f"COMPRA: ${trade_usd:,.0f}"
                trade_type = "BUY"
            else:
                trade_btc = abs(trade_usd) / price
                action_msg = f"VENDE: ${abs(trade_usd):,.0f}"
                trade_type = "SELL"
                
        if row["signal"] == 1 and last_signal != 1:
            action_msg += " [ENTRADA]"
        elif row["signal"] == -1 and last_signal != -1:
            action_msg += " [SALIDA]"
            
        last_signal = row["signal"]
        
        if trade_usd != 0:
            trades.append({
                "date": date_str,
                "price": float(price),
                "target_risk": float(target_risk),
                "total_portfolio": float(total_portfolio),
                "btc_value": float(current_btc_value),
                "cash_value": float(cash_balance),
                "action": action_msg,
                "trade_type": trade_type
            })
        
        equity_curve.append({
            "date": date_str,
            "equity": float(total_portfolio),
            "btc_value": float(target_btc_value), 
            "cash_value": float(total_portfolio - target_btc_value),
            "buy_hold_equity": float(buy_hold_value),
            "dd_equity": float(dd_equity),
            "dd_bh": float(dd_bh)
        })
        
        # Track Yearly Data
        if year_str not in yearly_stats_dict:
            yearly_stats_dict[year_str] = {
                "start_equity": float(total_portfolio),
                "start_bh_equity": float(buy_hold_value),
                "end_equity": float(total_portfolio),
                "end_bh_equity": float(buy_hold_value),
                "max_dd_equity": float(dd_equity),
                "max_dd_bh": float(dd_bh),
                "peak_year_equity": float(total_portfolio),
                "peak_year_bh": float(buy_hold_value)
            }
        else:
            yearly_stats_dict[year_str]["end_equity"] = float(total_portfolio)
            yearly_stats_dict[year_str]["end_bh_equity"] = float(buy_hold_value)
            
            # Yearly Drawdown calculations
            curr_peak_eq = yearly_stats_dict[year_str]["peak_year_equity"]
            curr_peak_bh = yearly_stats_dict[year_str]["peak_year_bh"]
            
            if total_portfolio > curr_peak_eq:
                yearly_stats_dict[year_str]["peak_year_equity"] = float(total_portfolio)
            else:
                yearly_dd = (curr_peak_eq - total_portfolio) / curr_peak_eq
                if yearly_dd > yearly_stats_dict[year_str]["max_dd_equity"]:
                    yearly_stats_dict[year_str]["max_dd_equity"] = float(yearly_dd)
                    
            if buy_hold_value > curr_peak_bh:
                yearly_stats_dict[year_str]["peak_year_bh"] = float(buy_hold_value)
            else:
                yearly_dd_bh = (curr_peak_bh - buy_hold_value) / curr_peak_bh
                if yearly_dd_bh > yearly_stats_dict[year_str]["max_dd_bh"]:
                    yearly_stats_dict[year_str]["max_dd_bh"] = float(yearly_dd_bh)
        
        if trade_usd != 0:
            btc_units += trade_usd / price
            cash_balance -= trade_usd
            
    final_equity = equity_curve[-1]["equity"]
    total_return = (final_equity - req.initial_capital) / req.initial_capital * 100
    
    final_buy_hold = equity_curve[-1]["buy_hold_equity"]
    total_bh_return = (final_buy_hold - req.initial_capital) / req.initial_capital * 100
    
    yearly_stats = []
    for year, stats in yearly_stats_dict.items():
        model_return = ((stats["end_equity"] - stats["start_equity"]) / stats["start_equity"]) * 100
        bh_return = ((stats["end_bh_equity"] - stats["start_bh_equity"]) / stats["start_bh_equity"]) * 100
        yearly_stats.append({
            "year": year,
            "model_return": float(model_return),
            "buy_hold_return": float(bh_return),
            "alpha": float(model_return - bh_return),
            "max_dd_equity": float(stats["max_dd_equity"] * 100),
            "max_dd_bh": float(stats["max_dd_bh"] * 100)
        })
    
    return {
        "summary": {
            "initial_capital": req.initial_capital,
            "final_equity": final_equity,
            "total_return_pct": total_return,
            "final_btc_value": btc_units * sim_data.iloc[-1]["price"],
            "final_cash_value": cash_balance,
            "buy_hold_equity": final_buy_hold,
            "buy_hold_return_pct": total_bh_return,
            "max_drawdown_pct": float(max_dd_equity * 100),
            "max_drawdown_bh_pct": float(max_dd_bh * 100)
        },
        "equity_curve": equity_curve,
        "yearly_stats": yearly_stats,
        "trades": trades[::-1] 
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
