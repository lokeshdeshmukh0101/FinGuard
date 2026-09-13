import React, { useEffect, useState } from 'react';
import { X, Cpu } from 'lucide-react';
import { api, type XAIExplanation } from '../services/api';

interface XaiModalProps {
  transactionId: string | null;
  onClose: () => void;
  onOpenInvestigate?: (txId: string) => void;
}

export const XaiModal: React.FC<XaiModalProps> = ({ transactionId, onClose, onOpenInvestigate }) => {
  const [data, setData] = useState<XAIExplanation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!transactionId) return;
    setLoading(true);
    api.get(`/risk/${transactionId}`)
      .then((res) => setData(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [transactionId]);

  if (!transactionId) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '650px', maxHeight: '90vh', overflowY: 'auto', padding: '28px', background: '#131b2e' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Cpu color="var(--accent-cyan)" size={24} />
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Risk Score & XAI Explanation</h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Transaction ID: <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-blue)' }}>{transactionId}</span></p>
            </div>
          </div>
          <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={onClose}><X size={18} /></button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Evaluating Risk & Extracting SHAP Explanations...</div>
        ) : data ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(255, 255, 255, 0.03)', padding: '16px 20px', borderRadius: 'var(--radius-md)', marginBottom: '20px', border: '1px solid var(--border-color)' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Risk Score</span>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: data.risk_level === 'HIGH' ? 'var(--accent-rose)' : (data.risk_level === 'MEDIUM' ? 'var(--accent-amber)' : 'var(--accent-green)') }}>
                  {data.final_risk_score} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 100</span>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span className={`badge badge-${data.risk_level.toLowerCase()}`} style={{ fontSize: '0.85rem', padding: '6px 14px' }}>
                  {data.risk_level} RISK
                </span>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
                  Rules: {data.rule_score} pts | ML Prob: {(data.model_probability * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
              Why was this transaction flagged?
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
              {data.contributing_factors.map((factor, index) => (
                <div key={index} style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px 16px', borderRadius: 'var(--radius-sm)', borderLeft: `3px solid ${factor.weight.includes('+') ? 'var(--accent-rose)' : 'var(--accent-green)'}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>{factor.factor}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{factor.description}</div>
                  </div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: factor.weight.includes('+') ? 'var(--accent-rose)' : 'var(--accent-green)', fontFamily: 'var(--font-mono)' }}>
                    {factor.weight}
                  </span>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button className="btn btn-secondary" onClick={onClose}>Close</button>
              {onOpenInvestigate && (
                <button className="btn btn-primary" onClick={() => { onClose(); onOpenInvestigate(transactionId); }}>
                  Investigate Transaction
                </button>
              )}
            </div>
          </div>
        ) : (
          <div style={{ color: 'var(--accent-rose)' }}>Failed to load XAI explanation.</div>
        )}
      </div>
    </div>
  );
};
