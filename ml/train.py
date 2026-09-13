import argparse
import os
import sys

# Ensure ml directory is on sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.model_trainer import train_and_evaluate_models

def main():
    parser = argparse.ArgumentParser(description="FinGuard ML Model Training Pipeline")
    parser.add_argument("--data", type=str, default="ml/data/synthetic_transactions.csv", help="Input synthetic dataset CSV")
    parser.add_argument("--output", type=str, default="ml/models/fraud_detector_v1.joblib", help="Model artifact destination")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: Dataset path '{args.data}' does not exist. Run scripts/generate_data.py first.")
        sys.exit(1)

    print("Executing FinGuard Model Training Pipeline...")
    results = train_and_evaluate_models(args.data, args.output)

    rf_m = results["random_forest"]
    lr_m = results["logistic_regression"]

    print("\n================ ML EVALUATION METRICS ================")
    print("Baseline Model (Logistic Regression):")
    print(f"  Accuracy  : {lr_m['accuracy']:.4f}")
    print(f"  Precision : {lr_m['precision']:.4f}")
    print(f"  Recall    : {lr_m['recall']:.4f}")
    print(f"  F1-Score  : {lr_m['f1']:.4f}")
    print(f"  ROC-AUC   : {lr_m['roc_auc']:.4f}")

    print("\nPrimary Model (Random Forest Classifier):")
    print(f"  Accuracy  : {rf_m['accuracy']:.4f}")
    print(f"  Precision : {rf_m['precision']:.4f}")
    print(f"  Recall    : {rf_m['recall']:.4f}")
    print(f"  F1-Score  : {rf_m['f1']:.4f}")
    print(f"  ROC-AUC   : {rf_m['roc_auc']:.4f}")
    print("========================================================\n")

    # Generate docs/ml.md
    doc_path = "docs/ml.md"
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    with open(doc_path, "w") as f:
        f.write(f"""# FinGuard Machine Learning & Explainable AI Evaluation Report

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
| **Logistic Regression (Baseline)** | {lr_m['accuracy']:.4f} | {lr_m['precision']:.4f} | {lr_m['recall']:.4f} | {lr_m['f1']:.4f} | {lr_m['roc_auc']:.4f} |
| **Random Forest (Primary)** | **{rf_m['accuracy']:.4f}** | **{rf_m['precision']:.4f}** | **{rf_m['recall']:.4f}** | **{rf_m['f1']:.4f}** | **{rf_m['roc_auc']:.4f}** |

## 4. Confusion Matrix (Random Forest)
- True Negatives (Legitimate correctly identified): {rf_m['confusion_matrix'][0][0]}
- False Positives (False Alarms): {rf_m['confusion_matrix'][0][1]}
- False Negatives (Missed Fraud): {rf_m['confusion_matrix'][1][0]}
- True Positives (Fraud correctly detected): {rf_m['confusion_matrix'][1][1]}

## 5. Feature Importances
""")
        for feat, imp in sorted(results["feature_importances"].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- `{feat}`: {imp*100:.2f}%\n")

    print(f"ML evaluation documentation created at '{doc_path}'")

if __name__ == "__main__":
    main()
