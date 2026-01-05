"""
Discovery Profile database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DiscoveryProfile(Base):
    __tablename__ = "discovery_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), unique=True, nullable=False)
    
    # Classification Results
    persona = Column(String(100), nullable=False)
    maturity_stage = Column(String(50), nullable=False)
    
    # Confidence Scores
    persona_confidence = Column(Float, default=0.0)
    maturity_confidence = Column(Float, default=0.0)
    
    # Feature Insights
    key_features = Column(Text)  # JSON string
    persona_characteristics = Column(Text)  # JSON string
    maturity_indicators = Column(Text)  # JSON string
    
    # Model Metadata
    model_version = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    merchant = relationship("Merchant", back_populates="discovery_profile")
    
    def __repr__(self):
        return f"<DiscoveryProfile merchant_id={self.merchant_id}: {self.persona}, {self.maturity_stage}>"
