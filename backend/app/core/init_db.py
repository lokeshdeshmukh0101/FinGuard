from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.domain import Base, User, Customer, Merchant, UserRole

def init_db(db: Session) -> None:
    """
    Seed initial roles, demo users (Customer, Analyst, Admin), and default merchants.
    """
    # Demo Users Definition
    users_to_seed = [
        {
            "email": "customer@example.com",
            "name": "Jane Doe (Demo Customer)",
            "password": "Password123!",
            "role": UserRole.CUSTOMER.value,
            "account_number": "ACCT-10001",
            "normal_location": "New York, NY",
            "average_transaction_amount": 150.0
        },
        {
            "email": "analyst@example.com",
            "name": "Alex Smith (Fraud Analyst)",
            "password": "Password123!",
            "role": UserRole.ANALYST.value,
        },
        {
            "email": "admin@example.com",
            "name": "System Admin",
            "password": "Password123!",
            "role": UserRole.ADMIN.value,
        }
    ]

    for item in users_to_seed:
        user = db.query(User).filter(User.email == item["email"]).first()
        if not user:
            user = User(
                email=item["email"],
                name=item["name"],
                password_hash=get_password_hash(item["password"]),
                role=item["role"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            if item["role"] == UserRole.CUSTOMER.value:
                customer = db.query(Customer).filter(Customer.user_id == user.id).first()
                if not customer:
                    customer = Customer(
                        user_id=user.id,
                        account_number=item["account_number"],
                        normal_location=item["normal_location"],
                        average_transaction_amount=item["average_transaction_amount"]
                    )
                    db.add(customer)
                    db.commit()

    # Seed Default Merchants
    merchants_to_seed = [
        {"name": "Amazon Online", "category": "E-COMMERCE", "location": "Online"},
        {"name": "SuperMart Groceries", "category": "GROCERY", "location": "New York, NY"},
        {"name": "Luxury Watches Boutique", "category": "JEWELRY", "location": "Miami, FL"},
        {"name": "Global Crypto Exchange", "category": "CRYPTO", "location": "London, UK"},
        {"name": "Metropolis Gas Station", "category": "GAS", "location": "New York, NY"},
    ]

    for m in merchants_to_seed:
        merchant = db.query(Merchant).filter(Merchant.name == m["name"]).first()
        if not merchant:
            merchant = Merchant(name=m["name"], category=m["category"], location=m["location"])
            db.add(merchant)

    db.commit()
