from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.domain import (
    Transaction, RiskScore, FraudAlert, Investigation, Merchant, User, UserRole,
    TransactionStatus, RiskLevel, AlertStatus, InvestigationDecision
)
from app.api.deps import require_roles

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Statistics"])

@router.get("/statistics")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
) -> Dict[str, Any]:
    """
    Get executive banking fraud statistics, KPI cards, and charts data for analyst dashboard.
    """
    total_transactions = db.query(func.count(Transaction.id)).scalar() or 0
    total_value = db.query(func.sum(Transaction.amount)).scalar() or 0.0

    flagged_count = db.query(func.count(Transaction.id)).filter(Transaction.status == TransactionStatus.FLAGGED.value).scalar() or 0
    high_risk_count = db.query(func.count(RiskScore.id)).filter(RiskScore.risk_level == RiskLevel.HIGH.value).scalar() or 0
    medium_risk_count = db.query(func.count(RiskScore.id)).filter(RiskScore.risk_level == RiskLevel.MEDIUM.value).scalar() or 0
    low_risk_count = db.query(func.count(RiskScore.id)).filter(RiskScore.risk_level == RiskLevel.LOW.value).scalar() or 0

    pending_alerts_count = db.query(func.count(FraudAlert.id)).filter(FraudAlert.status == AlertStatus.NEW.value).scalar() or 0
    
    confirmed_fraud_count = (
        db.query(func.count(Investigation.id))
        .filter(Investigation.decision == InvestigationDecision.CONFIRMED_FRAUD.value)
        .scalar() or 0
    )
    legitimate_count = (
        db.query(func.count(Investigation.id))
        .filter(Investigation.decision == InvestigationDecision.LEGITIMATE.value)
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
    category_stats_query = (
        db.query(Merchant.category, func.count(Transaction.id).label("count"))
        .join(Transaction, Transaction.merchant_id == Merchant.id)
        .group_by(Merchant.category)
        .all()
    )
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
