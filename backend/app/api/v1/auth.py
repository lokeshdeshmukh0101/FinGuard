from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import uuid

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.domain import User, Customer, UserRole
from app.schemas.domain import UserCreate, UserResponse, Token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password, returning JWT access token.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.email, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user and automatically create a customer profile if role is CUSTOMER.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=hashed_password,
        role=user_in.role.value
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Auto-create Customer profile if user role is CUSTOMER
    if str(new_user.role).upper() == UserRole.CUSTOMER.value:
        acct_num = f"ACCT-{uuid.uuid4().hex[:8].upper()}"
        customer = Customer(
            user_id=new_user.id,
            account_number=acct_num,
            normal_location="New York, USA",
            average_transaction_amount=250.0
        )
        db.add(customer)
        db.commit()

    return new_user

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get profile information of currently logged in user.
    """
    return current_user
