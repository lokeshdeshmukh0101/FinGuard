# FinGuard Data Structures & Algorithms (DSA) Specifications

This document outlines the core algorithms and data structures implemented in FinGuard for interview explanation and algorithmic rigor.

## 1. Sliding Window Transaction Velocity Engine

### Problem Statement
Fraudsters often execute multiple rapid transactions within short windows (e.g. 5 transactions in 10 minutes) after compromising a card or account credentials.

### Algorithm & Data Structure
- **Data Structure**: Sliding Window Deque / Queue (Timestamped Event Stream) & Hash Maps.
- **Approach**: For customer $C_i$ with transaction history timestamp queue $Q$, upon arrival of new transaction $T_new$ at time $t_{new}$:
  1. Pop elements from head of queue $Q$ where $t < (t_{new} - W)$ for time window $W \in \{10\text{ min}, 1\text{ hr}, 24\text{ hr}\}$.
  2. Push $t_{new}$ to tail of queue.
  3. Size of queue $|Q|$ yields exact transaction velocity count in interval $[t_{new} - W, t_{new}]$.
- **Time Complexity**: $\mathcal{O}(k)$ amortized where $k$ is the number of expired transactions popped (each transaction pushed and popped at most once). Average time per transaction check is $\mathcal{O}(1)$.
- **Space Complexity**: $\mathcal{O}(N)$ where $N$ is the number of active transactions within the max window $W_{max} = 24\text{ hours}$.

---

## 2. In-Memory Hash Map Lookup for Customer Spending Baselines

### Problem Statement
Real-time transaction risk scoring requires instantaneous retrieval of customer historical averages and primary locations without incurring DB bottleneck latencies on every API call.

### Algorithm & Data Structure
- **Data Structure**: Hash Map / Dictionary (`Dict[UUID, CustomerProfile]`).
- **Approach**: Direct key lookup on `customer_id`.
- **Time Complexity**: Average case $\mathcal{O}(1)$ lookup and update. Worst case $\mathcal{O}(n)$ hash collision.
- **Space Complexity**: $\mathcal{O}(C)$ where $C$ is the number of active customer profiles cached.

---

## 3. Weighted Risk Score Normalization & Categorization

### Algorithm
1. Compute Rule Risk Score $S_{rule} \in [0, 100]$.
2. Compute ML Model Fraud Probability $P_{ml} \in [0.0, 1.0]$, scale to $S_{ml} = P_{ml} \times 100$.
3. Compute Hybrid Score:
   $$S_{final} = \min\left(100.0, \, (w_{rule} \cdot S_{rule}) + (w_{ml} \cdot S_{ml})\right)$$
4. Classify via Threshold Function:
   $$\text{RiskLevel}(S) = \begin{cases} \text{LOW} & 0 \le S < 40 \\ \text{MEDIUM} & 40 \le S < 70 \\ \text{HIGH} & 70 \le S \le 100 \end{cases}$$
- **Time Complexity**: $\mathcal{O}(1)$ arithmetic and branch operations.
- **Space Complexity**: $\mathcal{O}(1)$.
