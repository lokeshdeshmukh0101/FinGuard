import React, { useEffect, useState } from 'react';
import { api, type AuditLog } from '../services/api';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const res = await api.get('/audit-logs');
      setLogs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Immutable System Audit Trail</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Regulatory compliance logging for analyst decisions, authentication events, and rule updates</p>
      </div>

      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Loading Audit Logs...</div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>User ID</th>
                <th>Metadata</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    No audit logs recorded yet.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--accent-purple)' }}>{log.id.substring(0, 8)}...</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(log.timestamp).toLocaleString()}</td>
                    <td>
                      <span className="badge badge-medium" style={{ fontSize: '0.7rem' }}>
                        {log.action}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', fontWeight: 600 }}>{log.entity_type}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{log.entity_id ? log.entity_id.substring(0, 12) : '-'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--accent-blue)' }}>{log.user_id ? log.user_id.substring(0, 8) : 'SYSTEM'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {log.metadata_json ? JSON.stringify(log.metadata_json) : '-'}
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
