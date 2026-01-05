"""
Customer database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Customer Information
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    
    # ✅ FIX: Added missing columns for CSV import
    country = Column(String(10), default="US")
    city = Column(String(100))
    zip_code = Column(String(20))
    
    # Metrics
    total_spent = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    average_order_value = Column(Float, default=0.0)
    
    # Marketing
    accepts_marketing = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Shopify Integration
    shopify_customer_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_order_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    merchant = relationship("Merchant", back_populates="customers")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.customer_id}: {self.email}>"