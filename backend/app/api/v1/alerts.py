from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.domain import FraudAlert, User, UserRole, AlertStatus, AuditLog
from app.schemas.domain import FraudAlertResponse, FraudAlertUpdate
from app.api.deps import require_roles

router = APIRouter(prefix="/alerts", tags=["Fraud Alerts"])

@router.get("", response_model=List[FraudAlertResponse])
def list_fraud_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    List fraud alerts (Analyst and Admin only).
    """
    query = db.query(FraudAlert)
    if status_filter:
        query = query.filter(FraudAlert.status == status_filter.upper())

    alerts = query.order_by(desc(FraudAlert.created_at)).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=FraudAlertResponse)
def get_fraud_alert_detail(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    Get detailed information for a specific fraud alert.
    """
    alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fraud alert not found.")
    return alert

@router.patch("/{alert_id}", response_model=FraudAlertResponse)
def update_fraud_alert_status(
    alert_id: str,
    alert_update: FraudAlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    Update fraud alert status (NEW -> UNDER_REVIEW -> RESOLVED).
    """
    alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fraud alert not found.")

    alert.status = alert_update.status.value
    if alert_update.status == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.utcnow()

    # Record Audit Log
    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_ALERT_STATUS",
        entity_type="FRAUD_ALERT",
        entity_id=alert.id,
        metadata_json={"new_status": alert.status}
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)

    return alert
