import React, { useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import { api, type User } from '../services/api';

interface LoginPageProps {
  onLoginSuccess: (token: string, user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('analyst@example.com');
  const [password, setPassword] = useState('Password123!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await api.post('/auth/login', { email, password });
      const { access_token, user } = res.data;
      localStorage.setItem('finguard_token', access_token);
      onLoginSuccess(access_token, user);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('Password123!');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(circle at 50% 30%, #1e293b 0%, #0b0f17 100%)', padding: '20px' }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '440px', padding: '36px', background: '#131b2e' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'linear-gradient(135deg, #2563eb, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px' }}>
            <ShieldAlert size={28} color="white" />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>FinGuard Banking API</h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>AI-Powered Real-Time Fraud & Risk Platform</p>
        </div>

        <div style={{ marginBottom: '24px', padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '8px', textAlign: 'center' }}>
            DEMO QUICK LOGIN PERSONAS
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '6px' }}
              onClick={() => handleDemoLogin('analyst@example.com')}
            >
              Analyst
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '6px' }}
              onClick={() => handleDemoLogin('customer@example.com')}
            >
              Customer
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '6px' }}
              onClick={() => handleDemoLogin('admin@example.com')}
            >
              Admin
            </button>
          </div>
        </div>

        {error && (
          <div style={{ padding: '10px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#f87171', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>EMAIL ADDRESS</label>
            <input
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>PASSWORD</label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }} disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In to FinGuard'}
          </button>
        </form>

      </div>
    </div>
  );
};
