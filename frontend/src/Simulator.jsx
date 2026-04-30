import React, { useState } from 'react';
import axios from 'axios';
import { AreaChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Play, Info, ShieldAlert } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

export default function Simulator() {
  const [startDate, setStartDate] = useState('2022-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [capital, setCapital] = useState(10000);
  
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runSimulation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await axios.post(`${API_URL}/simulator/run`, {
        start_date: startDate,
        end_date: endDate,
        initial_capital: parseFloat(capital)
      });
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al ejecutar la simulación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      <div className="glass-panel" style={{ borderTop: '4px solid var(--accent-blue)' }}>
        <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldAlert size={24} color="var(--accent-blue)" /> 
          Perfil: Modelo Defensivo
        </h2>
        <div className="info-box" style={{ marginBottom: '2rem', borderLeftColor: 'var(--accent-green)', backgroundColor: 'rgba(0, 208, 132, 0.05)' }}>
          <strong>🛡️ ¿Qué es un Modelo Defensivo?</strong> Este sistema cuantitativo no está diseñado para multiplicar tu dinero agresivamente en mercados alcistas, sino para <strong>preservar tu capital en los mercados bajistas (Bear Markets)</strong>. 
          Su objetivo principal es mantener la <strong>Máxima Caída (Max Drawdown)</strong> lo más pequeña posible comparada con simplemente comprar y mantener Bitcoin (Hold). Al perder menos, el interés compuesto a largo plazo funciona a tu favor.
        </div>
        
        <form onSubmit={runSimulation} style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Fecha de Inicio</label>
            <input 
              type="date" 
              className="form-control" 
              value={startDate} 
              onChange={e => setStartDate(e.target.value)}
              required 
            />
          </div>
          
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Fecha de Fin</label>
            <input 
              type="date" 
              className="form-control" 
              value={endDate} 
              onChange={e => setEndDate(e.target.value)}
              required 
            />
          </div>
          
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Capital Inicial (USD)</label>
            <input 
              type="number" 
              className="form-control" 
              value={capital} 
              onChange={e => setCapital(e.target.value)}
              min="100"
              required 
            />
          </div>
          
          <button type="submit" className="btn-primary" disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Play size={18} />
            {loading ? 'Simulando...' : 'Ejecutar'}
          </button>
        </form>
        
        {error && <div style={{ color: 'var(--accent-red)', marginTop: '1rem' }}>{error}</div>}
      </div>

      {results && (
        <>
          <div className="kpi-grid animate-fade-in">
            <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
              <span className="kpi-label" title="Capital total al final del periodo usando tu modelo.">Capital Final (Modelo) <Info size={12}/></span>
              <span className="kpi-value">${results.summary.final_equity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
            </div>
            <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
              <span className="kpi-label" title="Porcentaje de ganancia o pérdida usando tu modelo.">Retorno (Modelo) <Info size={12}/></span>
              <span className={`kpi-value ${results.summary.total_return_pct >= 0 ? 'status-green' : 'status-red'}`}>
                {results.summary.total_return_pct.toFixed(2)}%
              </span>
            </div>
            
            {/* Nuevos KPIs de Drawdown */}
            <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid var(--accent-red)' }}>
              <span className="kpi-label" title="La caída más fuerte que sufrió tu capital desde su punto más alto (Riesgo del Modelo).">Max Drawdown (Modelo) <Info size={12}/></span>
              <span className="kpi-value status-red">
                -{results.summary.max_drawdown_pct.toFixed(2)}%
              </span>
            </div>
            <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid var(--text-muted)' }}>
              <span className="kpi-label" title="La caída más fuerte que hubieras sufrido haciendo Buy & Hold.">Max Drawdown (Hold) <Info size={12}/></span>
              <span className="kpi-value" style={{ color: 'var(--text-muted)' }}>
                -{results.summary.max_drawdown_bh_pct.toFixed(2)}%
              </span>
            </div>
          </div>

          <div className="glass-panel animate-fade-in">
            <h2>Comparación de Rendimiento</h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={results.equity_curve} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" stroke="#8b9bb4" tick={{fill: '#8b9bb4', fontSize: 12}} />
                  <YAxis stroke="#8b9bb4" tick={{fill: '#8b9bb4', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(20, 26, 42, 0.95)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                    itemStyle={{ color: '#fff', padding: '4px 0' }}
                    formatter={(value) => `$${value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                  <Area type="monotone" dataKey="cash_value" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.4} name="En Dólares (Modelo)" />
                  <Area type="monotone" dataKey="btc_value" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} name="En Bitcoin (Modelo)" />
                  <Line type="monotone" dataKey="buy_hold_equity" stroke="#f59e0b" strokeWidth={3} dot={false} name="Buy & Hold (Referencia)" strokeDasharray="5 5" />
                  <Line type="monotone" dataKey="equity" stroke="#ffffff" strokeWidth={2} dot={false} name="Capital Total (Modelo)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Tabla de Estadísticas por Año Mejorada */}
            <div className="glass-panel animate-fade-in" style={{ gridColumn: 'span 2' }}>
              <h2>Estadísticas Detalladas por Año</h2>
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Año</th>
                      <th>Retorno Modelo</th>
                      <th>Retorno Buy & Hold</th>
                      <th>Diferencia (Alpha)</th>
                      <th style={{ color: 'var(--accent-red)' }}>Drawdown Modelo</th>
                      <th style={{ color: 'var(--accent-red)' }}>Drawdown Hold</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.yearly_stats.map((stat, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: 'bold' }}>{stat.year}</td>
                        <td className={stat.model_return >= 0 ? 'status-green' : 'status-red'}>{stat.model_return.toFixed(2)}%</td>
                        <td className={stat.buy_hold_return >= 0 ? 'status-orange' : 'status-red'}>{stat.buy_hold_return.toFixed(2)}%</td>
                        <td className={stat.alpha > 0 ? 'status-green' : 'status-red'} style={{ fontWeight: 'bold' }}>
                          {stat.alpha > 0 ? '+' : ''}{stat.alpha.toFixed(2)}%
                        </td>
                        <td style={{ color: 'var(--accent-red)' }}>-{stat.max_dd_equity.toFixed(2)}%</td>
                        <td style={{ color: 'var(--text-muted)' }}>-{stat.max_dd_bh.toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="glass-panel animate-fade-in" style={{ marginTop: '2rem' }}>
            <h2>Registro de Transacciones</h2>
            <div style={{ overflowX: 'auto', maxHeight: '500px' }}>
              <table className="data-table">
                <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--panel-bg)', zIndex: 1, backdropFilter: 'blur(10px)' }}>
                  <tr>
                    <th>Fecha</th>
                    <th>Precio BTC</th>
                    <th>Riesgo</th>
                    <th>Total (USD)</th>
                    <th>En Bitcoin</th>
                    <th>En Dólares</th>
                    <th>Orden de Trading</th>
                  </tr>
                </thead>
                <tbody>
                  {results.trades.map((trade, i) => (
                    <tr key={i}>
                      <td>{trade.date}</td>
                      <td>${trade.price.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                      <td>{(trade.target_risk * 100).toFixed(0)}%</td>
                      <td>${trade.total_portfolio.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                      <td>${trade.btc_value.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                      <td>${trade.cash_value.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                      <td style={{ 
                        color: trade.trade_type === 'BUY' ? 'var(--accent-green)' : 
                               trade.trade_type === 'SELL' ? 'var(--accent-red)' : 'var(--text-muted)',
                        fontWeight: '600'
                      }}>
                        {trade.action}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
