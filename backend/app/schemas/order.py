"""
Order schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    total_price: float = Field(..., ge=0)
    subtotal_price: float = Field(..., ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    final_price: float = Field(..., ge=0)
    line_items_count: int = Field(default=1, ge=1)
    line_items: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    customer_id: str


class OrderUpdate(BaseModel):
    financial_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    order_id: str
    order_number: int
    merchant_id: int
    customer_id: int
    financial_status: str
    fulfillment_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
