import React, { useEffect, useState } from 'react';
import { api, type FraudAlert } from '../services/api';

interface AlertsPageProps {
  onOpenXai: (txId: string) => void;
  onOpenInvestigate: (txId: string) => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ onOpenXai, onOpenInvestigate }) => {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.get('/alerts');
      setAlerts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Fraud Alert Management Queue</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>High-severity fraud alerts requiring immediate analyst investigation and status resolution</p>
      </div>

      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Loading Alerts...</div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Transaction ID</th>
                <th>Severity</th>
                <th>Flag Reason</th>
                <th>Status</th>
                <th>Created At</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    No active fraud alerts in queue.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-rose)' }}>{alert.id.substring(0, 8)}...</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-blue)' }}>{alert.transaction_id.substring(0, 8)}...</td>
                    <td><span className="badge badge-high">{alert.severity}</span></td>
                    <td style={{ maxWidth: '300px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{alert.reason}</td>
                    <td>
                      <span className={`badge badge-${alert.status === 'NEW' ? 'high' : (alert.status === 'UNDER_REVIEW' ? 'medium' : 'low')}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(alert.created_at).toLocaleString()}</td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => onOpenXai(alert.transaction_id)}>
                          XAI Reasons
                        </button>
                        <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => onOpenInvestigate(alert.transaction_id)}>
                          Investigate
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

    </div>
  );
};
