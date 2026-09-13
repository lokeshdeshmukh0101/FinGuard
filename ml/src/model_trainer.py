import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

FEATURE_COLUMNS = [
    "amount",
    "customer_avg_amount",
    "amount_ratio",
    "velocity_10m",
    "location_distance_km",
    "hour",
    "merchant_risk_index",
    "is_new_device"
]
TARGET_COLUMN = "is_fraud"

def train_and_evaluate_models(data_path: str, model_output_path: str) -> Dict[str, Any]:
    print(f"Loading synthetic dataset from {data_path}...")
    df = pd.read_csv(data_path)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # Train / Test Stratified Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Baseline Model: Logistic Regression
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train_scaled, y_train)
    lr_preds = lr_model.predict(X_test_scaled)
    lr_probs = lr_model.predict_proba(X_test_scaled)[:, 1]

    # 2. Primary Model: Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )
    rf_model.fit(X_train_scaled, y_train)
    rf_preds = rf_model.predict(X_test_scaled)
    rf_probs = rf_model.predict_proba(X_test_scaled)[:, 1]

    # Evaluate Random Forest Metrics
    rf_metrics = {
        "accuracy": float(accuracy_score(y_test, rf_preds)),
        "precision": float(precision_score(y_test, rf_preds, zero_division=0)),
        "recall": float(recall_score(y_test, rf_preds, zero_division=0)),
        "f1": float(f1_score(y_test, rf_preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, rf_probs)),
        "confusion_matrix": confusion_matrix(y_test, rf_preds).tolist()
    }

    lr_metrics = {
        "accuracy": float(accuracy_score(y_test, lr_preds)),
        "precision": float(precision_score(y_test, lr_preds, zero_division=0)),
        "recall": float(recall_score(y_test, lr_preds, zero_division=0)),
        "f1": float(f1_score(y_test, lr_preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, lr_probs)),
        "confusion_matrix": confusion_matrix(y_test, lr_preds).tolist()
    }

    # Save Pipeline (Scaler + Random Forest Model + Feature Names)
    pipeline_artifact = {
        "scaler": scaler,
        "model": rf_model,
        "feature_names": FEATURE_COLUMNS,
        "feature_importances": dict(zip(FEATURE_COLUMNS, rf_model.feature_importances_.tolist())),
        "metrics": rf_metrics
    }

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(pipeline_artifact, model_output_path)
    print(f"Model pipeline artifact serialized to '{model_output_path}'")

    return {
        "logistic_regression": lr_metrics,
        "random_forest": rf_metrics,
        "feature_importances": pipeline_artifact["feature_importances"]
    }
