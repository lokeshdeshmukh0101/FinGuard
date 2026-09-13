# FinGuard Engineering Trade-Offs & Architecture Decisions

## 1. Why FastAPI over Django / Flask?
- **Asynchronous Execution & High Throughput**: FastAPI is built on Starlette and Asgi, delivering near-Go performance for I/O-bound banking API workloads.
- **Pydantic Validation**: Automatic request parsing, response serialization, and OpenAPI Swagger documentation without boilerplate.

## 2. Why Hybrid Fraud Engine (Rules + ML)?
- **Rules Only**: Fast and deterministic, but rigid. Easily bypassed by evolving fraud vectors.
- **Pure ML Only**: Captures complex non-linear patterns, but suffers from "cold start" (new rules take time to retrain models) and lacks instant explainability.
- **Hybrid Fusion**: Combines configurable rule guardrails ($S_{rule}$) with statistical model probability ($S_{ml}$) to yield a robust, explainable risk score from 0–100.

## 3. Why Modular Monolith over Microservices?
- For an intern/portfolio codebase, microservices introduce distributed network latency, gRPC/RPC overhead, complex distributed tracing, and multi-repo deployment complexity.
- A Modular Monolith establishes clean domain separation (`auth`, `transactions`, `rule_engine`, `ml_service`, `investigations`) within a unified repository while allowing easy future extraction into microservices if scaling requires.

## 4. Scalability & Evolution Path
- **Caching**: Add Redis cache for customer spending baselines (`average_transaction_amount`) and merchant risk indices to reduce DB read ops.
- **Message Queues**: Ingest transactions via Apache Kafka or RabbitMQ to decouple real-time scoring from asynchronous database writes.
- **Horizontal Scaling**: Backend FastAPI containers are 100% stateless and can scale horizontally behind an AWS Application Load Balancer (ALB).
