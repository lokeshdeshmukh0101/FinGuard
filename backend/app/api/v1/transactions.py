from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.domain import Transaction, Customer, Merchant, User, UserRole, TransactionStatus, RiskLevel, RiskScore
from app.schemas.domain import TransactionCreate, TransactionResponse, TransactionEvaluationResponse
from app.api.deps import get_current_user, require_roles
from app.services.fraud_service import evaluate_and_process_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionEvaluationResponse, status_code=status.HTTP_201_CREATED)
def process_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process an incoming banking transaction through the real-time fraud risk engine.
    - Validates customer and merchant existence.
    - Performs rule-based fraud detection & ML risk scoring.
    - Updates transaction status (APPROVED / FLAGGED / REJECTED).
    - Generates Fraud Alert if HIGH risk.
    - Records audit log entry.
    """
    customer = db.query(Customer).filter(Customer.id == tx_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
        
    merchant = db.query(Merchant).filter(Merchant.id == tx_in.merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found.")

    # Enforce customer self-creation restrictions unless Analyst/Admin
    if current_user.role == UserRole.CUSTOMER.value and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot submit transactions on behalf of another customer."
        )

    result = evaluate_and_process_transaction(
        db=db,
        customer=customer,
        merchant=merchant,
        amount=tx_in.amount,
        location=tx_in.location,
        device_id=tx_in.device_id,
        tx_time=tx_in.transaction_time or datetime.utcnow(),
        user_id=current_user.id
    )
    
    return result

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    risk_level_filter: Optional[str] = Query(None, alias="risk_level"),
    search: Optional[str] = Query(None, description="Search by transaction ID, device ID, or location"),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List transactions with pagination, filtering by status or risk level, and keyword search.
    - Customers can only see their own transactions.
    - Analysts and Admins can see all transactions.
    """
    query = db.query(Transaction)

    # Customer role restriction
    if current_user.role == UserRole.CUSTOMER.value:
        cust = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not cust:
            return []
        query = query.filter(Transaction.customer_id == cust.id)
    elif customer_id:
        query = query.filter(Transaction.customer_id == customer_id)

    # Filters
    if status_filter:
        query = query.filter(Transaction.status == status_filter.upper())
        
    if risk_level_filter:
        query = query.join(RiskScore).filter(RiskScore.risk_level == risk_level_filter.upper())

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Transaction.id.like(search_pattern)) |
            (Transaction.location.like(search_pattern)) |
            (Transaction.device_id.like(search_pattern))
        )

    transactions = query.order_by(desc(Transaction.transaction_time)).offset(skip).limit(limit).all()
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_detail(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve single transaction details.
    """
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    if current_user.role == UserRole.CUSTOMER.value:
        cust = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not cust or tx.customer_id != cust.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this transaction."
            )

    return tx
