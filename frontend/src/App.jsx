import React, { useState } from 'react';
import Dashboard from './Dashboard';
import Simulator from './Simulator';
import DecisionsHistory from './DecisionsHistory';
import { Shield, LayoutDashboard, ActivitySquare, List } from 'lucide-react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      <header style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Shield size={40} color="var(--accent-blue)" />
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <h1 style={{ margin: 0, lineHeight: 1 }}>Centinela</h1>
          <span className="text-muted" style={{ fontSize: '0.9rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Sistema Predictivo Cuantitativo</span>
        </div>
      </header>

      <nav className="nav-tabs">
        <button 
          className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <LayoutDashboard size={20} />
          Panel de Control
        </button>
        <button 
          className={`nav-tab ${activeTab === 'simulator' ? 'active' : ''}`}
          onClick={() => setActiveTab('simulator')}
        >
          <ActivitySquare size={20} />
          Simulador Avanzado
        </button>
        <button 
          className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <List size={20} />
          Historial Completo
        </button>
      </nav>

      <main>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'simulator' && <Simulator />}
        {activeTab === 'history' && <DecisionsHistory />}
      </main>
    </div>
  );
}

export default App;
