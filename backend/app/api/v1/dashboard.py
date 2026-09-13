from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.domain import (
    Transaction, RiskScore, FraudAlert, Investigation, Merchant, Customer, User, UserRole,
    TransactionStatus, RiskLevel, AlertStatus, InvestigationDecision
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Statistics"])

@router.get("/statistics")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get executive banking fraud statistics or customer-scoped statistics for dashboard.
    """
    tx_query = db.query(Transaction)
    risk_query = db.query(RiskScore)
    alert_query = db.query(FraudAlert)
    inv_query = db.query(Investigation)

    # If user is a CUSTOMER, scope statistics strictly to their customer profile
    if current_user.role == UserRole.CUSTOMER.value:
        cust = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if cust:
            tx_query = tx_query.filter(Transaction.customer_id == cust.id)
            risk_query = risk_query.join(Transaction).filter(Transaction.customer_id == cust.id)
            alert_query = alert_query.join(Transaction).filter(Transaction.customer_id == cust.id)
            inv_query = inv_query.join(Transaction).filter(Transaction.customer_id == cust.id)
        else:
            return {
                "kpis": {
                    "total_transactions": 0, "total_value": 0.0, "flagged_transactions": 0,
                    "high_risk_transactions": 0, "fraud_rate_percentage": 0.0,
                    "pending_investigations": 0, "confirmed_fraud": 0, "legitimate_transactions": 0
                },
                "charts": {"risk_distribution": [], "category_distribution": []}
            }

    total_transactions = tx_query.with_entities(func.count(Transaction.id)).scalar() or 0
    total_value = tx_query.with_entities(func.sum(Transaction.amount)).scalar() or 0.0

    flagged_count = tx_query.filter(Transaction.status == TransactionStatus.FLAGGED.value).with_entities(func.count(Transaction.id)).scalar() or 0
    high_risk_count = risk_query.filter(RiskScore.risk_level == RiskLevel.HIGH.value).with_entities(func.count(RiskScore.id)).scalar() or 0
    medium_risk_count = risk_query.filter(RiskScore.risk_level == RiskLevel.MEDIUM.value).with_entities(func.count(RiskScore.id)).scalar() or 0
    low_risk_count = risk_query.filter(RiskScore.risk_level == RiskLevel.LOW.value).with_entities(func.count(RiskScore.id)).scalar() or 0

    pending_alerts_count = alert_query.filter(FraudAlert.status == AlertStatus.NEW.value).with_entities(func.count(FraudAlert.id)).scalar() or 0
    
    confirmed_fraud_count = (
        inv_query
        .filter(Investigation.decision == InvestigationDecision.CONFIRMED_FRAUD.value)
        .with_entities(func.count(Investigation.id))
        .scalar() or 0
    )
    legitimate_count = (
        inv_query
        .filter(Investigation.decision == InvestigationDecision.LEGITIMATE.value)
        .with_entities(func.count(Investigation.id))
        .scalar() or 0
    )

    fraud_rate_pct = round((flagged_count / max(1, total_transactions)) * 100.0, 2)

    # Risk Level Distribution for Donut Chart
    risk_distribution = [
        {"name": "LOW", "value": low_risk_count, "color": "#10B981"},
        {"name": "MEDIUM", "value": medium_risk_count, "color": "#F59E0B"},
        {"name": "HIGH", "value": high_risk_count, "color": "#EF4444"}
    ]

    # Category Breakdown
    category_query = (
        db.query(Merchant.category, func.count(Transaction.id).label("count"))
        .join(Transaction, Transaction.merchant_id == Merchant.id)
    )
    if current_user.role == UserRole.CUSTOMER.value:
        cust = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if cust:
            category_query = category_query.filter(Transaction.customer_id == cust.id)

    category_stats_query = category_query.group_by(Merchant.category).all()
    category_distribution = [{"category": cat, "count": cnt} for cat, cnt in category_stats_query]

    return {
        "kpis": {
            "total_transactions": total_transactions,
            "total_value": round(total_value, 2),
            "flagged_transactions": flagged_count,
            "high_risk_transactions": high_risk_count,
            "fraud_rate_percentage": fraud_rate_pct,
            "pending_investigations": pending_alerts_count,
            "confirmed_fraud": confirmed_fraud_count,
            "legitimate_transactions": legitimate_count
        },
        "charts": {
            "risk_distribution": risk_distribution,
            "category_distribution": category_distribution
        }
    }
