import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Database } from 'lucide-react';

const API_URL = 'https://modelopredictivocriptomonedas.onrender.com/api';

export default function DecisionsHistory() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API_URL}/dashboard/all-decisions`);
        setDecisions(res.data.decisions);
      } catch (error) {
        console.error("Error fetching all decisions:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="glass-panel animate-fade-in">Cargando historial completo...</div>;
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      <div className="info-box">
        <strong>📚 Base de Datos Completa:</strong> Aquí puedes auditar todas las decisiones que el modelo ha tomado a lo largo del tiempo. 
        Se muestran desde la más reciente hasta la más antigua.
      </div>

      <div className="glass-panel">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <Database size={24} color="var(--accent-blue)" />
          <h2 style={{ margin: 0 }}>Historial Completo de Decisiones</h2>
        </div>
        
        <div style={{ overflowX: 'auto', maxHeight: '70vh', overflowY: 'auto' }}>
          <table className="data-table">
            <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--panel-bg)', zIndex: 1, backdropFilter: 'blur(10px)' }}>
              <tr>
                <th>Fecha</th>
                <th>Precio BTC</th>
                <th>Volatilidad (GARCH)</th>
                <th>Régimen (IA)</th>
                <th>Decisión Final</th>
              </tr>
            </thead>
            <tbody>
              {decisions.map((row, i) => (
                <tr key={i}>
                  <td>{row.date}</td>
                  <td>${row.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                  <td>{row.volatility.toFixed(4)}</td>
                  <td>
                    {row.regime === 0 ? '0 (Baja Vol)' : row.regime === 1 ? '1 (Media Vol)' : '2 (Alta Vol/Peligro)'}
                  </td>
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
