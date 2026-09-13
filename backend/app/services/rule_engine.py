from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
from collections import deque
from sqlalchemy.orm import Session

from app.models.domain import Transaction, Customer, Merchant

@dataclass
class RuleConfig:
    amount_ratio_high: float = 4.0
    amount_weight_high: float = 35.0
    amount_ratio_medium: float = 2.5
    amount_weight_medium: float = 20.0

    velocity_window_minutes: int = 10
    velocity_count_high: int = 4
    velocity_weight_high: float = 30.0
    velocity_count_medium: int = 2
    velocity_weight_medium: float = 15.0

    location_weight: float = 25.0
    
    unusual_hour_start: int = 0
    unusual_hour_end: int = 5
    unusual_hour_weight: float = 15.0

    high_risk_categories: List[str] = field(default_factory=lambda: ["CRYPTO", "JEWELRY", "GAMBLING"])
    high_risk_category_weight: float = 20.0


class SlidingWindowVelocityEngine:
    """
    DSA Implementation: Amortized O(1) Sliding Window Queue for transaction velocity tracking.
    """
    def __init__(self, window_minutes: int = 10):
        self.window_delta = timedelta(minutes=window_minutes)

    def count_velocity(self, timestamps: List[datetime], current_time: datetime) -> int:
        """
        Pushes current timestamp and pops all elements older than (current_time - window_delta).
        """
        cutoff = current_time - self.window_delta
        queue = deque(sorted(timestamps))
        
        # Pop expired items from head of deque
        while queue and queue[0] < cutoff:
            queue.popleft()
            
        return len(queue)


class RuleEngine:
    def __init__(self, config: RuleConfig = None):
        self.config = config or RuleConfig()
        self.velocity_engine = SlidingWindowVelocityEngine(self.config.velocity_window_minutes)

    def evaluate(
        self,
        db: Session,
        customer: Customer,
        merchant: Merchant,
        amount: float,
        location: str,
        device_id: str,
        tx_time: datetime
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        rule_score = 0.0
        reasons = []
        rule_details = {}

        # 1. Amount Deviation Rule
        avg_amt = max(customer.average_transaction_amount or 100.0, 1.0)
        ratio = amount / avg_amt
        rule_details["amount_ratio"] = round(ratio, 2)

        if ratio >= self.config.amount_ratio_high:
            rule_score += self.config.amount_weight_high
            reasons.append(f"Transaction amount (${amount:.2f}) is {ratio:.1f}x customer normal average (${avg_amt:.2f})")
        elif ratio >= self.config.amount_ratio_medium:
            rule_score += self.config.amount_weight_medium
            reasons.append(f"Transaction amount (${amount:.2f}) is elevated ({ratio:.1f}x customer average)")

        # 2. Velocity Rule (Sliding Window DSA)
        window_start = tx_time - timedelta(minutes=self.config.velocity_window_minutes)
        recent_timestamps = [
            t[0] for t in db.query(Transaction.transaction_time)
            .filter(Transaction.customer_id == customer.id)
            .filter(Transaction.transaction_time >= window_start)
            .all()
        ]
        velocity_count = self.velocity_engine.count_velocity(recent_timestamps, tx_time)
        rule_details["velocity_count_10m"] = velocity_count

        if velocity_count >= self.config.velocity_count_high:
            rule_score += self.config.velocity_weight_high
            reasons.append(f"High velocity spike: {velocity_count} transactions within last {self.config.velocity_window_minutes} minutes")
        elif velocity_count >= self.config.velocity_count_medium:
            rule_score += self.config.velocity_weight_medium
            reasons.append(f"Elevated velocity: {velocity_count} transactions within last {self.config.velocity_window_minutes} minutes")

        # 3. Location Anomaly Rule
        norm_loc = customer.normal_location.strip().lower() if customer.normal_location else ""
        curr_loc = location.strip().lower()
        rule_details["location_mismatch"] = (norm_loc != curr_loc)

        if norm_loc and curr_loc and norm_loc != curr_loc:
            rule_score += self.config.location_weight
            reasons.append(f"Unusual location '{location}' (Customer primary: '{customer.normal_location}')")

        # 4. Time Anomaly Rule
        hour = tx_time.hour
        rule_details["tx_hour"] = hour
        if self.config.unusual_hour_start <= hour <= self.config.unusual_hour_end:
            rule_score += self.config.unusual_hour_weight
            reasons.append(f"Transaction initiated during high-risk hours ({hour:02d}:00)")

        # 5. Merchant Category Risk Rule
        rule_details["merchant_category"] = merchant.category
        if merchant.category.upper() in [cat.upper() for cat in self.config.high_risk_categories]:
            rule_score += self.config.high_risk_category_weight
            reasons.append(f"High-risk merchant category: {merchant.category}")

        final_rule_score = min(100.0, rule_score)
        rule_details["total_rule_score"] = final_rule_score

        return final_rule_score, reasons, rule_details


# Singleton default RuleEngine instance
default_rule_engine = RuleEngine()
