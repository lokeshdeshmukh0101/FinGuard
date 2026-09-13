import React, { useEffect, useState } from 'react';
import { Activity, ShieldAlert, IndianRupee, AlertTriangle, CheckCircle } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { api, type DashboardStats, type Transaction, type FraudAlert } from '../services/api';
import { KpiCard } from '../components/KpiCard';

import { type User } from '../services/api';

interface DashboardPageProps {
  user: User | null;
  onOpenXai: (txId: string) => void;
  onOpenInvestigate: (txId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ user, onOpenXai, onOpenInvestigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      if (user?.role === 'CUSTOMER') {
        const [statsRes, txRes] = await Promise.all([
          api.get('/dashboard/statistics'),
          api.get('/transactions?limit=6')
        ]);
        setStats(statsRes.data);
        setRecentTransactions(txRes.data);
        setRecentAlerts([]);
      } else {
        const [statsRes, txRes, alertRes] = await Promise.all([
          api.get('/dashboard/statistics'),
          api.get('/transactions?limit=6'),
          api.get('/alerts?limit=5')
        ]);
        setStats(statsRes.data);
        setRecentTransactions(txRes.data);
        setRecentAlerts(alertRes.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>Loading Real-Time Analytics Dashboard...</div>;
  }

  const kpis = stats.kpis;
  const isCustomer = user?.role === 'CUSTOMER';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>
            {isCustomer ? 'Customer Account Summary & Risk Overview' : 'Fraud Intelligence & Risk Executive Summary'}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            {isCustomer ? 'Personal account transaction activity, spending baseline, and automated security indicators' : 'Real-time monitoring of transaction velocity, rule violations, and ML probability scores'}
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchDashboardData}>Refresh Data</button>
      </div>

      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
        <KpiCard
          title="Total Transactions"
          value={kpis.total_transactions.toLocaleString()}
          subtext="Processed by Risk Engine"
          icon={<Activity size={20} />}
          color="var(--accent-blue)"
        />
        <KpiCard
          title="Total Transaction Volume"
          value={`₹${kpis.total_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          subtext="INR Gross Value"
          icon={<IndianRupee size={20} />}
          color="var(--accent-cyan)"
        />
        <KpiCard
          title="Flagged High Risk"
          value={kpis.flagged_transactions}
          subtext={`Fraud Rate: ${kpis.fraud_rate_percentage}%`}
          icon={<ShieldAlert size={20} />}
          color="var(--accent-rose)"
        />
        <KpiCard
          title="Pending Investigations"
          value={kpis.pending_investigations}
          subtext="Requires Analyst Review"
          icon={<AlertTriangle size={20} />}
          color="var(--accent-amber)"
        />
        <KpiCard
          title="Confirmed Fraud"
          value={kpis.confirmed_fraud}
          subtext="Confirmed by Analyst Audit"
          icon={<CheckCircle size={20} />}
          color="var(--accent-purple)"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)' }}>Risk Category Breakdown</h3>
          <div style={{ width: '100%', height: '240px' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={stats.charts.risk_distribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                >
                  {stats.charts.risk_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#131b2e', border: '1px solid #334155', borderRadius: '6px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)' }}>Transaction Distribution by Category</h3>
          <div style={{ width: '100%', height: '240px' }}>
            <ResponsiveContainer>
              <BarChart data={stats.charts.category_distribution}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: '#131b2e', border: '1px solid #334155', borderRadius: '6px' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px' }}>Real-Time Ingested Transactions</h3>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Tx ID</th>
                <th>Amount</th>
                <th>Location</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((tx) => (
                <tr key={tx.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-blue)' }}>{tx.id.substring(0, 8)}...</td>
                  <td style={{ fontWeight: 700 }}>₹{tx.amount.toFixed(2)}</td>
                  <td>{tx.location}</td>
                  <td>
                    <span className={`badge badge-${tx.status === 'FLAGGED' ? 'high' : 'low'}`}>
                      {tx.status}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }} onClick={() => onOpenXai(tx.id)}>
                      XAI Insights
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', color: 'var(--accent-rose)' }}>Active Fraud Alerts</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recentAlerts.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No active fraud alerts.</div>
            ) : (
              recentAlerts.map(alert => (
                <div key={alert.id} style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-rose)' }}>HIGH SEVERITY</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{new Date(alert.created_at).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>{alert.reason}</div>
                  <button className="btn btn-primary" style={{ padding: '4px 8px', fontSize: '0.75rem', width: '100%' }} onClick={() => onOpenInvestigate(alert.transaction_id)}>
                    Investigate Alert
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
