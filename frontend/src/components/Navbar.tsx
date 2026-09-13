import React from 'react';
import { ShieldAlert, User as UserIcon, LogOut, Activity, FileText } from 'lucide-react';
import type { User } from '../services/api';

interface NavbarProps {
  user: User | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout: () => void;
  onOpenSimulator: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  activeTab,
  setActiveTab,
  onLogout,
  onOpenSimulator,
}) => {
  return (
    <header style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-color)', padding: '14px 24px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => setActiveTab('dashboard')}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #2563eb, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ShieldAlert size={22} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', background: 'linear-gradient(to right, #f8fafc, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              FinGuard
            </h1>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>AI Fraud Detection Platform</p>
          </div>
        </div>

        <nav style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <Activity size={16} /> Dashboard
          </button>
          <button
            className={`btn ${activeTab === 'transactions' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('transactions')}
          >
            Transactions
          </button>
          {user?.role !== 'CUSTOMER' && (
            <button
              className={`btn ${activeTab === 'alerts' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('alerts')}
            >
              Alerts
            </button>
          )}
          {user?.role !== 'CUSTOMER' && (
            <button
              className={`btn ${activeTab === 'audit' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('audit')}
            >
              <FileText size={16} /> Audit Trail
            </button>
          )}
        </nav>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn btn-primary" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }} onClick={onOpenSimulator}>
            + Test Transaction
          </button>

          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '6px 12px', background: 'rgba(255, 255, 255, 0.04)', borderRadius: '20px', border: '1px solid var(--border-color)' }}>
              <UserIcon size={16} color="var(--accent-blue)" />
              <div style={{ fontSize: '0.8rem' }}>
                <span style={{ fontWeight: 600 }}>{user.name}</span>
                <span style={{ marginLeft: '6px', fontSize: '0.68rem', padding: '2px 6px', borderRadius: '4px', background: user.role === 'ADMIN' ? 'rgba(244, 63, 94, 0.2)' : (user.role === 'ANALYST' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(59, 130, 246, 0.2)'), color: 'white' }}>
                  {user.role}
                </span>
              </div>
            </div>
          )}

          <button className="btn btn-secondary" style={{ padding: '8px' }} onClick={onLogout} title="Logout">
            <LogOut size={16} />
          </button>
        </div>

      </div>
    </header>
  );
};
