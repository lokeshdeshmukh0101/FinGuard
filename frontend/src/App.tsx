import { useEffect, useState } from 'react';
import { api, type User } from './services/api';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { AlertsPage } from './pages/AlertsPage';
import { AuditPage } from './pages/AuditPage';
import { XaiModal } from './components/XaiModal';
import { InvestigationModal } from './components/InvestigationModal';
import { TransactionSimulatorModal } from './components/TransactionSimulatorModal';

export function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('finguard_token'));
  const [user, setUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'transactions' | 'alerts' | 'audit'>('dashboard');
  const [loading, setLoading] = useState(true);

  // Modals state
  const [xaiTxId, setXaiTxId] = useState<string | null>(null);
  const [investigateTxId, setInvestigateTxId] = useState<string | null>(null);
  const [simulatorOpen, setSimulatorOpen] = useState(false);

  useEffect(() => {
    if (token) {
      api.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('finguard_token');
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const handleLoginSuccess = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
  };

  const handleLogout = () => {
    localStorage.removeItem('finguard_token');
    setToken(null);
    setUser(null);
  };

  const handleSimulationSuccess = (evalResult: any) => {
    setXaiTxId(evalResult.transaction_id);
  };

  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0b0f17', color: '#94a3b8' }}>Loading FinGuard...</div>;
  }

  if (!token || !user) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', display: 'flex', flexDirection: 'column' }}>
      
      <Navbar
        user={user}
        activeTab={activeTab}
        setActiveTab={(tab: any) => setActiveTab(tab)}
        onLogout={handleLogout}
        onOpenSimulator={() => setSimulatorOpen(true)}
      />

      <main style={{ flex: 1, maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '28px 24px' }}>
        {activeTab === 'dashboard' && (
          <DashboardPage
            user={user}
            onOpenXai={(txId) => setXaiTxId(txId)}
            onOpenInvestigate={(txId) => setInvestigateTxId(txId)}
          />
        )}
        {activeTab === 'transactions' && (
          <TransactionsPage
            user={user}
            onOpenXai={(txId) => setXaiTxId(txId)}
            onOpenInvestigate={(txId) => setInvestigateTxId(txId)}
          />
        )}
        {activeTab === 'alerts' && (
          <AlertsPage
            onOpenXai={(txId) => setXaiTxId(txId)}
            onOpenInvestigate={(txId) => setInvestigateTxId(txId)}
          />
        )}
        {activeTab === 'audit' && <AuditPage />}
      </main>

      <XaiModal
        transactionId={xaiTxId}
        onClose={() => setXaiTxId(null)}
        onOpenInvestigate={(txId) => setInvestigateTxId(txId)}
      />

      <InvestigationModal
        user={user}
        transactionId={investigateTxId}
        onClose={() => setInvestigateTxId(null)}
        onSuccess={() => {
          setInvestigateTxId(null);
        }}
      />

      <TransactionSimulatorModal
        isOpen={simulatorOpen}
        onClose={() => setSimulatorOpen(false)}
        onSuccess={handleSimulationSuccess}
      />

    </div>
  );
}

export default App;
