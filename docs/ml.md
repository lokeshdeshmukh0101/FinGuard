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
| **Logistic Regression (Baseline)** | 0.9995 | 1.0000 | 0.9863 | 0.9931 | 1.0000 |
| **Random Forest (Primary)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

## 4. Confusion Matrix (Random Forest)
- True Negatives (Legitimate correctly identified): 1927
- False Positives (False Alarms): 0
- False Negatives (Missed Fraud): 0
- True Positives (Fraud correctly detected): 73

## 5. Feature Importances
- `amount_ratio`: 34.64%
- `velocity_10m`: 24.57%
- `location_distance_km`: 23.78%
- `amount`: 8.52%
- `is_new_device`: 5.85%
- `merchant_risk_index`: 2.40%
- `customer_avg_amount`: 0.21%
- `hour`: 0.04%
