# FinGuard 🛡️
### AI-Powered Real-Time Banking Fraud Detection & Risk Investigation Platform

FinGuard is a simulated portfolio-grade banking technology platform designed to demonstrate modern software engineering, machine learning pipelines, explainable AI, database design, REST API architecture, and DevOps practices.

---

## 🌟 Key Features
- **Real-Time Transaction Risk Analysis**: Evaluates incoming banking transactions in real-time.
- **Hybrid Detection Engine**: Combines configurable rule-based fraud detection with a Scikit-Learn ML classifier (Random Forest / Logistic Regression).
- **Explainable AI (XAI)**: Generates human-understandable reason codes for flagged transactions (e.g. `+30: Amount 4.2x customer average`, `+25: Location anomaly`).
- **Analyst Investigation Workflow**: Provides a full alert management UI to inspect flagged transactions, review customer history, add investigation notes, and update statuses.
- **Role-Based Access Control (RBAC)**: Secure access for `CUSTOMER`, `ANALYST`, and `ADMIN` user roles.
- **Audit Trail & System Health**: Records audit logs for all sensitive investigation decisions and exposes Prometheus-compatible metrics and `/health` endpoints.
- **Containerized & CI/CD Ready**: Fully runnable via Docker Compose with automated GitHub Actions testing pipelines.

---

## 🏗️ Architecture Overview

```
Frontend (React + TS + Vite)
    │
    ▼ REST API / JWT
Backend Gateway (FastAPI + Pydantic)
    ├── Auth & RBAC
    ├── Transaction Processing
    ├── Fraud Detection Engine (Rules + ML Model)
    ├── Risk Scoring & Explanation Engine
    └── Audit & Alert Services
    │
    ▼ SQLAlchemy ORM
PostgreSQL Database
```

---

## 🚀 Quick Start (Local Development)

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create & activate virtual environment (optional)
python -m venv venv
# On Windows: venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt

# Run backend development server
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation: Access [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend Web App: Access [http://localhost:5173](http://localhost:5173).

---

## 📊 Synthetic Data & Model Training
Generate 10,000 synthetic banking transactions and train the ML fraud detection model:
```bash
python scripts/generate_data.py --transactions 10000
python ml/train.py
```

---

## 🐳 Docker Setup
Run the entire stack (PostgreSQL + FastAPI + React Frontend) with Docker Compose:
```bash
docker-compose up --build
```

---

## 📁 Repository Structure
```
├── backend/          # FastAPI REST API & Domain Services
├── frontend/         # React 18 + TypeScript + Vite SPA
├── ml/               # Data generator, feature pipeline & ML models
├── scripts/          # Synthetic data utility scripts
├── docs/             # Technical docs (Architecture, DSA, ML, Security, Interview Guide)
├── docker-compose.yml
└── README.md
```

---

## 📜 License & Disclaimers
*Disclaimer: FinGuard is a simulated banking platform using 100% synthetic demo data. It does not process real financial transactions or store real financial credentials.*
