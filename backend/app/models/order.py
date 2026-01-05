"""
Order database model
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    order_number = Column(Integer, nullable=False)
    
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Order Details
    total_price = Column(Float, nullable=False)
    subtotal_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    final_price = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    
    # Line Items
    line_items_count = Column(Integer, default=0)
    line_items = Column(Text)  # JSON string
    
    # Status
    financial_status = Column(String(50), default="pending")
    fulfillment_status = Column(String(50), default="unfulfilled")
    
    # Tags and Notes
    tags = Column(String(500))
    notes = Column(Text)
    
    # Shopify Integration
    shopify_order_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    merchant = relationship("Merchant", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    
    def __repr__(self):
        return f"<Order {self.order_id}: ${self.final_price}>"