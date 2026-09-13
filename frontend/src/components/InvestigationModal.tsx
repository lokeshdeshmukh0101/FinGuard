import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle, AlertOctagon } from 'lucide-react';
import { api } from '../services/api';

interface InvestigationModalProps {
  transactionId: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const InvestigationModal: React.FC<InvestigationModalProps> = ({ transactionId, onClose, onSuccess }) => {
  const [decision, setDecision] = useState<'LEGITIMATE' | 'CONFIRMED_FRAUD' | 'UNDER_REVIEW'>('CONFIRMED_FRAUD');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!transactionId) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/investigations', {
        transaction_id: transactionId,
        decision,
        notes,
      });
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to submit investigation decision.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '550px', padding: '28px', background: '#131b2e' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert color="var(--accent-amber)" size={22} />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Fraud Investigation Workflow</h2>
          </div>
          <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={onClose}><X size={18} /></button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>TRANSACTION ID</label>
            <input className="input-field" value={transactionId} disabled style={{ fontFamily: 'var(--font-mono)', opacity: 0.7 }} />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 600 }}>ANALYST DECISION</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
              <button
                type="button"
                className="btn"
                style={{
                  background: decision === 'CONFIRMED_FRAUD' ? 'rgba(244, 63, 94, 0.25)' : 'rgba(255,255,255,0.04)',
                  border: `1px solid ${decision === 'CONFIRMED_FRAUD' ? 'var(--accent-rose)' : 'var(--border-color)'}`,
                  color: decision === 'CONFIRMED_FRAUD' ? 'var(--accent-rose)' : 'var(--text-secondary)'
                }}
                onClick={() => setDecision('CONFIRMED_FRAUD')}
              >
                <AlertOctagon size={16} /> Confirmed Fraud
              </button>

              <button
                type="button"
                className="btn"
                style={{
                  background: decision === 'LEGITIMATE' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(255,255,255,0.04)',
                  border: `1px solid ${decision === 'LEGITIMATE' ? 'var(--accent-green)' : 'var(--border-color)'}`,
                  color: decision === 'LEGITIMATE' ? 'var(--accent-green)' : 'var(--text-secondary)'
                }}
                onClick={() => setDecision('LEGITIMATE')}
              >
                <CheckCircle size={16} /> Legitimate
              </button>

              <button
                type="button"
                className="btn"
                style={{
                  background: decision === 'UNDER_REVIEW' ? 'rgba(245, 158, 11, 0.25)' : 'rgba(255,255,255,0.04)',
                  border: `1px solid ${decision === 'UNDER_REVIEW' ? 'var(--accent-amber)' : 'var(--border-color)'}`,
                  color: decision === 'UNDER_REVIEW' ? 'var(--accent-amber)' : 'var(--text-secondary)'
                }}
                onClick={() => setDecision('UNDER_REVIEW')}
              >
                Under Review
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>INVESTIGATION NOTES</label>
            <textarea
              className="input-field"
              rows={4}
              placeholder="Record details of customer verification, IP tracing, or merchant logs..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Save Decision'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
