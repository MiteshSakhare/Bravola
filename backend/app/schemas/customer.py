"""
Customer schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    accepts_marketing: bool = False


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    accepts_marketing: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    customer_id: str
    merchant_id: int
    total_spent: float
    order_count: int
    average_order_value: float
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_order_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
