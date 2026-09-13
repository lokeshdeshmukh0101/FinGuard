# FinGuard System Architecture & Design

## 1. Executive Summary
FinGuard is an enterprise-grade banking fraud detection platform built with Python (FastAPI), PostgreSQL, Scikit-learn ML models, and React/TypeScript. The platform processes high-velocity financial transactions, flags anomalous activity using a hybrid risk engine (rules + ML), and provides an interactive analyst dashboard for fraud investigations.

## 2. Core Architecture Diagram

```
[ Frontend: React + TypeScript + Vite ]
                   │
                   ▼ (REST / JSON over HTTPS + JWT Auth)
[ FastAPI Backend Gateway & Services ]
   ├── Authentication & RBAC Middleware (Customer / Analyst / Admin)
   ├── Transaction Processing Service
   ├── Fraud Detection Engine
   │     ├── Rule Engine (Velocity, Location, Amount Ratio, Time Anomaly)
   │     └── ML Model Pipeline (Random Forest / Logistic Regression)
   ├── Risk Scoring Engine (Hybrid Weighted Fusion + SHAP Reason Codes)
   ├── Fraud Alert & Investigation Workflow Service
   └── Audit Trail & Metrics Logging
                   │
                   ▼ (SQLAlchemy ORM)
[ PostgreSQL Database (or SQLite Dev Engine) ]
```

## 3. High-Level Component Responsibilities

| Component | Technology | Responsibility |
|---|---|---|
| **Frontend SPA** | React 18, TypeScript, Vite, Recharts, Lucide Icons | Analyst UI, real-time metrics dashboard, transaction inspection, alert resolution modal, customer view. |
| **API Gateway** | FastAPI, Pydantic v2 | Request routing, payload validation, JWT token verification, exception handling, OpenAPI docs generation. |
| **Transaction Service** | Python | Transaction ingestion, database persistence, state management (PENDING, APPROVED, FLAGGED, REJECTED). |
| **Fraud Detection Engine** | Scikit-learn, Custom Rules | Feature extraction, sliding window velocity calculation, rule execution, ML model prediction. |
| **Risk Scoring Engine** | Python | Combines rule weight scores and ML prediction probability into normalized 0-100 score + explainability reason codes. |
| **Database** | PostgreSQL / SQLite | Relational storage for users, customers, merchants, transactions, risk scores, alerts, investigations, and audit logs. |

## 4. Key Engineering Choices
- **Modular Monolith**: Microservices introduce distributed tracing and network latency overhead unnecessary for single-team deployments. A modular monolith provides strict domain boundaries while keeping deployment simple and performant.
- **Hybrid Scoring (Rules + ML)**: Pure ML models struggle with newly emergent fraud vectors ("cold start"). Pure rules miss complex multi-dimensional fraud patterns. Combining both guarantees deterministic guardrails (Rules) alongside statistical pattern detection (ML).
- **Stateless REST & JWT**: Allows independent horizontal scaling of backend API containers behind a standard load balancer.
