"""
Campaign database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(50), unique=True, index=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Campaign Information
    campaign_name = Column(String(255), nullable=False)
    campaign_type = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Targeting
    segment = Column(String(100))
    recipients = Column(Integer, default=0)
    
    # Performance Metrics
    opens = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="draft")
    
    # Klaviyo Integration
    klaviyo_campaign_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    merchant = relationship("Merchant", back_populates="campaigns")
    
    def __repr__(self):
        return f"<Campaign {self.campaign_id}: {self.campaign_name}>"