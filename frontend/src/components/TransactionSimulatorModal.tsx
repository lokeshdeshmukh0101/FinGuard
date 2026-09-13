import React, { useEffect, useState } from 'react';
import { X, Send } from 'lucide-react';
import { api, type Customer, type Merchant } from '../services/api';

interface TransactionSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (result: any) => void;
}

export const TransactionSimulatorModal: React.FC<TransactionSimulatorModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [selectedMerchantId, setSelectedMerchantId] = useState('');
  const [amount, setAmount] = useState('150.00');
  const [location, setLocation] = useState('New York, USA');
  const [deviceId, setDeviceId] = useState('DEV-WEB-MOBILE-1');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    api.get('/customers').then((res) => {
      setCustomers(res.data);
      if (res.data.length > 0) setSelectedCustomerId(res.data[0].id);
    }).catch(err => console.error(err));

    api.get('/merchants').then((res) => {
      setMerchants(res.data);
      if (res.data.length > 0) setSelectedMerchantId(res.data[0].id);
    }).catch(err => console.error(err));
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.post('/transactions', {
        customer_id: selectedCustomerId,
        merchant_id: selectedMerchantId,
        amount: parseFloat(amount),
        location,
        device_id: deviceId
      });
      onSuccess(res.data);
      onClose();
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || 'Transaction evaluation failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '580px', padding: '28px', background: '#131b2e' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Send color="var(--accent-blue)" size={20} />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Real-Time Transaction Simulator</h2>
          </div>
          <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={onClose}><X size={18} /></button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '18px', padding: '12px', background: 'rgba(59, 130, 246, 0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)', display: 'block', marginBottom: '6px' }}>⚡ QUICK SCENARIO TEMPLATES:</span>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: '0.75rem', padding: '4px 8px' }}
                onClick={() => { setAmount('85.00'); setLocation('Mumbai, India'); }}
              >
                Normal Spending (₹85)
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: '0.75rem', padding: '4px 8px', color: 'var(--accent-amber)' }}
                onClick={() => { setAmount('850.00'); setLocation('Mumbai, India'); }}
              >
                High Amount Spike (₹850)
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: '0.75rem', padding: '4px 8px', color: 'var(--accent-rose)' }}
                onClick={() => { setAmount('3500.00'); setLocation('Tokyo, Japan'); setDeviceId('DEV-UNKNOWN-X'); }}
              >
                High-Risk Fraud (₹3,500 + Tokyo)
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>SELECT CUSTOMER</label>
            <select className="input-field" value={selectedCustomerId} onChange={(e) => setSelectedCustomerId(e.target.value)}>
              {customers.map(c => (
                <option key={c.id} value={c.id}>
                  {c.account_number} — Normal: {c.normal_location} (Avg: ₹{c.average_transaction_amount})
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>SELECT MERCHANT</label>
            <select className="input-field" value={selectedMerchantId} onChange={(e) => setSelectedMerchantId(e.target.value)}>
              {merchants.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name} [{m.category}] — {m.location}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>AMOUNT (₹ INR)</label>
              <input className="input-field" type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>LOCATION</label>
              <input className="input-field" value={location} onChange={(e) => setLocation(e.target.value)} required />
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>DEVICE ID</label>
            <input className="input-field" value={deviceId} onChange={(e) => setDeviceId(e.target.value)} required />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Evaluating...' : 'Process Transaction'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
