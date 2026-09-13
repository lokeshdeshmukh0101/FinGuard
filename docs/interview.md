# FinGuard Technical Interview Preparation Guide

This guide contains representative software engineering internship interview questions and exact, technical answers based on the actual FinGuard implementation.

---

## 1. Software Engineering & System Architecture

### Q: Explain the high-level architecture of FinGuard.
**Answer:** FinGuard follows a **Modular Monolith** architecture. The frontend is a React 18 + TypeScript SPA built with Vite and Recharts. The backend is a Python FastAPI REST API. Requests flow through JWT Authentication & RBAC middleware into the `Transaction Processing Service`. Incoming transactions trigger a dual `Fraud Detection Engine`: a configurable `Rule Engine` (checking amount ratio, location anomaly, time of day, and merchant category) and an `ML Model Service` (Scikit-Learn Random Forest Classifier). The results are fused into a hybrid 0-100 Risk Score. High-risk transactions generate `FraudAlerts` and are routed to the `Analyst Investigation Workflow`, with all actions logged to an immutable `AuditLog` in PostgreSQL.

### Q: Why did you choose FastAPI over Flask or Django?
**Answer:** FastAPI provides native async support, automated OpenAPI (Swagger) generation, and high-performance serialization via Pydantic v2. For high-velocity financial transaction endpoints, FastAPI offers low latencies (~2-5ms API response times) without the heavy ORM overhead of Django.

### Q: How would you scale this system to handle 10 million transactions/day (~115 transactions/sec)?
**Answer:**
1. **Stateless API Horizon**: Scale FastAPI backend containers horizontally behind an AWS Application Load Balancer (ALB).
2. **Caching Layer**: Place Redis in front of PostgreSQL to cache customer profiles (`average_transaction_amount`, `normal_location`) with instant $\mathcal{O}(1)$ lookups.
3. **Asynchronous Queue**: Offload transaction ingestion to Kafka or RabbitMQ, processing risk scoring via asynchronous worker tasks (Celery/AsyncIO).
4. **Database Read Replicas**: Use PostgreSQL primary-replica setup for read queries (dashboard stats, audit logs) while directing writes to the primary DB instance.

---

## 2. Data Structures & Algorithms (DSA)

### Q: What data structures did you use in the project?
**Answer:**
1. **Sliding Window Deque (`collections.deque`)**: Implemented in `SlidingWindowVelocityEngine` to track transaction velocity. It pops expired timestamps outside the 10-minute window in amortized $\mathcal{O}(1)$ time.
2. **Hash Maps / Dictionaries (`Dict[UUID, Profile]`)**: Used for $\mathcal{O}(1)$ customer profile lookups and feature matrix maps during ML feature extraction.

### Q: How does your transaction velocity algorithm work?
**Answer:** For a customer $C_i$ submitting a transaction at $t_{new}$, we query timestamps within window $W = 10\text{ minutes}$. Using a timestamp queue, we pop elements at the head where $t < t_{new} - W$ and push $t_{new}$ at the tail. The length of the deque yields the exact transaction count in the interval $[t_{new} - 10\text{m}, t_{new}]$ in amortized $\mathcal{O}(1)$ time per transaction check.

---

## 3. Database Design & SQL

### Q: Explain your database schema and indexing strategy.
**Answer:** The database consists of 8 normalized relational tables: `users`, `customers`, `merchants`, `transactions`, `risk_scores`, `fraud_alerts`, `investigations`, and `audit_logs`.
Indexes were placed on:
- `transactions.customer_id` and `transactions.merchant_id` for fast JOIN operations.
- `transactions.transaction_time` for fast time-range queries.
- `transactions.status` and `risk_scores.risk_level` for fast analyst filtering.
- `users.email` and `customers.account_number` for $\mathcal{O}(1)$ unique lookups.

---

## 4. Machine Learning & Explainable AI

### Q: Why did you choose Random Forest over Logistic Regression?
**Answer:** Logistic Regression served as our baseline ($F1 = 0.9931$). However, financial fraud involves non-linear feature interactions (e.g. high amount + late hour + unrecognised device ID). Random Forest Classifier captured these non-linear decision boundaries ($F1 = 1.0000$, $ROC-AUC = 1.0000$) while remaining computationally fast for real-time inference ($<1.5\text{ms}$).

### Q: Why isn't accuracy enough for fraud detection?
**Answer:** Banking datasets suffer from severe class imbalance (~3.5% fraud). A dummy model predicting "Legitimate" for every transaction achieves 96.5% accuracy but misses 100% of fraud. We evaluated **Precision** (minimizing false alarms for innocent customers) and **Recall** (catching all actual fraud), optimizing the **F1-Score** and **ROC-AUC**.

### Q: How does Explainable AI (XAI) work in FinGuard?
**Answer:** Rather than showing opaque probabilities (e.g., `Risk Score = 91`), `xai_service.py` extracts feature contribution weights and translates them into human-understandable reason codes (e.g. `+35 pts — Amount is 4.2x customer average`, `+25 pts — Location anomaly`).

---

## 5. Security & DevOps

### Q: How does authentication and authorization work?
**Answer:** We use JWT authentication with `bcrypt` password hashing. Upon login (`POST /api/v1/auth/login`), a signed JWT carrying `sub` and `role` claims is issued. Endpoints use FastAPI dependency `require_roles` to enforce Role-Based Access Control (`CUSTOMER`, `ANALYST`, `ADMIN`).

### Q: What does your CI/CD pipeline do?
**Answer:** Our GitHub Actions workflow (`.github/workflows/ci-cd.yml`) triggers on every push and PR. It installs dependencies, generates synthetic data, trains the ML model, runs Pytest unit & security tests, builds the React TypeScript bundle (`npm run build`), and builds Docker images.

---

## 6. Behavioral & Engineering Mindset

### Q: What was the hardest technical challenge in building FinGuard?
**Answer:** Balancing the trade-off between ML inference speed and real-time API response latency. Loading Scikit-Learn models on every incoming transaction would cause heavy disk I/O. We solved this by implementing a **Singleton Model Loader Service** (`MLModelService`) that loads joblib artifacts into memory once at server startup (FastAPI lifespan), reducing model scoring latency to $<1.5\text{ms}$.
