"""
Strategy database model
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
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    merchant = relationship("Merchant", back_populates="strategies")
    
    def __repr__(self):
        return f"<Strategy {self.strategy_id}: {self.strategy_name}>"
