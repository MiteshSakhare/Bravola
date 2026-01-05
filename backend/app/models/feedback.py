"""
Feedback Event database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Event Type
    event_type = Column(String(100), nullable=False)  # strategy_accepted, campaign_completed, etc.
    event_category = Column(String(50))  # positive, negative, neutral
    
    # Performance Data
    actual_value = Column(Float, nullable=True)
    predicted_value = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    
    # Context
    context_data = Column(Text)  # JSON string with additional context
    
    # Learning Status
    is_processed = Column(Boolean, default=False)
    model_updated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FeedbackEvent {self.event_id}: {self.event_type}>"
