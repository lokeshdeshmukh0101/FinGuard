import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.domain import Base, User, Customer, Merchant, Transaction, UserRole, TransactionStatus

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_user_and_customer(db_session):
    user = User(
        email="test_cust@example.com",
        name="Test Customer",
        password_hash="hashed_pw_123",
        role=UserRole.CUSTOMER.value
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    customer = Customer(
        user_id=user.id,
        account_number="ACCT-9988",
        normal_location="New York, USA",
        average_transaction_amount=250.0
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    assert customer.user.email == "test_cust@example.com"
    assert user.customer_profile.account_number == "ACCT-9988"

def test_create_transaction_relationship(db_session):
    user = User(email="cust2@example.com", name="Cust 2", password_hash="pw", role=UserRole.CUSTOMER.value)
    db_session.add(user)
    db_session.commit()

    customer = Customer(user_id=user.id, account_number="ACCT-1122", normal_location="Chicago, USA", average_transaction_amount=150.0)
    merchant = Merchant(name="SuperStore", category="GROCERY", location="Chicago, USA")
    db_session.add_all([customer, merchant])
    db_session.commit()

    tx = Transaction(
        customer_id=customer.id,
        merchant_id=merchant.id,
        amount=45.50,
        location="Chicago, USA",
        device_id="DEV-99",
        status=TransactionStatus.APPROVED.value
    )
    db_session.add(tx)
    db_session.commit()
    db_session.refresh(tx)

    assert tx.customer.account_number == "ACCT-1122"
    assert tx.merchant.name == "SuperStore"
    assert tx.amount == 45.50
