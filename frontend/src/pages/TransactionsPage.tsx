import React, { useEffect, useState } from 'react';
import { Search, Cpu, ShieldAlert } from 'lucide-react';
import { api, type Transaction, type User } from '../services/api';

interface TransactionsPageProps {
  user: User | null;
  onOpenXai: (txId: string) => void;
  onOpenInvestigate: (txId: string) => void;
}

export const TransactionsPage: React.FC<TransactionsPageProps> = ({ user, onOpenXai, onOpenInvestigate }) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetchTransactions();
  }, [search, statusFilter, riskFilter, page]);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const res = await api.get('/transactions', {
        params: {
          skip: page * 20,
          limit: 20,
          search: search || undefined,
          status: statusFilter || undefined,
          risk_level: riskFilter || undefined
        }
      });
      setTransactions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Transaction Log & Real-Time Risk Registry</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Search, filter, and inspect risk explanations for financial transactions</p>
        </div>
      </div>

      <div className="glass-card" style={{ padding: '16px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
        
        <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            className="input-field"
            style={{ paddingLeft: '36px' }}
            placeholder="Search by Tx ID, location, or device..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          />
        </div>

        <select
          className="input-field"
          style={{ width: '160px' }}
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
        >
          <option value="">All Statuses</option>
          <option value="APPROVED">APPROVED</option>
          <option value="FLAGGED">FLAGGED</option>
          <option value="REJECTED">REJECTED</option>
        </select>

        <select
          className="input-field"
          style={{ width: '160px' }}
          value={riskFilter}
          onChange={(e) => { setRiskFilter(e.target.value); setPage(0); }}
        >
          <option value="">All Risk Levels</option>
          <option value="LOW">LOW Risk</option>
          <option value="MEDIUM">MEDIUM Risk</option>
          <option value="HIGH">HIGH Risk</option>
        </select>

      </div>

      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Fetching Transactions...</div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Amount</th>
                <th>Location</th>
                <th>Device ID</th>
                <th>Timestamp</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    No transactions match current filters.
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => (
                  <tr key={tx.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--accent-blue)' }}>{tx.id.substring(0, 13)}...</td>
                    <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>₹{tx.amount.toFixed(2)}</td>
                    <td>{tx.location}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{tx.device_id}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(tx.transaction_time).toLocaleString()}</td>
                    <td>
                      <span className={`badge badge-${tx.status === 'FLAGGED' || tx.status === 'REJECTED' ? 'high' : 'low'}`}>
                        {tx.status}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => onOpenXai(tx.id)}>
                          <Cpu size={14} /> Why Flagged?
                        </button>
                        {user?.role !== 'CUSTOMER' && (
                          <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => onOpenInvestigate(tx.id)}>
                            <ShieldAlert size={14} /> Investigate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Showing Page {page + 1}</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-secondary" disabled={page === 0} onClick={() => setPage(p => Math.max(0, p - 1))}>
            Previous
          </button>
          <button className="btn btn-secondary" disabled={transactions.length < 20} onClick={() => setPage(p => p + 1)}>
            Next
          </button>
        </div>
      </div>

    </div>
  );
};
