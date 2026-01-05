"""
Benchmark Score database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BenchmarkScore(Base):
    __tablename__ = "benchmark_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Peer Group
    peer_group_id = Column(Integer, nullable=False)
    peer_group_name = Column(String(100))
    
    # Overall Scores (0-100)
    overall_score = Column(Float, default=0.0)
    aov_score = Column(Float, default=0.0)
    ltv_score = Column(Float, default=0.0)
    repeat_rate_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # Percentile Rankings
    aov_percentile = Column(Float, default=0.0)
    ltv_percentile = Column(Float, default=0.0)
    repeat_rate_percentile = Column(Float, default=0.0)
    
    # Gaps and Opportunities
    gap_analysis = Column(Text)  # JSON string
    improvement_areas = Column(Text)  # JSON string
    
    # Peer Benchmarks
    peer_benchmarks = Column(Text)  # JSON string with p25, p50, p75
    
    # Model Metadata
    model_version = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    merchant = relationship("Merchant", back_populates="benchmark_scores")
    
    def __repr__(self):
        return f"<BenchmarkScore merchant_id={self.merchant_id}: Overall {self.overall_score:.1f}>"
