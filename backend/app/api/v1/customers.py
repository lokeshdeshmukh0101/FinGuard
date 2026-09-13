from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import Customer, User, UserRole, Transaction
from app.schemas.domain import CustomerResponse, TransactionResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=List[CustomerResponse])
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    List all customer profiles (Analyst and Admin access only).
    """
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/me", response_model=CustomerResponse)
def get_my_customer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer profile for the currently authenticated user.
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No customer profile found for this user."
        )
    return customer

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer profile by ID.
    Customers can only view their own profile unless they are an Analyst or Admin.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
    
    if current_user.role == UserRole.CUSTOMER.value and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view another customer's profile."
        )
        
    return customer

@router.get("/{customer_id}/transactions", response_model=List[TransactionResponse])
def get_customer_transactions(
    customer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get transaction history for a specific customer.
    Customers can only view their own transaction history unless they are an Analyst/Admin.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
        
    if current_user.role == UserRole.CUSTOMER.value and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this transaction history."
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(Transaction.transaction_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions
