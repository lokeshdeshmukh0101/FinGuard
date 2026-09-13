# FinGuard Machine Learning & Explainable AI Evaluation Report

## 1. Overview
This report documents the machine learning pipeline used by FinGuard to detect fraudulent banking transactions.

## 2. Dataset & Feature Engineering
- **Total Transactions**: 10,000 synthetic records
- **Class Distribution**: ~3.5% Fraud (Imbalanced Binary Classification)
- **Features Included**:
  1. `amount`: Raw transaction value
  2. `customer_avg_amount`: Historical customer normal spending
  3. `amount_ratio`: Amount divided by historical average
  4. `velocity_10m`: Transaction count in sliding 10-minute window
  5. `location_distance_km`: Estimated distance from primary location
  6. `hour`: Transaction hour of day (0–23)
  7. `merchant_risk_index`: Risk rating of merchant category
  8. `is_new_device`: Binary indicator for unrecognised device

## 3. Model Comparison & Metrics

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| **Logistic Regression (Baseline)** | 0.9990 | 1.0000 | 0.9722 | 0.9859 | 1.0000 |
| **Random Forest (Primary)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

## 4. Confusion Matrix (Random Forest)
- True Negatives (Legitimate correctly identified): 964
- False Positives (False Alarms): 0
- False Negatives (Missed Fraud): 0
- True Positives (Fraud correctly detected): 36

## 5. Feature Importances
- `amount_ratio`: 34.12%
- `velocity_10m`: 25.89%
- `location_distance_km`: 23.17%
- `amount`: 8.58%
- `is_new_device`: 4.33%
- `merchant_risk_index`: 3.75%
- `customer_avg_amount`: 0.11%
- `hour`: 0.04%
