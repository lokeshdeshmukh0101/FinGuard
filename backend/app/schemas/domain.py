from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.models.domain import UserRole, TransactionStatus, RiskLevel, AlertStatus, InvestigationDecision


# --- USER & AUTH SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# --- CUSTOMER SCHEMAS ---
class CustomerCreate(BaseModel):
    user_id: str
    account_number: str
    normal_location: str
    average_transaction_amount: float = 100.0

class CustomerResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    normal_location: str
    average_transaction_amount: float
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- MERCHANT SCHEMAS ---
class MerchantCreate(BaseModel):
    name: str
    category: str
    location: str

class MerchantResponse(BaseModel):
    id: str
    name: str
    category: str
    location: str

    model_config = ConfigDict(from_attributes=True)


# --- TRANSACTION SCHEMAS ---
class TransactionCreate(BaseModel):
    customer_id: str
    merchant_id: str
    amount: float = Field(..., gt=0)
    location: str
    device_id: str
    transaction_time: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: str
    customer_id: str
    merchant_id: str
    amount: float
    transaction_time: datetime
    location: str
    device_id: str
    status: TransactionStatus
    created_at: datetime
    customer: Optional[CustomerResponse] = None
    merchant: Optional[MerchantResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- RISK SCORE & EVALUATION SCHEMAS ---
class RiskScoreResponse(BaseModel):
    id: str
    transaction_id: str
    score: int
    risk_level: RiskLevel
    model_score: float
    rule_score: float
    breakdown: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionEvaluationResponse(BaseModel):
    transaction_id: str
    risk_score: int
    risk_level: RiskLevel
    status: TransactionStatus
    reasons: List[str]
    model_score: float
    rule_score: float


# --- FRAUD ALERT SCHEMAS ---
class FraudAlertResponse(BaseModel):
    id: str
    transaction_id: str
    severity: RiskLevel
    reason: str
    status: AlertStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    transaction: Optional[TransactionResponse] = None

    model_config = ConfigDict(from_attributes=True)

class FraudAlertUpdate(BaseModel):
    status: AlertStatus


# --- INVESTIGATION SCHEMAS ---
class InvestigationCreate(BaseModel):
    transaction_id: str
    decision: InvestigationDecision
    notes: Optional[str] = None

class InvestigationResponse(BaseModel):
    id: str
    transaction_id: str
    analyst_id: str
    decision: InvestigationDecision
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    analyst: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- AUDIT LOG SCHEMAS ---
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    metadata_json: Optional[Dict[str, Any]] = None
    timestamp: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
