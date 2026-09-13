import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from app.core.config import settings

class MLModelService:
    _instance: Optional['MLModelService'] = None

    def __init__(self):
        self.scaler = None
        self.model = None
        self.feature_names = []
        self.feature_importances = {}
        self.is_loaded = False
        self.load_model()

    @classmethod
    def get_instance(cls) -> 'MLModelService':
        if cls._instance is None:
            cls._instance = MLModelService()
        return cls._instance

    def load_model(self, model_path: Optional[str] = None):
        target_path = model_path or settings.MODEL_PATH
        # Convert relative path relative to project root
        if not os.path.isabs(target_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            target_path = os.path.join(base_dir, target_path.replace("../", ""))

        if os.path.exists(target_path):
            try:
                artifact = joblib.load(target_path)
                self.scaler = artifact.get("scaler")
                self.model = artifact.get("model")
                self.feature_names = artifact.get("feature_names", [])
                self.feature_importances = artifact.get("feature_importances", {})
                self.is_loaded = True
                print(f"[MLModelService] Successfully loaded ML model pipeline from '{target_path}'")
            except Exception as e:
                print(f"[MLModelService] Error loading ML model from '{target_path}': {e}")
                self.is_loaded = False
        else:
            print(f"[MLModelService] Model file not found at '{target_path}'. Using rule-based fallback.")
            self.is_loaded = False

    def predict_fraud_probability(
        self,
        amount: float,
        customer_avg_amount: float,
        amount_ratio: float,
        velocity_10m: int,
        location_distance_km: float,
        hour: int,
        merchant_risk_index: float,
        is_new_device: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Extracts features, scales inputs, runs inference, and returns (fraud_probability_0_1, feature_contributions).
        """
        if not self.is_loaded or self.model is None or self.scaler is None:
            # Fallback estimation based on feature heuristics
            estimated_prob = min(1.0, max(0.0, (amount_ratio * 0.15) + (velocity_10m * 0.1) + merchant_risk_index * 0.2))
            return float(estimated_prob), {}

        features_df = pd.DataFrame([{
            "amount": float(amount),
            "customer_avg_amount": float(customer_avg_amount),
            "amount_ratio": float(amount_ratio),
            "velocity_10m": int(velocity_10m),
            "location_distance_km": float(location_distance_km),
            "hour": int(hour),
            "merchant_risk_index": float(merchant_risk_index),
            "is_new_device": int(is_new_device)
        }])

        scaled_features = self.scaler.transform(features_df)
        prob = float(self.model.predict_proba(scaled_features)[0][1])

        # Compute feature contribution weights
        contributions = {}
        for col, imp in self.feature_importances.items():
            val = features_df[col].iloc[0]
            contributions[col] = round(float(imp * val), 4)

        return prob, contributions


ml_service = MLModelService.get_instance()
