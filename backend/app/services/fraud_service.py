import uuid
from datetime import datetime
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.domain import (
    Transaction, Customer, Merchant, RiskScore, FraudAlert, AuditLog,
    TransactionStatus, RiskLevel, AlertStatus
)
from app.schemas.domain import TransactionEvaluationResponse
from app.services.rule_engine import default_rule_engine
from app.services.ml_service import ml_service

def calculate_location_distance(norm_loc: str, curr_loc: str) -> float:
    if not norm_loc or not curr_loc:
        return 0.0
    if norm_loc.strip().lower() == curr_loc.strip().lower():
        return 0.0
    return 2500.0 # Estimated cross-city / international distance indicator

def calculate_merchant_risk(category: str) -> float:
    cat = category.upper()
    if cat in ["CRYPTO", "JEWELRY", "GAMBLING"]:
        return 0.85
    elif cat in ["E-COMMERCE", "ELECTRONICS"]:
        return 0.45
    return 0.10

def evaluate_and_process_transaction(
    db: Session,
    customer: Customer,
    merchant: Merchant,
    amount: float,
    location: str,
    device_id: str,
    tx_time: datetime,
    user_id: str
) -> TransactionEvaluationResponse:
    """
    Main orchestration service for real-time transaction risk scoring & fraud detection.
    Combines:
    1. Configurable Rule Engine score (0 - 100)
    2. ML Model prediction probability (0.0 - 1.0)
    3. Hybrid Score Fusion & Risk Classification
    """
    # 1. Calculate Rule Engine Score
    rule_score, reasons, rule_details = default_rule_engine.evaluate(
        db, customer, merchant, amount, location, device_id, tx_time
    )

    # 2. Extract ML Features & Compute ML Probability
    avg_amt = max(customer.average_transaction_amount or 100.0, 1.0)
    amount_ratio = amount / avg_amt
    velocity_10m = rule_details.get("velocity_count_10m", 0)
    loc_distance = calculate_location_distance(customer.normal_location, location)
    merchant_risk = calculate_merchant_risk(merchant.category)
    
    # Check if device is new for customer
    previous_device_count = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer.id)
        .filter(Transaction.device_id == device_id)
        .count()
    )
    is_new_device = 1 if previous_device_count == 0 else 0

    ml_prob, ml_contributions = ml_service.predict_fraud_probability(
        amount=amount,
        customer_avg_amount=avg_amt,
        amount_ratio=amount_ratio,
        velocity_10m=velocity_10m,
        location_distance_km=loc_distance,
        hour=tx_time.hour,
        merchant_risk_index=merchant_risk,
        is_new_device=is_new_device
    )
    model_score = ml_prob # Scale 0.0 - 1.0

    # 3. Compute Hybrid Weighted Risk Score (0 - 100)
    final_score = int(min(100, round(
        (settings.RULE_WEIGHT * rule_score) + (settings.ML_WEIGHT * (model_score * 100.0))
    )))

    # 4. Classify Risk Level
    if final_score >= settings.RISK_THRESHOLD_HIGH:
        risk_level = RiskLevel.HIGH
        status = TransactionStatus.FLAGGED
    elif final_score >= settings.RISK_THRESHOLD_MEDIUM:
        risk_level = RiskLevel.MEDIUM
        status = TransactionStatus.APPROVED
    else:
        risk_level = RiskLevel.LOW
        status = TransactionStatus.APPROVED

    # 5. Create Transaction Record
    tx = Transaction(
        customer_id=customer.id,
        merchant_id=merchant.id,
        amount=amount,
        location=location,
        device_id=device_id,
        transaction_time=tx_time,
        status=status.value
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # 6. Record Risk Score
    risk_record = RiskScore(
        transaction_id=tx.id,
        score=final_score,
        risk_level=risk_level.value,
        model_score=model_score,
        rule_score=rule_score,
        breakdown={
            "reasons": reasons,
            "rule_details": rule_details,
            "ml_contributions": ml_contributions,
            "rule_score": rule_score,
            "model_score": model_score
        }
    )
    db.add(risk_record)

    # 7. Create Fraud Alert if HIGH risk
    if risk_level == RiskLevel.HIGH:
        alert_reason = "; ".join(reasons) if reasons else f"High risk score ({final_score}) flagged by ML & Rule engine."
        alert = FraudAlert(
            transaction_id=tx.id,
            severity=RiskLevel.HIGH.value,
            reason=alert_reason,
            status=AlertStatus.NEW.value
        )
        db.add(alert)

    # 8. Create Audit Log
    audit = AuditLog(
        user_id=user_id,
        action="PROCESS_TRANSACTION",
        entity_type="TRANSACTION",
        entity_id=tx.id,
        metadata_json={
            "amount": amount,
            "risk_score": final_score,
            "risk_level": risk_level.value,
            "status": status.value,
            "ml_prob": round(ml_prob, 4)
        }
    )
    db.add(audit)
    db.commit()

    return TransactionEvaluationResponse(
        transaction_id=tx.id,
        risk_score=final_score,
        risk_level=risk_level,
        status=status,
        reasons=reasons if reasons else ["Transaction within normal parameters"],
        model_score=model_score,
        rule_score=rule_score
    )
