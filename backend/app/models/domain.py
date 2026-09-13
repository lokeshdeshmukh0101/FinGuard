import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FLAGGED = "FLAGGED"
    REJECTED = "REJECTED"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"

class InvestigationDecision(str, enum.Enum):
    LEGITIMATE = "LEGITIMATE"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    UNDER_REVIEW = "UNDER_REVIEW"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.CUSTOMER.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer_profile = relationship("Customer", back_populates="user", uselist=False)
    investigations = relationship("Investigation", back_populates="analyst")
    audit_logs = relationship("AuditLog", back_populates="user")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    account_number = Column(String(64), unique=True, nullable=False, index=True)
    normal_location = Column(String(255), nullable=False)
    average_transaction_amount = Column(Float, nullable=False, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="customer_profile")
    transactions = relationship("Transaction", back_populates="customer")


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="merchant")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False, index=True)
    transaction_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    location = Column(String(255), nullable=False)
    device_id = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default=TransactionStatus.PENDING.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    risk_score = relationship("RiskScore", back_populates="transaction", uselist=False)
    alerts = relationship("FraudAlert", back_populates="transaction")
    investigations = relationship("Investigation", back_populates="transaction")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False, unique=True, index=True)
    score = Column(Integer, nullable=False, index=True)
    risk_level = Column(String(50), nullable=False, index=True)
    model_score = Column(Float, nullable=False)
    rule_score = Column(Float, nullable=False)
    breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="risk_score")


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default=AlertStatus.NEW.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False, index=True)
    analyst_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    decision = Column(String(50), nullable=False, default=InvestigationDecision.UNDER_REVIEW.value, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="investigations")
    analyst = relationship("User", back_populates="investigations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
