import React from 'react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon?: React.ReactNode;
  color?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({ title, value, subtext, icon, color = '#3b82f6' }) => {
  return (
    <div className="glass-card" style={{ padding: '20px', flex: 1, minWidth: '220px', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: color }} />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {title}
        </span>
        {icon && <div style={{ color }}>{icon}</div>}
      </div>
      <div style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
        {value}
      </div>
      {subtext && (
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          {subtext}
        </div>
      )}
    </div>
  );
};
