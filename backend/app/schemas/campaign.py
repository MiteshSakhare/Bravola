"""
Campaign schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    campaign_name: str = Field(..., min_length=1, max_length=255)
    campaign_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    segment: Optional[str] = None
    recipients: int = Field(default=0, ge=0)


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    campaign_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    opens: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    revenue: Optional[float] = None


class CampaignResponse(CampaignBase):
    id: int
    campaign_id: str
    merchant_id: int
    
    # Performance metrics
    opens: int
    clicks: int
    conversions: int
    revenue: float
    open_rate: float
    click_rate: float
    conversion_rate: float
    roi: float
    
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
