from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models.domain import RiskScore, Transaction, Customer, User, UserRole
from app.api.deps import get_current_user
from app.services.xai_service import generate_xai_explanation

router = APIRouter(prefix="/risk", tags=["Risk Analysis & XAI"])

@router.get("/{transaction_id}")
def get_transaction_risk_explanation(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve granular Risk Score and Explainable AI (XAI) reason codes for a transaction.
    - Customers can only view risk explanations for their own transactions.
    - Analysts and Admins can view any transaction explanation.
    """
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    if current_user.role == UserRole.CUSTOMER.value:
        cust = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not cust or tx.customer_id != cust.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view risk score explanations for this transaction."
            )

    risk_record = db.query(RiskScore).filter(RiskScore.transaction_id == transaction_id).first()
    if not risk_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk record not found for this transaction.")

    explanation = generate_xai_explanation(risk_record)
    return explanation
