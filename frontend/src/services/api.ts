import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('finguard_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interfaces
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'CUSTOMER' | 'ANALYST' | 'ADMIN';
  created_at: string;
}

export interface Customer {
  id: string;
  user_id: string;
  account_number: string;
  normal_location: string;
  average_transaction_amount: number;
}

export interface Merchant {
  id: string;
  name: string;
  category: string;
  location: string;
}

export interface Transaction {
  id: string;
  customer_id: string;
  merchant_id: string;
  amount: number;
  transaction_time: string;
  location: string;
  device_id: string;
  status: 'PENDING' | 'APPROVED' | 'FLAGGED' | 'REJECTED';
  created_at: string;
  customer?: Customer;
  merchant?: Merchant;
}

export interface RiskScore {
  id: string;
  transaction_id: string;
  score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  model_score: number;
  rule_score: number;
  breakdown?: any;
}

export interface XAIExplanation {
  transaction_id: string;
  final_risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  rule_score: number;
  model_probability: number;
  contributing_factors: Array<{
    factor: string;
    weight: string;
    description: string;
  }>;
  raw_reasons: string[];
}

export interface FraudAlert {
  id: string;
  transaction_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  reason: string;
  status: 'NEW' | 'UNDER_REVIEW' | 'RESOLVED';
  created_at: string;
  resolved_at?: string;
  transaction?: Transaction;
}

export interface AuditLog {
  id: string;
  user_id?: string;
  action: string;
  entity_type: string;
  entity_id: string;
  metadata_json?: any;
  timestamp: string;
  user?: User;
}

export interface DashboardStats {
  kpis: {
    total_transactions: number;
    total_value: number;
    flagged_transactions: number;
    high_risk_transactions: number;
    fraud_rate_percentage: number;
    pending_investigations: number;
    confirmed_fraud: number;
    legitimate_transactions: number;
  };
  charts: {
    risk_distribution: Array<{ name: string; value: number; color: string }>;
    category_distribution: Array<{ category: string; count: number }>;
  };
}
