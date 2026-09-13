from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.domain import (
    Investigation, Transaction, FraudAlert, AuditLog, User, UserRole,
    InvestigationDecision, AlertStatus, TransactionStatus
)
from app.schemas.domain import InvestigationCreate, InvestigationResponse
from app.api.deps import require_roles

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def submit_investigation(
    inv_in: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    Submit analyst investigation decision (LEGITIMATE, CONFIRMED_FRAUD, UNDER_REVIEW) with notes.
    - Automatically updates related transaction and fraud alert statuses.
    - Records comprehensive audit trail.
    """
    tx = db.query(Transaction).filter(Transaction.id == inv_in.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    # Create investigation record
    investigation = Investigation(
        transaction_id=tx.id,
        analyst_id=current_user.id,
        decision=inv_in.decision.value,
        notes=inv_in.notes
    )
    db.add(investigation)

    # Update Transaction and Alert statuses based on Decision
    if inv_in.decision == InvestigationDecision.CONFIRMED_FRAUD:
        tx.status = TransactionStatus.REJECTED.value
    elif inv_in.decision == InvestigationDecision.LEGITIMATE:
        tx.status = TransactionStatus.APPROVED.value

    # Update associated alerts if any
    alert = db.query(FraudAlert).filter(FraudAlert.transaction_id == tx.id).first()
    if alert:
        if inv_in.decision in [InvestigationDecision.CONFIRMED_FRAUD, InvestigationDecision.LEGITIMATE]:
            alert.status = AlertStatus.RESOLVED.value
            alert.resolved_at = datetime.utcnow()
        elif inv_in.decision == InvestigationDecision.UNDER_REVIEW:
            alert.status = AlertStatus.UNDER_REVIEW.value

    # Record Audit Log
    audit = AuditLog(
        user_id=current_user.id,
        action="SUBMIT_INVESTIGATION",
        entity_type="INVESTIGATION",
        entity_id=tx.id,
        metadata_json={
            "decision": inv_in.decision.value,
            "notes": inv_in.notes,
            "analyst_email": current_user.email
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(investigation)

    return investigation

@router.get("/transaction/{transaction_id}", response_model=List[InvestigationResponse])
def get_transaction_investigations(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    Get full investigation note history for a transaction.
    """
    investigations = (
        db.query(Investigation)
        .filter(Investigation.transaction_id == transaction_id)
        .order_by(desc(Investigation.created_at))
        .all()
    )
    return investigations
