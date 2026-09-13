from typing import Dict, Any, List
from app.models.domain import RiskScore, Transaction, Customer, Merchant

def generate_xai_explanation(risk_record: RiskScore) -> Dict[str, Any]:
    """
    Generates granular XAI breakdown with human-readable contributing factors and point weights.
    """
    breakdown = risk_record.breakdown or {}
    reasons = breakdown.get("reasons", [])
    rule_details = breakdown.get("rule_details", {})
    ml_contributions = breakdown.get("ml_contributions", {})

    contributing_factors = []
    
    # 1. Format Rule Reasons with point contributions
    if rule_details.get("amount_ratio", 1.0) >= 4.0:
        contributing_factors.append({
            "factor": "Unusually High Amount",
            "weight": "+35 pts",
            "description": f"Transaction amount is {rule_details['amount_ratio']}x customer's normal average"
        })
    elif rule_details.get("amount_ratio", 1.0) >= 2.5:
        contributing_factors.append({
            "factor": "Elevated Amount",
            "weight": "+20 pts",
            "description": f"Transaction amount is {rule_details['amount_ratio']}x customer's normal average"
        })

    if rule_details.get("velocity_count_10m", 0) >= 4:
        contributing_factors.append({
            "factor": "High Transaction Velocity",
            "weight": "+30 pts",
            "description": f"{rule_details['velocity_count_10m']} transactions detected within 10-minute window"
        })
    elif rule_details.get("velocity_count_10m", 0) >= 2:
        contributing_factors.append({
            "factor": "Elevated Velocity",
            "weight": "+15 pts",
            "description": f"{rule_details['velocity_count_10m']} transactions detected within 10-minute window"
        })

    if rule_details.get("location_mismatch", False):
        contributing_factors.append({
            "factor": "Unusual Location Anomaly",
            "weight": "+25 pts",
            "description": "Transaction location differs significantly from customer's home region"
        })

    if "tx_hour" in rule_details and 0 <= rule_details["tx_hour"] <= 5:
        contributing_factors.append({
            "factor": "Unusual Hour",
            "weight": "+15 pts",
            "description": f"Transaction initiated during high-risk window ({rule_details['tx_hour']:02d}:00)"
        })

    if rule_details.get("merchant_category") in ["CRYPTO", "JEWELRY", "GAMBLING"]:
        contributing_factors.append({
            "factor": "High-Risk Merchant Category",
            "weight": "+20 pts",
            "description": f"Merchant category '{rule_details['merchant_category']}' flagged as high risk"
        })

    if not contributing_factors:
        contributing_factors.append({
            "factor": "Normal Behavioral Patterns",
            "weight": "0 pts",
            "description": "All monitored risk metrics are within normal customer baselines"
        })

    return {
        "transaction_id": risk_record.transaction_id,
        "final_risk_score": risk_record.score,
        "risk_level": risk_record.risk_level,
        "rule_score": risk_record.rule_score,
        "model_probability": risk_record.model_score,
        "contributing_factors": contributing_factors,
        "raw_reasons": reasons,
        "ml_feature_contributions": ml_contributions
    }
