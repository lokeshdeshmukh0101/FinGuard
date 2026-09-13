# FinGuard AWS Cloud Deployment Guide & Infrastructure Architecture

## 1. AWS Cloud Architecture Topology

```
[ End Users / Fraud Analysts ]
               │
               ▼ (HTTPS / DNS Route 53)
[ AWS CloudFront CDN ] ──► [ Amazon S3 Static Bucket ] (React + Vite SPA)
               │
               ▼ (API Requests: /api/v1/*)
[ AWS Application Load Balancer (ALB) ]
               │
               ▼ (VPC Public Subnets)
[ AWS App Runner / ECS Fargate Container Cluster ]
  └── FinGuard FastAPI Containers (Auto-scaling 2 to 10 tasks)
               │
               ▼ (VPC Private Isolated Subnets)
[ Amazon RDS PostgreSQL (Multi-AZ) ] ◄── Encrypted DB Data Volume
               │
               ▼
[ AWS CloudWatch Logs & Amazon Managed Prometheus / Grafana ]
```

## 2. Infrastructure Component Specifications

| Service | Configuration | Justification & Production Strategy |
|---|---|---|
| **Frontend** | Amazon S3 + CloudFront CDN | Edge caching ensures <50ms global latency for static React assets with zero server maintenance costs. |
| **API Backend** | AWS App Runner or ECS Fargate | Fully managed container runtime. Automatically scales FastAPI containers based on incoming HTTP request volume. |
| **Database** | Amazon RDS PostgreSQL 16 (db.t4g.micro) | Managed relational database providing automated daily backups, point-in-time recovery, and multi-AZ replication. |
| **Secrets & Keys** | AWS Secrets Manager | Securely stores JWT signing keys, DB credentials, and TLS certificates without hardcoding in git repositories. |
| **Monitoring** | Amazon CloudWatch | Captures application logs, API response latency, 4xx/5xx error spikes, and container health metrics. |

---

## 3. Step-by-Step Production Deployment Instructions

### Step 1: Provision Database on Amazon RDS
```bash
aws rds create-db-instance \
  --db-instance-identifier finguard-db-prod \
  --db-instance-class db.t4g.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password "STRONG_PROD_PASSWORD_HERE" \
  --allocated-storage 20
```

### Step 2: Build & Push Docker Container to AWS ECR
```bash
# Authenticate Docker to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build & Tag Backend Image
docker build -t finguard-backend -f Dockerfile.backend .
docker tag finguard-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/finguard-backend:latest

# Push Image to AWS ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/finguard-backend:latest
```

### Step 3: Deploy AWS App Runner Service
```bash
aws apprunner create-service \
  --service-name finguard-api-service \
  --source-configuration ImageRepository={ImageIdentifier=123456789012.dkr.ecr.us-east-1.amazonaws.com/finguard-backend:latest,ImageRepositoryType=ECR}
```

### Step 4: Deploy Frontend to S3 & CloudFront
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://finguard-frontend-prod-bucket --delete
aws cloudfront create-invalidation --distribution-id E1234567890 --paths "/*"
```
