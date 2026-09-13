from prometheus_client import Counter, Histogram

# HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "finguard_http_requests_total",
    "Total HTTP requests received by FinGuard API",
    ["method", "endpoint", "status"]
)

HTTP_LATENCY_SECONDS = Histogram(
    "finguard_http_latency_seconds",
    "HTTP request duration in seconds",
    ["endpoint"]
)

# Domain Specific Metrics
TRANSACTIONS_EVALUATED_TOTAL = Counter(
    "finguard_transactions_evaluated_total",
    "Total transactions evaluated by risk engine",
    ["risk_level", "status"]
)

FRAUD_ALERTS_GENERATED_TOTAL = Counter(
    "finguard_fraud_alerts_generated_total",
    "Total high severity fraud alerts generated"
)
