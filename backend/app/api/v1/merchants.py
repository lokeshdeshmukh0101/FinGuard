from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import Merchant, User, UserRole
from app.schemas.domain import MerchantCreate, MerchantResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/merchants", tags=["Merchants"])

@router.get("", response_model=List[MerchantResponse])
def list_merchants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all available merchants.
    """
    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return merchants

@router.post("", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
def create_merchant(
    merchant_in: MerchantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """
    Create a new merchant (Admin only).
    """
    merchant = Merchant(
        name=merchant_in.name,
        category=merchant_in.category.upper(),
        location=merchant_in.location
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant
