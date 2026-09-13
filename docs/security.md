# FinGuard Security Architecture & Controls

## 1. Overview
FinGuard is engineered with enterprise cybersecurity principles to ensure data confidentiality, integrity, availability, and strict role-based authorization.

## 2. Security Mechanisms Implemented

### A. Authentication & Password Hashing
- **Algorithm**: `bcrypt` password hashing with automatic salt generation and maximum 72-byte password truncation safeguard.
- **Tokens**: JSON Web Tokens (JWT) signed using `HMAC-SHA256` (`HS256`). Tokens carry expiration timestamps (`exp`), subject user ID (`sub`), and role claims (`role`).

### B. Role-Based Access Control (RBAC)
- Enforces 3 strict security roles via FastAPI dependency injection (`require_roles` middleware):
  1. `CUSTOMER`: Access restricted exclusively to own profile and own transaction history. Cannot inspect alerts or audit logs.
  2. `ANALYST`: Access to fraud alerts, risk scores, XAI reason codes, and investigation decisions.
  3. `ADMIN`: Full system administrative access, user management, system metrics, and audit log inspection.

### C. Injection Prevention & ORM Parameterization
- All SQL queries execute through SQLAlchemy ORM parameterization. Raw string concatenation in SQL queries is strictly prohibited to guarantee protection against SQL Injection (SQLi) vulnerabilities.

### D. API Validation & Error Masking
- Pydantic schemas enforce type validation on all incoming JSON payloads. Invalid inputs return standard `422 Unprocessable Entity` responses without revealing internal stack traces, database schema details, or system credentials.

### E. Audit Logging
- Every sensitive operation (`LOGIN`, `PROCESS_TRANSACTION`, `SUBMIT_INVESTIGATION`, `UPDATE_ALERT_STATUS`) writes an immutable record to the `audit_logs` database table.
