import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot } from 'recharts';
import { RefreshCw, DatabaseZap } from 'lucide-react';

const API_URL = 'https://modelopredictivocriptomonedas.onrender.com/api';

export default function Dashboard() {
  const [current, setCurrent] = useState(null);
  const [history, setHistory] = useState([]);
  const [recentDecisions, setRecentDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  const fetchData = async () => {
    try {
      const [currRes, histRes, decRes] = await Promise.all([
        axios.get(`${API_URL}/dashboard/current`),
        axios.get(`${API_URL}/dashboard/history`),
        axios.get(`${API_URL}/dashboard/recent-decisions`)
      ]);
      setCurrent(currRes.data);
      setHistory(histRes.data.history);
      setRecentDecisions(decRes.data.decisions);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const triggerAction = async (endpoint) => {
    setActionLoading(true);
    if (endpoint === 'update') {
      setActionMessage('⏳ Descargando últimos precios y actualizando señales...');
    } else {
      setActionMessage('⏳ Re-entrenando la Inteligencia Artificial (esto tomará unos minutos)...');
    }
    
    try {
      const res = await axios.post(`${API_URL}/actions/${endpoint}`);
      setActionMessage('✅ ' + res.data.message);
      // Actualizar la pantalla inmediatamente con los nuevos datos
      await fetchData();
    } catch (error) {
      setActionMessage('❌ ' + (error.response?.data?.detail || "Error al realizar la acción."));
    } finally {
      setActionLoading(false);
      setTimeout(() => setActionMessage(''), 8000);
    }
  };

  if (loading) {
    return <div className="glass-panel animate-fade-in">Cargando datos del dashboard...</div>;
  }

  if (!current) {
    return <div className="glass-panel animate-fade-in status-red">Error cargando datos. Asegúrate de que el backend (FastAPI) esté corriendo.</div>;
  }

  const isBuy = current.decision === 'COMPRAR';
  const isSell = current.decision === 'SALIR';

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      {/* Control Panel */}
      <div className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Controles del Sistema</h2>
          <span className="text-muted" style={{ fontSize: '0.9rem' }}>Ejecuta los scripts subyacentes de Python</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button 
            className="btn-primary" 
            onClick={() => triggerAction('update')} 
            disabled={actionLoading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, var(--accent-green) 0%, #059669 100%)' }}
          >
            <RefreshCw size={18} className={actionLoading ? 'animate-spin' : ''} />
            Actualizar Datos
          </button>
          <button 
            className="btn-primary" 
            onClick={() => triggerAction('retrain')} 
            disabled={actionLoading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)' }}
          >
            <DatabaseZap size={18} className={actionLoading ? 'animate-spin' : ''} />
            Re-entrenar Modelo
          </button>
        </div>
      </div>
      {actionMessage && (
        <div className="info-box animate-fade-in" style={{ borderLeftColor: 'var(--accent-green)', color: 'var(--accent-green)' }}>
          ✅ {actionMessage}
        </div>
      )}

      {/* KPIs */}
      <div className="kpi-grid">
        <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid ' + (isBuy ? 'var(--accent-green)' : isSell ? 'var(--accent-red)' : 'var(--text-muted)') }}>
          <span className="kpi-label">Decisión de Hoy ({current.date})</span>
          <span className={`kpi-value ${isBuy ? 'status-green' : isSell ? 'status-red' : ''}`}>
            {current.decision} {isBuy ? '🟢' : isSell ? '🔴' : '⚪'}
          </span>
        </div>
        
        <div className="glass-panel kpi-card">
          <span className="kpi-label">Régimen IA</span>
          <span className={`kpi-value ${current.regime >= 2 ? 'status-red' : 'status-green'}`}>
            {current.regime <= 1 ? 'Seguro (0/1)' : 'Peligro (2)'}
          </span>
        </div>

        <div className="glass-panel kpi-card">
          <span className="kpi-label">Volatilidad Actual</span>
          <span className="kpi-value">{current.volatility.toFixed(4)}</span>
        </div>

        <div className="glass-panel kpi-card">
          <span className="kpi-label">Tendencia Vol (5d)</span>
          <span className="kpi-value">{current.vol_trend_5.toFixed(4)}</span>
        </div>
      </div>

      <div className="glass-panel">
        <h2>Evolución de la Volatilidad GARCH</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" stroke="#8b9bb4" tick={{fill: '#8b9bb4', fontSize: 12}} />
              <YAxis stroke="#8b9bb4" tick={{fill: '#8b9bb4', fontSize: 12}} domain={['auto', 'auto']} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(20, 26, 42, 0.95)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Line type="monotone" dataKey="volatility" stroke="var(--accent-blue)" strokeWidth={2} dot={false} name="Volatilidad" />
              
              {history.map((entry, index) => {
                if (entry.decision === 'SALIR') {
                  return <ReferenceDot key={`sell-${index}`} x={entry.date} y={entry.volatility} r={4} fill="var(--accent-red)" stroke="none" />;
                }
                if (entry.decision === 'COMPRAR') {
                  return <ReferenceDot key={`buy-${index}`} x={entry.date} y={entry.volatility} r={4} fill="var(--accent-green)" stroke="none" />;
                }
                return null;
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-panel">
        <h2>Últimas 10 Decisiones</h2>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Precio</th>
                <th>Volatilidad</th>
                <th>Régimen</th>
                <th>Decisión</th>
              </tr>
            </thead>
            <tbody>
              {recentDecisions.map((row, i) => (
                <tr key={i}>
                  <td>{row.date}</td>
                  <td>${row.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                  <td>{row.volatility.toFixed(4)}</td>
                  <td>{row.regime}</td>
                  <td className={row.decision === 'COMPRAR' ? 'status-green' : row.decision === 'SALIR' ? 'status-red' : ''} style={{ fontWeight: '600' }}>
                    {row.decision}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
