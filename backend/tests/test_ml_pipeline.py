import os
import pytest
import pandas as pd
import joblib

# Dynamically resolve root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "ml", "data", "synthetic_transactions.csv")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "fraud_detector_v1.joblib")

def test_synthetic_dataset_exists():
    assert os.path.exists(DATA_PATH), f"Synthetic dataset not found at {DATA_PATH}"
    df = pd.read_csv(DATA_PATH)
    assert len(df) >= 1000
    assert "is_fraud" in df.columns
    assert "amount_ratio" in df.columns
    assert df["is_fraud"].sum() > 0

def test_model_artifact_load_and_predict():
    assert os.path.exists(MODEL_PATH), f"Model artifact not found at {MODEL_PATH}"
    artifact = joblib.load(MODEL_PATH)
    assert "scaler" in artifact
    assert "model" in artifact
    assert "feature_names" in artifact
    
    scaler = artifact["scaler"]
    model = artifact["model"]
    
    sample_df = pd.DataFrame([{
        "amount": 500.0,
        "customer_avg_amount": 100.0,
        "amount_ratio": 5.0,
        "velocity_10m": 4,
        "location_distance_km": 2500.0,
        "hour": 2,
        "merchant_risk_index": 0.8,
        "is_new_device": 1
    }])
    
    scaled_sample = scaler.transform(sample_df)
    prob = float(model.predict_proba(scaled_sample)[0][1])
    assert 0.0 <= prob <= 1.0
