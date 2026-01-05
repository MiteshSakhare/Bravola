"""
Merchant database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Shop Information
    shop_name = Column(String(255), nullable=False)
    shop_domain = Column(String(255), unique=True, nullable=False)
    vertical = Column(String(100), nullable=False)
    country = Column(String(10), default="US")
    currency = Column(String(10), default="USD")
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Business Metrics (Crucial for AI)
    monthly_revenue = Column(Float, default=0.0)
    total_customers = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    aov = Column(Float, default=0.0)
    repeat_purchase_rate = Column(Float, default=0.0)
    ltv = Column(Float, default=0.0)
    customer_acquisition_cost = Column(Float, default=0.0)
    email_subscriber_count = Column(Integer, default=0)
    
    # AI Metadata
    maturity_stage = Column(String(50), default="Startup")
    persona = Column(String(100), nullable=True)
    
    # Integration Status
    shopify_connected = Column(Boolean, default=False)
    shopify_shop_id = Column(String(100), nullable=True)
    shopify_access_token = Column(String(255), nullable=True)
    klaviyo_connected = Column(Boolean, default=False)
    klaviyo_api_key = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # ✅ FIX: Explicit Relationships
    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="merchant", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="merchant", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="merchant", cascade="all, delete-orphan")
    discovery_profile = relationship("DiscoveryProfile", back_populates="merchant", uselist=False)
    benchmark_scores = relationship("BenchmarkScore", back_populates="merchant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Merchant {self.merchant_id}: {self.shop_name}>"