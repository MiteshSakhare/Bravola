"""
Strategy database model with Rules Engine support
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String(50), unique=True, index=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Strategy Information
    strategy_name = Column(String(255), nullable=False)
    strategy_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Scoring
    priority_score = Column(Float, default=0.0)
    expected_roi = Column(Float, default=0.0)
    estimated_revenue = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    
    # Implementation Details
    action_steps = Column(Text)  # JSON string
    required_resources = Column(Text)  # JSON string
    estimated_effort = Column(String(50))  # low, medium, high
    timeline = Column(String(100))
    
    # Status
    status = Column(String(50), default="recommended")  # recommended, active, completed, dismissed
    is_eligible = Column(Boolean, default=True)
    
    # Execution Tracking
    implemented_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    actual_roi = Column(Float, nullable=True)
    actual_revenue = Column(Float, nullable=True)
    
    # --- NEW: Klaviyo Sync Status ---
    klaviyo_campaign_id = Column(String(100), nullable=True)
    sync_status = Column(String(50), default="pending") # pending, synced, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    merchant = relationship("Merchant", back_populates="strategies")
    # Note: Feedback events relation is defined in FeedbackEvent model usually, 
    # but you can add back_populates here if FeedbackEvent has it defined.
    # feedback_events = relationship("FeedbackEvent", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy {self.strategy_id}: {self.strategy_name}>"


class StrategyRule(Base):
    """
    Orchestrator Rules Table.
    Allows dynamic logic injection without code changes.
    Example: If 'average_order_value' 'lt' '50' then boost 'Upsell Strategy'
    """
    __tablename__ = "strategy_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    
    # Logic Definition
    # Condition: e.g., "aov", "open_rate", "persona", "maturity"
    condition_metric = Column(String(50), nullable=False) 
    
    # Operator: "gt" (>), "lt" (<), "eq" (==), "contains"
    operator = Column(String(20), nullable=False)
    
    # Threshold: The value to compare against (e.g., 50.0, "Brand Builder")
    threshold_value = Column(String(100), nullable=False)
    
    # Consequence
    # What happens? "boost_score", "filter_out", "recommend_strategy"
    action_type = Column(String(50), nullable=False)
    
    # The target: e.g., "Win-Back", "All", "Welcome Series"
    target_strategy_type = Column(String(100), nullable=False)
    
    # The impact: e.g., 1.5 (multiplier), -1 (exclude)
    impact_factor = Column(Float, default=1.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<StrategyRule {self.rule_name}>"