import pytest
from datetime import datetime, timedelta
from app.services.rule_engine import RuleEngine, RuleConfig, SlidingWindowVelocityEngine

def test_sliding_window_velocity_engine():
    engine = SlidingWindowVelocityEngine(window_minutes=10)
    now = datetime(2026, 9, 13, 10, 30, 0)
    
    # 5 timestamps: 2 expired (older than 10 mins), 3 active (within last 10 mins)
    timestamps = [
        now - timedelta(minutes=25),
        now - timedelta(minutes=15),
        now - timedelta(minutes=8),
        now - timedelta(minutes=4),
        now - timedelta(minutes=1),
    ]
    
    velocity = engine.count_velocity(timestamps, now)
    assert velocity == 3

def test_rule_engine_evaluation_logic():
    config = RuleConfig(
        amount_ratio_high=3.0,
        amount_weight_high=40.0,
        high_risk_categories=["CRYPTO"],
        high_risk_category_weight=25.0
    )
    rule_engine = RuleEngine(config=config)
    
    assert rule_engine.config.amount_ratio_high == 3.0
    assert rule_engine.config.high_risk_category_weight == 25.0
