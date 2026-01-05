"""
Merchant schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

class MerchantIntegrationUpdate(BaseModel):
    shopify_access_token: Optional[str] = None
    shopify_shop_domain: Optional[str] = None
    klaviyo_api_key: Optional[str] = None

class MerchantBase(BaseModel):
    shop_name: str = Field(..., min_length=1, max_length=255)
    shop_domain: str = Field(..., min_length=1, max_length=255)
    vertical: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = "US"
    currency: Optional[str] = "USD"

class MerchantCreate(MerchantBase):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class MerchantUpdate(BaseModel):
    shop_name: Optional[str] = None
    vertical: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    shopify_connected: Optional[bool] = None
    klaviyo_connected: Optional[bool] = None

class MerchantResponse(MerchantBase):
    id: int
    merchant_id: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    
    # Metrics - Defaults to 0 if None
    monthly_revenue: float = 0.0
    total_customers: int = 0
    total_orders: int = 0
    aov: float = 0.0
    repeat_purchase_rate: float = 0.0
    ltv: float = 0.0
    customer_acquisition_cost: float = 0.0
    email_subscriber_count: int = 0
    
    # Integration Status - Defaults to False if None
    shopify_connected: bool = False
    klaviyo_connected: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    
    # ✅ FIX: Automatically convert None to False for booleans
    @field_validator('shopify_connected', 'klaviyo_connected', 'is_active', 'is_verified', mode='before')
    @classmethod
    def set_bool_defaults(cls, v):
        return v or False

    # ✅ FIX: Automatically convert None to 0 for numbers
    @field_validator('monthly_revenue', 'total_customers', 'total_orders', 'aov', 'repeat_purchase_rate', 'ltv', 'customer_acquisition_cost', 'email_subscriber_count', mode='before')
    @classmethod
    def set_numeric_defaults(cls, v):
        return v or 0

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str