import argparse
import random
import uuid
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

LOCATIONS = ["New York, USA", "Los Angeles, USA", "Chicago, USA", "London, UK", "Tokyo, Japan", "Paris, France", "Sydney, Australia"]
MERCHANT_CATEGORIES = ["GROCERY", "ELECTRONICS", "RESTAURANT", "GAS", "E-COMMERCE", "CRYPTO", "JEWELRY", "GAMBLING"]

def generate_synthetic_data(num_transactions: int = 10000) -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)

    # 1. Create Synthetic Customer Profiles
    num_customers = max(50, num_transactions // 100)
    customers = []
    for i in range(num_customers):
        customers.append({
            "customer_id": f"cust-{i+1:04d}",
            "normal_location": random.choice(LOCATIONS[:3]), # mostly US cities
            "avg_amount": round(random.uniform(30.0, 300.0), 2)
        })

    # 2. Generate Transactions
    records = []
    start_time = datetime(2026, 1, 1, 0, 0, 0)
    
    for i in range(num_transactions):
        cust = random.choice(customers)
        is_fraud = random.random() < 0.035 # ~3.5% fraud rate

        tx_time = start_time + timedelta(minutes=random.randint(0, 60 * 24 * 60))
        hour = tx_time.hour
        
        if not is_fraud:
            amount = round(np.random.exponential(scale=cust["avg_amount"]), 2)
            amount = max(5.0, min(amount, cust["avg_amount"] * 2.5))
            location = cust["normal_location"]
            category = random.choice(MERCHANT_CATEGORIES[:5]) # low risk categories
            velocity_10m = random.choices([0, 1, 2], weights=[0.8, 0.15, 0.05])[0]
            is_new_device = 0 if random.random() < 0.9 else 1
        else:
            # Fraudulent transaction characteristics
            amount = round(cust["avg_amount"] * random.uniform(3.5, 12.0), 2)
            location = random.choice([loc for loc in LOCATIONS if loc != cust["normal_location"]])
            category = random.choice(MERCHANT_CATEGORIES[3:]) # higher risk categories
            velocity_10m = random.randint(3, 8) # velocity spike
            is_new_device = 1 if random.random() < 0.85 else 0

        amount_ratio = round(amount / cust["avg_amount"], 2)
        location_distance_km = 0.0 if location == cust["normal_location"] else float(random.randint(500, 10000))
        merchant_risk_index = 0.8 if category in ["CRYPTO", "JEWELRY", "GAMBLING"] else (0.4 if category == "E-COMMERCE" else 0.1)

        records.append({
            "transaction_id": f"tx-gen-{i+1:06d}",
            "customer_id": cust["customer_id"],
            "amount": amount,
            "customer_avg_amount": cust["avg_amount"],
            "amount_ratio": amount_ratio,
            "velocity_10m": velocity_10m,
            "location_distance_km": location_distance_km,
            "hour": hour,
            "merchant_risk_index": merchant_risk_index,
            "is_new_device": is_new_device,
            "is_fraud": int(is_fraud)
        })

    df = pd.DataFrame(records)
    return df

def main():
    parser = argparse.ArgumentParser(description="FinGuard Synthetic Transaction Data Generator")
    parser.add_argument("--transactions", type=int, default=10000, help="Number of synthetic transactions to generate")
    parser.add_argument("--output", type=str, default="ml/data/synthetic_transactions.csv", help="Output CSV path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"Generating {args.transactions} synthetic banking transactions...")
    df = generate_synthetic_data(args.transactions)
    df.to_csv(args.output, index=False)
    
    fraud_count = df["is_fraud"].sum()
    print(f"Dataset generated successfully -> '{args.output}'")
    print(f"Total Rows: {len(df)} | Fraud Rows: {fraud_count} ({fraud_count/len(df)*100:.2f}%)")

if __name__ == "__main__":
    main()
